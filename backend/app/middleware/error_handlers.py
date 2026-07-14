"""Maps domain exceptions to HTTP responses.

Keeps the API layer thin: services raise domain errors, and these handlers translate them
to consistent JSON problem responses without leaking internals.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.config.logging import get_logger
from app.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)

logger = get_logger(__name__)

_STATUS_MAP: dict[type[DomainError], int] = {
    EntityNotFoundError: status.HTTP_404_NOT_FOUND,
    DuplicateEntityError: status.HTTP_409_CONFLICT,
    ValidationError: 422,  # Unprocessable Content (constant name varies across versions)
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
}


def _status_for(exc: DomainError) -> int:
    for exc_type, code in _STATUS_MAP.items():
        if isinstance(exc, exc_type):
            return code
    return status.HTTP_400_BAD_REQUEST


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def _handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        code = _status_for(exc)
        if code >= 500:
            logger.exception("unhandled_domain_error", extra={"path": request.url.path})
        return JSONResponse(status_code=code, content={"detail": exc.message})
