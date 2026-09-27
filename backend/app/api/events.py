from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Alert, AlertStatus, Camera, DetectionEvent, EntityType, User, Watchlist
from app.schemas import DetectionCreate, DetectionResponse
from app.services.realtime import publish_event
from app.services.rate_limit import enforce_ingestion_rate_limit

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[DetectionResponse])
async def list_recent_events(
    limit: int = Query(default=30, ge=1, le=100),
    camera_id: int | None = Query(default=None, gt=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[DetectionEvent]:
    query = select(DetectionEvent).order_by(DetectionEvent.timestamp.desc()).limit(limit)
    if camera_id is not None:
        query = query.where(DetectionEvent.camera_id == camera_id)
    return list((await db.scalars(query)).all())


@router.post("/detection", response_model=DetectionResponse, status_code=status.HTTP_201_CREATED)
async def ingest_detection(request: Request, payload: DetectionCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)) -> DetectionEvent:
    await enforce_ingestion_rate_limit(request)
    camera = await db.get(Camera, payload.camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    identifier = payload.vehicle_number
    if identifier:
        duplicate = await db.scalar(
            select(DetectionEvent).where(
                DetectionEvent.camera_id == payload.camera_id,
                DetectionEvent.vehicle_number == identifier,
                DetectionEvent.timestamp.between(payload.timestamp - timedelta(seconds=15), payload.timestamp + timedelta(seconds=15)),
            )
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="Duplicate detection event")

    event = DetectionEvent(**payload.model_dump())
    db.add(event)
    await db.flush()
    await publish_event("detection_event", {"id": event.id, **payload.model_dump(mode="json")})

    if identifier:
        watchlist = await db.scalar(
            select(Watchlist).where(
                Watchlist.entity_type == EntityType.VEHICLE,
                Watchlist.identifier == identifier,
                Watchlist.status == "active",
            )
        )
        if watchlist:
            alert = Alert(
                event_id=event.id,
                watchlist_id=watchlist.id,
                camera_id=event.camera_id,
                matched_identifier=identifier,
                confidence=event.confidence,
                timestamp=event.timestamp,
                status=AlertStatus.NEW,
            )
            db.add(alert)
            await db.flush()
            await publish_event("watchlist_alert", {"id": alert.id, "event_id": event.id, "camera_id": event.camera_id, "identifier": identifier, "confidence": event.confidence, "timestamp": event.timestamp.isoformat()})
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/search/{identifier}", response_model=list[DetectionResponse])
async def search_entity(identifier: str, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)) -> list[DetectionEvent]:
    query = select(DetectionEvent).where(DetectionEvent.vehicle_number.ilike(identifier)).order_by(DetectionEvent.timestamp)
    return list((await db.scalars(query)).all())
