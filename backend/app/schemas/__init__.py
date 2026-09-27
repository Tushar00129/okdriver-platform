from app.schemas.alerts import AlertResponse, AlertStatusUpdate
from app.schemas.auth import TokenResponse, UserResponse
from app.schemas.cameras import (
    CameraCreate,
    CameraResponse,
    CameraUpdate,
    HeartbeatRequest,
    OnboardingRequest,
)
from app.schemas.events import DetectionCreate, DetectionResponse
from app.schemas.watchlist import WatchlistCreate, WatchlistResponse, WatchlistUpdate

__all__ = [
    "AlertResponse",
    "AlertStatusUpdate",
    "CameraCreate",
    "CameraResponse",
    "CameraUpdate",
    "DetectionCreate",
    "DetectionResponse",
    "HeartbeatRequest",
    "OnboardingRequest",
    "TokenResponse",
    "UserResponse",
    "WatchlistCreate",
    "WatchlistResponse",
    "WatchlistUpdate",
]
