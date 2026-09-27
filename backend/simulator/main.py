import argparse
import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx

from simulator.adapter import DetectionSimulator, SimulatedCameraSource, SIMULATED_SOURCES

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("okdriver-simulator")


@dataclass(frozen=True)
class SimulatorSettings:
    api_url: str = os.getenv("SIMULATOR_API_URL", "http://localhost:8000")
    token: str = os.getenv("SIMULATOR_TOKEN", "")
    username: str = os.getenv("SIMULATOR_USERNAME", "")
    password: str = os.getenv("SIMULATOR_PASSWORD", "")
    heartbeat_seconds: float = float(os.getenv("SIMULATOR_HEARTBEAT_SECONDS", "10"))
    detection_seconds: float = float(os.getenv("SIMULATOR_DETECTION_SECONDS", "5"))
    watchlist_identifiers: tuple[str, ...] = tuple(
        value.strip() for value in os.getenv("SIMULATOR_WATCHLIST_IDENTIFIERS", "KA01AB1234").split(",") if value.strip()
    )
    dry_run: bool = os.getenv("SIMULATOR_DRY_RUN", "false").lower() == "true"
    run_once: bool = os.getenv("SIMULATOR_RUN_ONCE", "false").lower() == "true"


class SimulatorClient:
    def __init__(self, settings: SimulatorSettings) -> None:
        self.settings = settings
        self.client = httpx.AsyncClient(base_url=settings.api_url, timeout=10)
        self.camera_ids: dict[str, int] = {}

    async def close(self) -> None:
        await self.client.aclose()

    async def authenticate(self) -> None:
        if self.settings.token or self.settings.dry_run:
            return
        if not self.settings.username or not self.settings.password:
            raise RuntimeError("Set SIMULATOR_TOKEN or SIMULATOR_USERNAME and SIMULATOR_PASSWORD")
        response = await self.client.post(
            "/auth/login",
            data={"username": self.settings.username, "password": self.settings.password},
        )
        response.raise_for_status()
        self.settings = SimulatorSettings(**{**self.settings.__dict__, "token": response.json()["access_token"]})

    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.settings.token}"} if self.settings.token else {}

    async def onboard(self, source: SimulatedCameraSource) -> int:
        response = await self.client.post(
            "/cameras/onboard",
            headers=self.headers(),
            json={
                "name": source.name,
                "department": source.department,
                "lat": source.lat,
                "lng": source.lng,
                "camera_type": source.camera_type,
                "source_protocol": "simulator",
                "stream_endpoint": source.stream_endpoint,
                "zone": source.zone,
                "storage_metadata": {"adapter": "simulated", "source_key": source.key},
                "external_id": source.key,
            },
        )
        response.raise_for_status()
        return response.json()["id"]

    async def prepare_sources(self) -> None:
        await self.authenticate()
        for source in SIMULATED_SOURCES:
            if self.settings.dry_run:
                self.camera_ids[source.key] = 1 if source.key == "traffic-junction" else 2
            else:
                self.camera_ids[source.key] = await self.onboard(source)
            logger.info("source ready: %s camera_id=%s stream=%s", source.key, self.camera_ids[source.key], source.stream_endpoint)

    async def heartbeat(self, source: SimulatedCameraSource, status: str = "online") -> None:
        payload = {"status": status}
        if self.settings.dry_run:
            logger.info("heartbeat camera=%s payload=%s", source.key, payload)
            return
        response = await self.client.post(f"/cameras/{self.camera_ids[source.key]}/heartbeat", headers=self.headers(), json=payload)
        response.raise_for_status()

    async def detection(self, source: SimulatedCameraSource, simulator: DetectionSimulator) -> None:
        payload: dict[str, Any] = {"camera_id": self.camera_ids[source.key], **simulator.next_detection(self.settings.watchlist_identifiers)}
        if self.settings.dry_run:
            logger.info("detection camera=%s payload=%s", source.key, payload)
            return
        response = await self.client.post("/events/detection", headers=self.headers(), json=payload)
        if response.status_code == 409:
            logger.info("duplicate detection ignored camera=%s", source.key)
            return
        response.raise_for_status()
        logger.info("detection accepted camera=%s vehicle=%s", source.key, payload["vehicle_number"])


async def run_source(client: SimulatorClient, source: SimulatedCameraSource, run_once: bool) -> None:
    simulator = DetectionSimulator(source, seed=hash(source.key) % 1000)
    await client.heartbeat(source)
    await client.detection(source, simulator)
    if run_once:
        return
    heartbeat_tick = 0
    while True:
        await asyncio.sleep(client.settings.detection_seconds)
        await client.detection(source, simulator)
        heartbeat_tick += 1
        if heartbeat_tick % max(1, round(client.settings.heartbeat_seconds / client.settings.detection_seconds)) == 0:
            status = "degraded" if simulator.event_count % 11 == 0 else "online"
            await client.heartbeat(source, status)


async def run() -> None:
    settings = SimulatorSettings()
    client = SimulatorClient(settings)
    try:
        await client.prepare_sources()
        await asyncio.gather(*(run_source(client, source, settings.run_once) for source in SIMULATED_SOURCES))
    finally:
        await client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="okDriver simulated camera adapter")
    parser.add_argument("--once", action="store_true", help="send one heartbeat and detection per source")
    args = parser.parse_args()
    if args.once:
        os.environ["SIMULATOR_RUN_ONCE"] = "true"
    asyncio.run(run())
