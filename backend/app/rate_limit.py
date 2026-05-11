import time

import redis
from fastapi import HTTPException, Request, status

from app.config import get_settings

_memory_hits: dict[str, list[float]] = {}


def check_rate_limit(request: Request) -> None:
    settings = get_settings()
    identifier = request.client.host if request.client else "unknown"
    limit = settings.rate_limit_per_minute
    if settings.redis_url:
        try:
            client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=0.2)
            key = f"rate:{identifier}:{int(time.time() // 60)}"
            hits = client.incr(key)
            client.expire(key, 70)
            if hits > limit:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
            return
        except redis.RedisError:
            pass

    now = time.time()
    window = [hit for hit in _memory_hits.get(identifier, []) if now - hit < 60]
    window.append(now)
    _memory_hits[identifier] = window
    if len(window) > limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
