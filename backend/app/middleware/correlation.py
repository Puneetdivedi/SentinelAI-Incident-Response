"""Correlation-ID middleware.

Assigns (or propagates) an ``X-Request-ID`` per request and binds it to the logging
context var so every log line emitted during the request is correlated.
"""

from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config.logging import correlation_id_ctx

_HEADER = "X-Request-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get(_HEADER) or str(uuid.uuid4())
        token = correlation_id_ctx.set(correlation_id)
        request.state.correlation_id = correlation_id
        try:
            response = await call_next(request)
        finally:
            correlation_id_ctx.reset(token)
        response.headers[_HEADER] = correlation_id
        return response
