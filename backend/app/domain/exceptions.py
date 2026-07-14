"""Domain-level exceptions.

These are framework-agnostic. The API layer maps them to HTTP responses in
``app/middleware/error_handlers.py``; the graph layer maps them to node errors.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain errors."""

    default_message = "A domain error occurred."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)
        self.message = message or self.default_message


class EntityNotFoundError(DomainError):
    """Raised when a requested aggregate/entity does not exist."""

    default_message = "The requested entity was not found."


class DuplicateEntityError(DomainError):
    """Raised when creating an entity that violates a uniqueness constraint."""

    default_message = "An entity with the same identity already exists."


class ValidationError(DomainError):
    """Raised when a domain invariant is violated."""

    default_message = "The provided data violates a domain invariant."


class AuthenticationError(DomainError):
    """Raised on invalid credentials or token."""

    default_message = "Authentication failed."


class AuthorizationError(DomainError):
    """Raised when an authenticated principal lacks the required role."""

    default_message = "You are not authorized to perform this action."


class InvestigationError(DomainError):
    """Raised when the agent graph cannot complete an investigation."""

    default_message = "The investigation could not be completed."


class AgentExecutionError(DomainError):
    """Raised when an individual agent exhausts its retries."""

    default_message = "An agent failed to execute after retries."

    def __init__(self, agent: str, message: str | None = None) -> None:
        super().__init__(message or f"Agent '{agent}' failed after retries.")
        self.agent = agent


class ToolExecutionError(DomainError):
    """Raised when a LangChain tool fails."""

    default_message = "A tool failed to execute."
