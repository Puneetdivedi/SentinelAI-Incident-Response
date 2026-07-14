"""Authentication service.

Owns credential verification and token issuance. Depends only on repository ports and the
pure security helpers — no FastAPI or DB session coupling.
"""

from __future__ import annotations

from app.config.logging import get_logger
from app.config.settings import Settings
from app.domain.entities import User
from app.domain.exceptions import AuthenticationError
from app.repositories.interfaces import UserRepository
from app.schemas.auth import TokenPair
from app.utils.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)

logger = get_logger(__name__)


class AuthService:
    def __init__(self, settings: Settings, user_repository: UserRepository) -> None:
        self._settings = settings
        self._users = user_repository

    async def authenticate(self, email: str, password: str) -> User:
        """Verify credentials and return the user, or raise ``AuthenticationError``.

        The same error is raised for unknown-user and bad-password to avoid user
        enumeration; a dummy hash is still verified to keep timing uniform.
        """
        user = await self._users.get_by_email(email)
        if user is None:
            # Constant-time-ish: still run a verify against a throwaway hash.
            verify_password(password, DUMMY_PASSWORD_HASH)
            raise AuthenticationError("Invalid email or password.")

        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("This account is disabled.")

        return user

    def issue_tokens(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(
                self._settings, subject=user.id, role=user.role.value
            ),
            refresh_token=create_refresh_token(
                self._settings, subject=user.id, role=user.role.value
            ),
        )

    async def login(self, email: str, password: str) -> tuple[User, TokenPair]:
        user = await self.authenticate(email, password)
        return user, self.issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        claims = decode_token(
            self._settings, refresh_token, expected_type="refresh"
        )
        user = await self._users.get_by_id(claims.subject)
        if user is None or not user.is_active:
            raise AuthenticationError("User no longer valid for this token.")
        return self.issue_tokens(user)
