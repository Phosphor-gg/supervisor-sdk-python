"""Supervisor API client."""

from __future__ import annotations

from typing import Optional

import httpx

from .errors import AuthenticationError, RateLimitError, SupervisorError, ValidationError
from .models import (
    BatchModerationRequest,
    ModerationLabel,
    ModerationModel,
    ModerationRequest,
    ModerationResponse,
    UsernameCheckRequest,
    UsernameCheckResponse,
)

DEFAULT_BASE_URL = "https://api.supervisor.gg"


class SupervisorClient:
    """Async client for the Supervisor content moderation API.

    Usage:
        async with SupervisorClient(api_key="sk-...") as client:
            result = await client.moderate("hello world")
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        response = await self._client.request(method, path, **kwargs)
        if response.status_code >= 400:
            self._raise_error(response)
        return response

    def _raise_error(self, response: httpx.Response) -> None:
        try:
            body = response.json()
            message = body.get("error", response.reason_phrase)
            details = body.get("details")
        except Exception:
            message = response.reason_phrase or "Unknown error"
            details = None

        status = response.status_code
        if status == 401:
            raise AuthenticationError(status, message, details)
        elif status == 429:
            raise RateLimitError(status, message, details)
        elif status in (400, 422):
            raise ValidationError(status, message, details)
        else:
            raise SupervisorError(status, message, details)

    async def moderate(
        self,
        text: Optional[str] = None,
        *,
        image: Optional[str] = None,
        model: Optional[ModerationModel] = None,
        enabled_labels: Optional[list[ModerationLabel]] = None,
        include_context: bool = False,
    ) -> ModerationResponse:
        """Moderate text or an image for harmful content.

        Args:
            text: Text content to moderate.
            image: Base64-encoded image to moderate.
            model: AI model to use (Auto, Observer, Sentinel, Arbiter).
            enabled_labels: Specific labels to check for. None means all.
            include_context: Whether to include conversation context.

        Returns:
            ModerationResponse with flagged status and detected labels.
        """
        request = ModerationRequest(
            text=text,
            image=image,
            model=model,
            enabled_labels=enabled_labels,
            include_context=include_context,
        )
        response = await self._request(
            "POST", "/api/moderate", json=request.model_dump(exclude_none=True)
        )
        return ModerationResponse.model_validate(response.json())

    async def moderate_batch(
        self,
        texts: list[str],
        *,
        images: Optional[list[str]] = None,
        model: Optional[ModerationModel] = None,
        enabled_labels: Optional[list[ModerationLabel]] = None,
        include_context: bool = False,
    ) -> list[ModerationResponse]:
        """Moderate multiple texts and/or images in a single request.

        Args:
            texts: List of text strings to moderate.
            images: List of base64-encoded images to moderate. If both texts
                and images are non-empty, their lengths must match.
            model: AI model to use.
            enabled_labels: Specific labels to check for.
            include_context: Whether to include conversation context.

        Returns:
            List of ModerationResponse, one per input item.
        """
        if texts and images and len(texts) != len(images):
            raise ValueError(
                "texts and images must have equal length when both are provided "
                f"(got {len(texts)} texts and {len(images)} images)."
            )
        request = BatchModerationRequest(
            texts=texts,
            images=images,
            model=model,
            enabled_labels=enabled_labels,
            include_context=include_context,
        )
        response = await self._request(
            "POST", "/api/batch", json=request.model_dump(exclude_none=True)
        )
        return [ModerationResponse.model_validate(r) for r in response.json()]

    async def check_username(self, username: str) -> UsernameCheckResponse:
        """Check a username for policy violations.

        Args:
            username: The username to check.

        Returns:
            UsernameCheckResponse with flagged status and confidence score.
        """
        request = UsernameCheckRequest(username=username)
        response = await self._request(
            "POST", "/api/username", json=request.model_dump()
        )
        return UsernameCheckResponse.model_validate(response.json())

    async def get_labels(self) -> dict[str, str]:
        """Get all available moderation labels.

        Returns:
            Mapping of label name to its description.
        """
        response = await self._request("GET", "/api/labels")
        return response.json()


class SyncSupervisorClient:
    """Synchronous client for the Supervisor content moderation API.

    Usage:
        with SyncSupervisorClient(api_key="sk-...") as client:
            result = client.moderate("hello world")
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """Close the underlying HTTP client."""
        self._client.close()

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        response = self._client.request(method, path, **kwargs)
        if response.status_code >= 400:
            self._raise_error(response)
        return response

    def _raise_error(self, response: httpx.Response) -> None:
        try:
            body = response.json()
            message = body.get("error", response.reason_phrase)
            details = body.get("details")
        except Exception:
            message = response.reason_phrase or "Unknown error"
            details = None

        status = response.status_code
        if status == 401:
            raise AuthenticationError(status, message, details)
        elif status == 429:
            raise RateLimitError(status, message, details)
        elif status in (400, 422):
            raise ValidationError(status, message, details)
        else:
            raise SupervisorError(status, message, details)

    def moderate(
        self,
        text: Optional[str] = None,
        *,
        image: Optional[str] = None,
        model: Optional[ModerationModel] = None,
        enabled_labels: Optional[list[ModerationLabel]] = None,
        include_context: bool = False,
    ) -> ModerationResponse:
        """Moderate text or an image for harmful content."""
        request = ModerationRequest(
            text=text,
            image=image,
            model=model,
            enabled_labels=enabled_labels,
            include_context=include_context,
        )
        response = self._request(
            "POST", "/api/moderate", json=request.model_dump(exclude_none=True)
        )
        return ModerationResponse.model_validate(response.json())

    def moderate_batch(
        self,
        texts: list[str],
        *,
        images: Optional[list[str]] = None,
        model: Optional[ModerationModel] = None,
        enabled_labels: Optional[list[ModerationLabel]] = None,
        include_context: bool = False,
    ) -> list[ModerationResponse]:
        """Moderate multiple texts and/or images in a single request.

        If both texts and images are non-empty, their lengths must match.
        """
        if texts and images and len(texts) != len(images):
            raise ValueError(
                "texts and images must have equal length when both are provided "
                f"(got {len(texts)} texts and {len(images)} images)."
            )
        request = BatchModerationRequest(
            texts=texts,
            images=images,
            model=model,
            enabled_labels=enabled_labels,
            include_context=include_context,
        )
        response = self._request(
            "POST", "/api/batch", json=request.model_dump(exclude_none=True)
        )
        return [ModerationResponse.model_validate(r) for r in response.json()]

    def check_username(self, username: str) -> UsernameCheckResponse:
        """Check a username for policy violations."""
        request = UsernameCheckRequest(username=username)
        response = self._request("POST", "/api/username", json=request.model_dump())
        return UsernameCheckResponse.model_validate(response.json())

    def get_labels(self) -> dict[str, str]:
        """Get all available moderation labels.

        Returns:
            Mapping of label name to its description.
        """
        response = self._request("GET", "/api/labels")
        return response.json()
