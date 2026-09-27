import json
from collections.abc import AsyncIterator
from typing import Any

from redis.asyncio import Redis, from_url

from app.core.config import get_settings

CHANNEL = "okdriver.events"


def get_redis() -> Redis:
    return from_url(get_settings().redis_url, decode_responses=True)


async def publish_event(event_type: str, payload: dict[str, Any]) -> None:
    redis = get_redis()
    try:
        await redis.publish(CHANNEL, json.dumps({"type": event_type, "data": payload}, default=str))
    finally:
        await redis.aclose()


async def subscribe_events() -> AsyncIterator[dict[str, Any]]:
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(CHANNEL)
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=20)
            if message and isinstance(message.get("data"), str):
                yield json.loads(message["data"])
    finally:
        await pubsub.unsubscribe(CHANNEL)
        await pubsub.close()
        await redis.aclose()
