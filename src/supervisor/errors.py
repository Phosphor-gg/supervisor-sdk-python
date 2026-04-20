"""Supervisor SDK exceptions."""

from __future__ import annotations

from typing import Optional


class SupervisorError(Exception):
    """Base exception for Supervisor API errors."""

    def __init__(self, status_code: int, message: str, details: Optional[str] = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"[{status_code}] {message}" + (f": {details}" if details else ""))


class AuthenticationError(SupervisorError):
    """Raised when authentication fails (401)."""

    pass


class RateLimitError(SupervisorError):
    """Raised when rate limited (429)."""

    pass


class ValidationError(SupervisorError):
    """Raised when request validation fails (400/422)."""

    pass
