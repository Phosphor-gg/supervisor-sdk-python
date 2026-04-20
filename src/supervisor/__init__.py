"""Supervisor SDK — Official Python client for the Supervisor content moderation API."""

from .client import SupervisorClient, SyncSupervisorClient
from .errors import AuthenticationError, RateLimitError, SupervisorError, ValidationError
from .models import (
    BatchModerationRequest,
    BillingCycle,
    ConfirmAuthorizationRequest,
    ConfirmAuthorizationResponse,
    ModerationLabel,
    ModerationModel,
    ModerationRequest,
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
    Tier,
    UsernameCheckRequest,
    UsernameCheckResponse,
)
from .partner import PartnerClient

__all__ = [
    # Clients
    "SupervisorClient",
    "SyncSupervisorClient",
    "PartnerClient",
    # Errors
    "SupervisorError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    # Enums
    "ModerationLabel",
    "ModerationModel",
    "Tier",
    "BillingCycle",
    # Request models
    "ModerationRequest",
    "BatchModerationRequest",
    "UsernameCheckRequest",
    "PartnerTokenRequest",
    "ProvisionUserRequest",
    "PartnerModerationRequest",
    "PartnerCheckoutRequest",
    "ConfirmAuthorizationRequest",
    # Response models
    "ModerationResponse",
    "UsernameCheckResponse",
    "PartnerTokenResponse",
    "ProvisionUserResponse",
    "PartnerUserInfo",
    "PartnerCheckoutResponse",
    "ConfirmAuthorizationResponse",
    "StripeConnectStatusResponse",
]
