"""Supervisor Partner API client with OAuth2 client credentials flow."""

from __future__ import annotations

import time
from typing import Optional

import httpx

from .client import DEFAULT_BASE_URL
from .errors import AuthenticationError, RateLimitError, SupervisorError, ValidationError
from .models import (
    ConfirmAuthorizationRequest,
    ConfirmAuthorizationResponse,
    ModerationLabel,
    ModerationModel,
    ModerationResponse,
    PartnerCheckoutRequest,
    PartnerCheckoutResponse,
    PartnerModerationRequest,
    PartnerTokenRequest,
    PartnerTokenResponse,
    PartnerUserInfo,
    ProvisionUserRequest,
    ProvisionUserResponse,
    StripeConnectStatusResponse,
    BillingCycle,
    Tier,
)


class PartnerClient:
    """Async client for the Supervisor Partner API.

    Handles OAuth2 client credentials token exchange and automatic refresh.

    Usage:
        async with PartnerClient(client_id="...", client_secret="...") as client:
            user = await client.provision_user("user@example.com")
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def _ensure_token(self) -> str:
        """Get a valid access token, refreshing if expired."""
        if self._access_token and time.time() < self._token_expires_at - 30:
            return self._access_token

        request = PartnerTokenRequest(
            client_id=self._client_id,
            client_secret=self._client_secret,
        )
        response = await self._client.post(
            "/api/partner/token", json=request.model_dump()
        )
        if response.status_code >= 400:
            self._raise_error(response)

        token_response = PartnerTokenResponse.model_validate(response.json())
        self._access_token = token_response.access_token
        self._token_expires_at = time.time() + token_response.expires_in
        return self._access_token

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        token = await self._ensure_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        response = await self._client.request(method, path, headers=headers, **kwargs)
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

    async def provision_user(self, email: str) -> ProvisionUserResponse:
        """Provision or link a user by email.

        Args:
            email: The user's email address.

        Returns:
            ProvisionUserResponse with user_id and account status.
        """
        request = ProvisionUserRequest(email=email)
        response = await self._request(
            "POST", "/api/partner/users/provision", json=request.model_dump()
        )
        return ProvisionUserResponse.model_validate(response.json())

    async def list_users(self) -> list[PartnerUserInfo]:
        """List all users linked to this partner.

        Returns:
            List of PartnerUserInfo with subscription details.
        """
        response = await self._request("GET", "/api/partner/users")
        return [PartnerUserInfo.model_validate(u) for u in response.json()]

    async def get_user(self, user_id: str) -> PartnerUserInfo:
        """Get a specific linked user by ID.

        Args:
            user_id: The user's ID.

        Returns:
            PartnerUserInfo for the specified user.
        """
        response = await self._request("GET", f"/api/partner/users/{user_id}")
        return PartnerUserInfo.model_validate(response.json())

    async def moderate(
        self,
        user_email: str,
        *,
        text: Optional[str] = None,
        image: Optional[str] = None,
        model: Optional[ModerationModel] = None,
        enabled_labels: Optional[list[ModerationLabel]] = None,
        include_context: bool = False,
    ) -> ModerationResponse:
        """Moderate content on behalf of a linked user.

        Args:
            user_email: Email of the user whose credits to use.
            text: Text content to moderate.
            image: Base64-encoded image to moderate.
            model: AI model to use.
            enabled_labels: Specific labels to check for.
            include_context: Whether to include conversation context.

        Returns:
            ModerationResponse with flagged status and detected labels.
        """
        request = PartnerModerationRequest(
            user_email=user_email,
            text=text,
            image=image,
            model=model,
            enabled_labels=enabled_labels,
            include_context=include_context,
        )
        response = await self._request(
            "POST", "/api/partner/moderate", json=request.model_dump(exclude_none=True)
        )
        return ModerationResponse.model_validate(response.json())

    async def create_checkout(
        self,
        user_email: str,
        tier: Tier,
        billing_cycle: BillingCycle,
        success_url: str,
        cancel_url: str,
    ) -> PartnerCheckoutResponse:
        """Create a Stripe checkout session for a partner user.

        Args:
            user_email: Email of the user to create checkout for.
            tier: Subscription tier to purchase.
            billing_cycle: Billing period.
            success_url: URL to redirect on success.
            cancel_url: URL to redirect on cancel.

        Returns:
            PartnerCheckoutResponse with the checkout URL.
        """
        request = PartnerCheckoutRequest(
            user_email=user_email,
            tier=tier,
            billing_cycle=billing_cycle,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        response = await self._request(
            "POST", "/api/partner/checkout", json=request.model_dump()
        )
        return PartnerCheckoutResponse.model_validate(response.json())

    async def confirm_authorization(self, code: str) -> ConfirmAuthorizationResponse:
        """Confirm a user's authorization with the provided code.

        Args:
            code: The authorization code from the consent flow.

        Returns:
            ConfirmAuthorizationResponse with user_id and email.
        """
        request = ConfirmAuthorizationRequest(code=code)
        response = await self._request(
            "POST", "/api/partner/users/confirm-authorization", json=request.model_dump()
        )
        return ConfirmAuthorizationResponse.model_validate(response.json())

    async def get_connect_status(self) -> StripeConnectStatusResponse:
        """Get the Stripe Connect onboarding status.

        Returns:
            StripeConnectStatusResponse with account and charge status.
        """
        response = await self._request("GET", "/api/partner/connect/status")
        return StripeConnectStatusResponse.model_validate(response.json())
