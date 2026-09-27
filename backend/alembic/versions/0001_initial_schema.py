"""create initial monitoring schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    camera_status = postgresql.ENUM("online", "offline", "degraded", name="camera_status")
    alert_status = postgresql.ENUM("new", "acknowledged", "resolved", name="alert_status")
    entity_type = postgresql.ENUM("vehicle", "person", name="entity_type")
    user_role = postgresql.ENUM("admin", "operator", name="user_role")
    for enum in (camera_status, alert_status, entity_type, user_role):
        enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "cameras",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("department", sa.String(length=120), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("camera_type", sa.String(length=80), nullable=False),
        sa.Column("source_protocol", sa.String(length=40), nullable=False),
        sa.Column("stream_endpoint", sa.Text(), nullable=False),
        sa.Column("status", camera_status, nullable=False),
        sa.Column("last_heartbeat", sa.DateTime(timezone=True)),
        sa.Column("zone", sa.String(length=120), nullable=False),
        sa.Column("storage_metadata", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "watchlist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", entity_type, nullable=False),
        sa.Column("identifier", sa.String(length=120), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("added_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("entity_type", "identifier", name="uq_watchlist_entity_identifier"),
    )
    op.create_index("ix_watchlist_identifier", "watchlist", ["identifier"])

    op.create_table(
        "detection_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("camera_id", sa.Integer(), sa.ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("vehicle_number", sa.String(length=40)),
        sa.Column("vehicle_type", sa.String(length=80)),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("bounding_box", postgresql.JSONB(), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_detection_camera_timestamp", "detection_events", ["camera_id", "timestamp"])
    op.create_index("ix_detection_vehicle_number", "detection_events", ["vehicle_number"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("detection_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("watchlist_id", sa.Integer(), sa.ForeignKey("watchlist.id", ondelete="CASCADE"), nullable=False),
        sa.Column("camera_id", sa.Integer(), sa.ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False),
        sa.Column("matched_identifier", sa.String(length=120), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", alert_status, nullable=False),
        sa.Column("resolved_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_alert_status_timestamp", "alerts", ["status", "timestamp"])

    op.create_table(
        "camera_audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("camera_id", sa.Integer(), sa.ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False),
        sa.Column("changed_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("changed_fields", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("camera_audit_log")
    op.drop_index("ix_alert_status_timestamp", table_name="alerts")
    op.drop_table("alerts")
    op.drop_index("ix_detection_vehicle_number", table_name="detection_events")
    op.drop_index("ix_detection_camera_timestamp", table_name="detection_events")
    op.drop_table("detection_events")
    op.drop_index("ix_watchlist_identifier", table_name="watchlist")
    op.drop_table("watchlist")
    op.drop_table("cameras")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
    for enum in ("user_role", "entity_type", "alert_status", "camera_status"):
        sa.Enum(name=enum).drop(op.get_bind(), checkfirst=True)
