import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import LOGGER


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        if request.url.path.startswith("/api/"):
            LOGGER.info("request", method=request.method, path=request.url.path, status=response.status_code, duration_ms=round(duration * 1000, 2))
        return response
