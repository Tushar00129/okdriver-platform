import logging
from time import time

from fastapi import HTTPException, Request, status
from redis.exceptions import RedisError

from app.services.realtime import get_redis

logger = logging.getLogger(__name__)


async def enforce_ingestion_rate_limit(request: Request, limit: int = 120, window_seconds: int = 60) -> None:
    client = request.client.host if request.client else "unknown"
    bucket = int(time() // window_seconds)
    key = f"rate:ingestion:{client}:{bucket}"
    redis = get_redis()
    try:
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, window_seconds + 1)
        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Detection ingestion rate limit exceeded",
                headers={"Retry-After": str(window_seconds)},
            )
    except HTTPException:
        raise
    except RedisError:
        logger.warning("Redis unavailable; allowing ingestion without rate-limit enforcement")
    finally:
        await redis.aclose()
