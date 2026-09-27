from dataclasses import dataclass
from datetime import datetime, timezone
from random import Random
from typing import Any


@dataclass(frozen=True)
class SimulatedCameraSource:
    key: str
    name: str
    department: str
    zone: str
    lat: float
    lng: float
    camera_type: str
    stream_endpoint: str


SIMULATED_SOURCES = (
    SimulatedCameraSource(
        key="traffic-junction",
        name="MG Road Traffic Junction",
        department="Bengaluru Traffic Operations",
        zone="Central Junction",
        lat=12.9718,
        lng=77.5946,
        camera_type="traffic_junction",
        stream_endpoint="http://localhost:8081/traffic-junction/index.m3u8",
    ),
    SimulatedCameraSource(
        key="rto-checkpoint",
        name="Electronic City RTO Checkpoint",
        department="RTO Enforcement",
        zone="Electronic City Gate",
        lat=12.8452,
        lng=77.6602,
        camera_type="rto_checkpoint",
        stream_endpoint="http://localhost:8081/rto-checkpoint/index.m3u8",
    ),
)

VEHICLE_TYPES = ("car", "motorcycle", "truck", "bus")
SAMPLE_NUMBERS = ("KA01AB1234", "KA05MN7788", "KA03PQ4421", "MH12RT9087", "DL01CD6612")


class DetectionSimulator:
    def __init__(self, source: SimulatedCameraSource, seed: int = 1) -> None:
        self.source = source
        self.random = Random(seed)
        self.event_count = 0

    def next_detection(self, watchlist_identifiers: tuple[str, ...]) -> dict[str, Any]:
        self.event_count += 1
        should_match = bool(watchlist_identifiers) and self.event_count % 5 == 0
        vehicle_number = (
            watchlist_identifiers[self.random.randrange(len(watchlist_identifiers))]
            if should_match
            else self.random.choice(SAMPLE_NUMBERS)
        )
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "vehicle_detection",
            "vehicle_number": vehicle_number,
            "vehicle_type": self.random.choice(VEHICLE_TYPES),
            "confidence": round(self.random.uniform(0.86, 0.99), 3),
            "bounding_box": {
                "x": round(self.random.uniform(0.1, 0.6), 3),
                "y": round(self.random.uniform(0.1, 0.6), 3),
                "width": round(self.random.uniform(0.15, 0.35), 3),
                "height": round(self.random.uniform(0.15, 0.3), 3),
            },
            "raw_payload": {
                "source": "okdriver-simulator",
                "source_key": self.source.key,
                "inference_model": "simulated-anpr-v1",
                "watchlist_match_candidate": should_match,
            },
        }
