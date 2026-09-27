from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Alert, AlertStatus, User
from app.schemas import AlertResponse, AlertStatusUpdate
from app.services.realtime import publish_event

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(status_filter: AlertStatus | None = Query(default=None, alias="status"), db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)) -> list[Alert]:
    query = select(Alert).order_by(Alert.timestamp.desc())
    if status_filter:
        query = query.where(Alert.status == status_filter)
    return list((await db.scalars(query)).all())


async def update_alert(alert_id: int, next_status: AlertStatus, db: AsyncSession, user: User) -> Alert:
    alert = await db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = next_status
    if next_status == AlertStatus.RESOLVED:
        alert.resolved_by = user.id
        alert.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(alert)
    await publish_event("alert_status_changed", {"id": alert.id, "status": alert.status.value, "resolved_by": alert.resolved_by})
    return alert


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(alert_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> Alert:
    return await update_alert(alert_id, AlertStatus.ACKNOWLEDGED, db, user)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(alert_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> Alert:
    return await update_alert(alert_id, AlertStatus.RESOLVED, db, user)
