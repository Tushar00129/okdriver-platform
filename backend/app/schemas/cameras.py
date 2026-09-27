from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models import CameraStatus


class CameraBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    department: str = Field(min_length=1, max_length=120)
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    camera_type: str = Field(min_length=1, max_length=80)
    source_protocol: str = Field(min_length=1, max_length=40)
    stream_endpoint: str = Field(min_length=1, max_length=2000)
    zone: str = Field(min_length=1, max_length=120)
    storage_metadata: dict[str, Any] = Field(default_factory=dict)


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    department: str | None = Field(default=None, min_length=1, max_length=120)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    camera_type: str | None = Field(default=None, min_length=1, max_length=80)
    source_protocol: str | None = Field(default=None, min_length=1, max_length=40)
    stream_endpoint: str | None = Field(default=None, min_length=1, max_length=2000)
    zone: str | None = Field(default=None, min_length=1, max_length=120)
    storage_metadata: dict[str, Any] | None = None
    status: CameraStatus | None = None


class CameraResponse(CameraBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: CameraStatus
    last_heartbeat: datetime | None
    created_at: datetime | None
    updated_at: datetime | None


class HeartbeatRequest(BaseModel):
    status: CameraStatus = CameraStatus.ONLINE


class OnboardingRequest(CameraCreate):
    external_id: str | None = Field(default=None, max_length=120)
