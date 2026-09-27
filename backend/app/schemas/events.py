from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DetectionCreate(BaseModel):
    camera_id: int = Field(gt=0)
    timestamp: datetime
    event_type: str = Field(min_length=1, max_length=80)
    vehicle_number: str | None = Field(default=None, max_length=40)
    vehicle_type: str | None = Field(default=None, max_length=80)
    confidence: float = Field(ge=0, le=1)
    bounding_box: dict[str, Any] = Field(default_factory=dict)
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class DetectionResponse(DetectionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None


class AlertEvent(BaseModel):
    alert_id: int
    detection_id: int
    camera_id: int
    identifier: str
    confidence: float
    timestamp: datetime
