import asyncio
import os

from sqlalchemy import select

from app.core.security import hash_password
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.models import Camera, CameraStatus, EntityType, User, UserRole, Watchlist
from simulator.adapter import SIMULATED_SOURCES


def required_password(name: str) -> str:
    value = os.getenv(name, "")
    if len(value) < 12:
        raise RuntimeError(f"{name} must be set and contain at least 12 characters")
    return value


async def get_or_create_user(session, username: str, password: str, role: UserRole) -> User:
    user = await session.scalar(select(User).where(User.username == username))
    if user is None:
        user = User(username=username, password_hash=hash_password(password), role=role)
        session.add(user)
        await session.flush()
    return user


async def seed() -> None:
    admin_username = os.getenv("SEED_ADMIN_USERNAME", "admin")
    operator_username = os.getenv("SEED_OPERATOR_USERNAME", "operator")
    admin_password = required_password("SEED_ADMIN_PASSWORD")
    operator_password = required_password("SEED_OPERATOR_PASSWORD")

    if get_settings().database_url.startswith("sqlite"):
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        admin = await get_or_create_user(session, admin_username, admin_password, UserRole.ADMIN)
        operator = await get_or_create_user(session, operator_username, operator_password, UserRole.OPERATOR)

        for source in SIMULATED_SOURCES:
            camera = await session.scalar(select(Camera).where(Camera.name == source.name))
            if camera is None:
                session.add(
                    Camera(
                        name=source.name,
                        department=source.department,
                        lat=source.lat,
                        lng=source.lng,
                        camera_type=source.camera_type,
                        source_protocol="simulator",
                        stream_endpoint=source.stream_endpoint,
                        status=CameraStatus.ONLINE,
                        zone=source.zone,
                        storage_metadata={"adapter": "simulated", "source_key": source.key},
                    )
                )

        identifier = os.getenv("SEED_WATCHLIST_IDENTIFIER", "KA01AB1234")
        watchlist = await session.scalar(
            select(Watchlist).where(
                Watchlist.entity_type == EntityType.VEHICLE,
                Watchlist.identifier == identifier,
            )
        )
        if watchlist is None:
            session.add(
                Watchlist(
                    entity_type=EntityType.VEHICLE,
                    identifier=identifier,
                    reason="Representative simulator watchlist target",
                    status="active",
                    added_by=admin.id,
                )
            )
        await session.commit()
        print(f"Seeded users: {admin.username} (admin), {operator.username} (operator)")
        print(f"Seeded cameras: {len(SIMULATED_SOURCES)}")
        print(f"Seeded watchlist target: {identifier}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
