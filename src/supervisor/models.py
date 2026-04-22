"""Supervisor API models and enums."""

from __future__ import annotations

from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class ModerationLabel(StrEnum):
    """Content moderation category labels."""

    PROFANITY = "profanity"
    TOXICITY = "toxicity"
    HARASSMENT = "harassment"
    HATE = "hate"
    INSULT = "insult"
    SEXUAL = "sexual"
    SEXUAL_MINORS = "sexual/minors"
    SEXUAL_EXPLICIT = "sexual/explicit"
    SENSITIVE = "sensitive"
    VIOLENCE = "violence"
    SELF_HARM = "self-harm"
    MEDICAL = "medical"
    SPAM = "spam"
    PROMOTIONAL = "promotional"
    SCAM = "scam"
    ILLEGAL = "illegal"
    PERSONAL_DATA = "personal-data"


class ModerationModel(StrEnum):
    """Available AI moderation models."""

    AUTO = "auto"
    OBSERVER = "observer"
    SENTINEL = "sentinel"
    ARBITER = "arbiter"


class Tier(StrEnum):
    """Subscription tiers."""

    FREE = "Free"
    BASIC = "Basic"
    STANDARD = "Standard"
    PREMIUM = "Premium"


class BillingCycle(StrEnum):
    """Billing cycle options."""

    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    ANNUAL = "Annual"
    TRIENNIAL = "Triennial"


# --- Request Models ---


class ModerationRequest(BaseModel):
    """Request to moderate text or an image."""

    text: Optional[str] = None
    image: Optional[str] = None
    model: Optional[ModerationModel] = None
    enabled_labels: Optional[list[ModerationLabel]] = None
    include_context: bool = False


class BatchModerationRequest(BaseModel):
    """Request to moderate multiple texts at once."""

    texts: list[str]
    model: Optional[ModerationModel] = None
    enabled_labels: Optional[list[ModerationLabel]] = None
    include_context: bool = False


class UsernameCheckRequest(BaseModel):
    """Request to check a username for violations."""

    username: str


class PlatformTokenRequest(BaseModel):
    """OAuth2 client credentials token exchange."""

    client_id: str
    client_secret: str
    grant_type: str = "client_credentials"


class ProvisionUserRequest(BaseModel):
    """Provision or link a user by email."""

    email: str


class PlatformModerationRequest(BaseModel):
    """Moderate content on behalf of a platform user."""

    user_email: str
    text: Optional[str] = None
    image: Optional[str] = None
    model: Optional[ModerationModel] = None
    enabled_labels: Optional[list[ModerationLabel]] = None
    include_context: bool = False


class PlatformCheckoutRequest(BaseModel):
    """Create a checkout session for a platform user."""

    user_email: str
    tier: Tier
    billing_cycle: BillingCycle
    success_url: str
    cancel_url: str


class ConfirmAuthorizationRequest(BaseModel):
    """Confirm user authorization with a code."""

    code: str


# --- Response Models ---


class ModerationResponse(BaseModel):
    """Result of a moderation request."""

    flagged: bool
    labels: list[ModerationLabel]
    implicit_labels: Optional[list[ModerationLabel]] = None
    model_version: Optional[str] = None
    needs_context: Optional[bool] = None
    context_labels: Optional[list[ModerationLabel]] = None
    rewritten_text: Optional[str] = None


class UsernameCheckResponse(BaseModel):
    """Result of a username check."""

    flagged: bool
    score: float


class PlatformTokenResponse(BaseModel):
    """OAuth2 access token response."""

    access_token: str
    token_type: str
    expires_in: int


class ProvisionUserResponse(BaseModel):
    """Result of provisioning a user."""

    user_id: str
    email: str
    is_new_account: bool
    is_newly_linked: bool


class PlatformUserInfo(BaseModel):
    """Platform's view of a linked user."""

    user_id: str
    email: str
    linked_at: str
    authorized: bool
    has_active_subscription: bool
    tier: Tier


class PlatformCheckoutResponse(BaseModel):
    """Checkout session URL."""

    checkout_url: str


class ConfirmAuthorizationResponse(BaseModel):
    """Confirmed authorization result."""

    user_id: str
    email: str


class StripeConnectStatusResponse(BaseModel):
    """Stripe Connect onboarding status."""

    account_id: Optional[str] = None
    onboarding_complete: bool
    charges_enabled: bool


class ErrorResponse(BaseModel):
    """API error response."""

    error: str
    details: Optional[str] = None
