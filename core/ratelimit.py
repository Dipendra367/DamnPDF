import time
from collections import defaultdict, deque

from starlette.responses import JSONResponse

from core.config import MAX_FILE_SIZE, RATE_LIMIT_PER_MINUTE


class RateLimitMiddleware:
    """Per-IP sliding-window rate limit + early rejection of oversized bodies.

    Pure ASGI (no BaseHTTPMiddleware) so it adds ~zero overhead to the
    event loop. Buckets live in memory — fine for a single container.
    """

    def __init__(self, app, limit: int = RATE_LIMIT_PER_MINUTE, window: float = 60.0):
        self.app = app
        self.limit = limit
        self.window = window
        self.buckets: dict[str, deque] = defaultdict(deque)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        ip = client[0] if client else "unknown"

        now = time.monotonic()
        bucket = self.buckets[ip]
        while bucket and now - bucket[0] > self.window:
            bucket.popleft()

        if len(bucket) >= self.limit:
            retry_after = max(1, int(self.window - (now - bucket[0])))
            response = JSONResponse(
                {"detail": "Too many requests. Slow down and try again shortly."},
                status_code=429,
                headers={"Retry-After": str(retry_after)},
            )
            await response(scope, receive, send)
            return

        bucket.append(now)

        # reject oversized uploads before the body is read into memory
        for name, value in scope.get("headers", []):
            if name == b"content-length":
                try:
                    if int(value) > MAX_FILE_SIZE + 1024 * 1024:  # 1MB slack for multipart overhead
                        response = JSONResponse(
                            {"detail": "File too large. Max size is 100MB."},
                            status_code=413,
                        )
                        await response(scope, receive, send)
                        return
                except ValueError:
                    break

        await self.app(scope, receive, send)
