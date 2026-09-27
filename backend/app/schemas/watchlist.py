from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import EntityType


class WatchlistCreate(BaseModel):
    entity_type: EntityType
    identifier: str = Field(min_length=1, max_length=120)
    reason: str = Field(min_length=1, max_length=2000)
    status: str = Field(default="active", min_length=1, max_length=40)


class WatchlistUpdate(BaseModel):
    reason: str | None = Field(default=None, min_length=1, max_length=2000)
    status: str | None = Field(default=None, min_length=1, max_length=40)


class WatchlistResponse(WatchlistCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    added_by: int | None
    created_at: datetime | None
