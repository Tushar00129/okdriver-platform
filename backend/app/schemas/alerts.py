from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import AlertStatus


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    watchlist_id: int
    camera_id: int
    matched_identifier: str
    confidence: float
    timestamp: datetime
    status: AlertStatus
    resolved_by: int | None
    resolved_at: datetime | None


class AlertStatusUpdate(BaseModel):
    status: AlertStatus
