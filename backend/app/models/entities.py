from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CameraStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"


class AlertStatus(StrEnum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class EntityType(StrEnum):
    VEHICLE = "vehicle"
    PERSON = "person"


class UserRole(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    department: Mapped[str] = mapped_column(String(120), nullable=False)
    lat: Mapped[float] = mapped_column(nullable=False)
    lng: Mapped[float] = mapped_column(nullable=False)
    camera_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_protocol: Mapped[str] = mapped_column(String(40), nullable=False)
    stream_endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[CameraStatus] = mapped_column(
        Enum(CameraStatus, name="camera_status"), default=CameraStatus.OFFLINE, nullable=False
    )
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    zone: Mapped[str] = mapped_column(String(120), nullable=False)
    storage_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    detections: Mapped[list["DetectionEvent"]] = relationship(back_populates="camera")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="camera")
    audit_logs: Mapped[list["CameraAuditLog"]] = relationship(back_populates="camera")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.OPERATOR, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    audit_logs: Mapped[list["CameraAuditLog"]] = relationship(back_populates="actor")
    resolved_alerts: Mapped[list["Alert"]] = relationship(back_populates="resolver")


class Watchlist(Base):
    __tablename__ = "watchlist"
    __table_args__ = (UniqueConstraint("entity_type", "identifier", name="uq_watchlist_entity_identifier"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[EntityType] = mapped_column(
        Enum(EntityType, name="entity_type"), nullable=False
    )
    identifier: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="active", nullable=False)
    added_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    alerts: Mapped[list["Alert"]] = relationship(back_populates="watchlist")


class DetectionEvent(Base):
    __tablename__ = "detection_events"
    __table_args__ = (
        Index("ix_detection_camera_timestamp", "camera_id", "timestamp"),
        Index("ix_detection_vehicle_number", "vehicle_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    camera_id: Mapped[int] = mapped_column(ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    vehicle_number: Mapped[str | None] = mapped_column(String(40), index=True)
    vehicle_type: Mapped[str | None] = mapped_column(String(80))
    confidence: Mapped[float] = mapped_column(nullable=False)
    bounding_box: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    camera: Mapped[Camera] = relationship(back_populates="detections")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="event")


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (Index("ix_alert_status_timestamp", "status", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("detection_events.id", ondelete="CASCADE"), nullable=False)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlist.id", ondelete="CASCADE"), nullable=False)
    camera_id: Mapped[int] = mapped_column(ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    matched_identifier: Mapped[str] = mapped_column(String(120), nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status"), default=AlertStatus.NEW, nullable=False
    )
    resolved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    event: Mapped[DetectionEvent] = relationship(back_populates="alerts")
    watchlist: Mapped[Watchlist] = relationship(back_populates="alerts")
    camera: Mapped[Camera] = relationship(back_populates="alerts")
    resolver: Mapped[User | None] = relationship(back_populates="resolved_alerts")


class CameraAuditLog(Base):
    __tablename__ = "camera_audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    camera_id: Mapped[int] = mapped_column(ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    changed_fields: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    camera: Mapped[Camera] = relationship(back_populates="audit_logs")
    actor: Mapped[User | None] = relationship(back_populates="audit_logs")
