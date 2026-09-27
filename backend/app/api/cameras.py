from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models import Camera, CameraAuditLog, CameraStatus, User, UserRole
from app.schemas import CameraCreate, CameraResponse, CameraUpdate, HeartbeatRequest, OnboardingRequest
from app.services.realtime import publish_event

router = APIRouter(prefix="/cameras", tags=["cameras"])


async def record_audit(db: AsyncSession, camera_id: int, user_id: int, action: str, fields: dict) -> None:
    db.add(CameraAuditLog(camera_id=camera_id, changed_by=user_id, action=action, changed_fields=fields))


@router.get("", response_model=list[CameraResponse])
async def list_cameras(
    status_filter: CameraStatus | None = Query(default=None, alias="status"),
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Camera]:
    query = select(Camera).order_by(Camera.name)
    if status_filter:
        query = query.where(Camera.status == status_filter)
    if search:
        term = f"%{search}%"
        query = query.where(or_(Camera.name.ilike(term), Camera.department.ilike(term), Camera.zone.ilike(term)))
    return list((await db.scalars(query)).all())


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    payload: CameraCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.OPERATOR)),
) -> Camera:
    camera = Camera(**payload.model_dump())
    db.add(camera)
    await db.flush()
    await record_audit(db, camera.id, user.id, "created", payload.model_dump())
    await db.commit()
    await db.refresh(camera)
    await publish_event("camera_status_changed", {"camera_id": camera.id, "status": camera.status.value})
    return camera


@router.post("/onboard", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def onboard_camera(
    payload: OnboardingRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.OPERATOR)),
) -> Camera:
    camera = Camera(**payload.model_dump(exclude={"external_id"}))
    db.add(camera)
    await db.flush()
    fields = payload.model_dump()
    fields["onboarding_mode"] = "api_simulated"
    await record_audit(db, camera.id, user.id, "onboarded", fields)
    await db.commit()
    await db.refresh(camera)
    return camera


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(camera_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)) -> Camera:
    camera = await db.get(Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.patch("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: int,
    payload: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN, UserRole.OPERATOR)),
) -> Camera:
    camera = await db.get(Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(camera, field, value)
    await record_audit(db, camera.id, user.id, "updated", changes)
    await db.commit()
    await db.refresh(camera)
    if "status" in changes:
        await publish_event("camera_status_changed", {"camera_id": camera.id, "status": camera.status.value})
    return camera


@router.post("/{camera_id}/disable", response_model=CameraResponse)
async def disable_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
) -> Camera:
    camera = await db.get(Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    camera.status = CameraStatus.OFFLINE
    await record_audit(db, camera.id, user.id, "disabled", {"status": CameraStatus.OFFLINE.value})
    await db.commit()
    await db.refresh(camera)
    await publish_event("camera_status_changed", {"camera_id": camera.id, "status": camera.status.value})
    return camera


@router.post("/{camera_id}/heartbeat", response_model=CameraResponse)
async def heartbeat(camera_id: int, payload: HeartbeatRequest, db: AsyncSession = Depends(get_db)) -> Camera:
    camera = await db.get(Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    camera.status = payload.status
    camera.last_heartbeat = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(camera)
    await publish_event("camera_status_changed", {"camera_id": camera.id, "status": camera.status.value})
    return camera


@router.get("/{camera_id}/audit", response_model=list[dict])
async def camera_audit(camera_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)) -> list[dict]:
    camera = await db.get(Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    rows = await db.scalars(select(CameraAuditLog).where(CameraAuditLog.camera_id == camera_id).order_by(CameraAuditLog.created_at.desc()))
    return [
        {"id": row.id, "action": row.action, "changed_by": row.changed_by, "changed_fields": row.changed_fields, "created_at": row.created_at}
        for row in rows
    ]
