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
    PlatformChangePlanRequest,
    PlatformChangePlanResponse,
    PlanPrice,
    CreditPack,
    LifetimePlan,
    PlatformProductsResponse,
    PlatformCreditCheckoutRequest,
    PlatformUserCreditsResponse,
    PlatformCheckoutRequest,
    PlatformCheckoutResponse,
    PlatformModerationRequest,
    PlatformTokenRequest,
    PlatformTokenResponse,
    PlatformUserInfo,
    ProvisionUserRequest,
    ProvisionUserResponse,
    StripeConnectStatusResponse,
    Tier,
    UsernameCheckRequest,
    UsernameCheckResponse,
)
from .platform import PlatformClient

__all__ = [
    # Clients
    "SupervisorClient",
    "SyncSupervisorClient",
    "PlatformClient",
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
    "PlatformTokenRequest",
    "ProvisionUserRequest",
    "PlatformModerationRequest",
    "PlatformCheckoutRequest",
    "PlatformChangePlanRequest",
    "PlanPrice",
    "CreditPack",
    "LifetimePlan",
    "PlatformProductsResponse",
    "PlatformCreditCheckoutRequest",
    "PlatformUserCreditsResponse",
    "ConfirmAuthorizationRequest",
    # Response models
    "ModerationResponse",
    "UsernameCheckResponse",
    "PlatformTokenResponse",
    "ProvisionUserResponse",
    "PlatformUserInfo",
    "PlatformCheckoutResponse",
    "PlatformChangePlanResponse",
    "ConfirmAuthorizationResponse",
    "StripeConnectStatusResponse",
]
