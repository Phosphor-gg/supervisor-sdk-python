# Supervisor Python SDK

Official Python SDK for the [Supervisor](https://supervisor.gg) content moderation API.

## Installation

```bash
pip install supervisor-sdk
```

## Quick Start

```python
import asyncio
from supervisor import SupervisorClient, ModerationModel

async def main():
    async with SupervisorClient(api_key="sk-...") as client:
        # Moderate text
        result = await client.moderate("check this text")
        print(f"Flagged: {result.flagged}")
        print(f"Labels: {result.labels}")

        # Use a specific model
        result = await client.moderate(
            "another message",
            model=ModerationModel.SENTINEL,
        )

        # Batch moderation
        results = await client.moderate_batch([
            "first message",
            "second message",
            "third message",
        ])
        for r in results:
            print(f"Flagged: {r.flagged}, Labels: {r.labels}")

        # Username check
        username_result = await client.check_username("user123")
        print(f"Username flagged: {username_result.flagged}")

asyncio.run(main())
```

## Synchronous Usage

```python
from supervisor import SyncSupervisorClient

with SyncSupervisorClient(api_key="sk-...") as client:
    result = client.moderate("check this text")
    print(f"Flagged: {result.flagged}")
```

## Platform API

For platform integrations using OAuth2 client credentials:

```python
from supervisor import PlatformClient, Tier, BillingCycle

async with PlatformClient(client_id="...", client_secret="...") as platform:
    # Provision a user
    user = await platform.provision_user("user@example.com")

    # Moderate on behalf of a user
    result = await platform.moderate("user@example.com", text="check this")

    # Create a checkout session
    checkout = await platform.create_checkout(
        user_email="user@example.com",
        tier=Tier.STANDARD,
        billing_cycle=BillingCycle.MONTHLY,
        success_url="https://yourapp.com/success",
        cancel_url="https://yourapp.com/cancel",
    )
    print(f"Checkout URL: {checkout.checkout_url}")

    # List linked users
    users = await platform.list_users()

    # Get a specific linked user by ID
    info = await platform.get_user(user.user_id)
    print(f"Authorized: {info.authorized}, Tier: {info.tier}")

    # Confirm a user's authorization with the code from the consent flow
    confirmed = await platform.confirm_authorization("auth-code-from-redirect")
    print(f"Authorized user: {confirmed.email}")

    # Check Stripe Connect onboarding status
    status = await platform.get_connect_status()
    print(f"Onboarding complete: {status.onboarding_complete}")

    # Change the plan of an existing subscription
    change = await platform.change_plan(
        user_email="user@example.com",
        tier=Tier.PREMIUM,
        billing_cycle=BillingCycle.ANNUAL,
    )
    print(f"Subscription {change.subscription_id} is now {change.tier}")
```

### Checkout and plan changes

`create_checkout` returns 403 if the user has not authorized the platform, and 400 if the user already has an active subscription (use `change_plan` instead). `change_plan` returns 403 if the subscription was not originated by this platform, and 400 if there is no active subscription. Revenue share is set at subscription creation and preserved across plan changes.

## Configuration

```python
client = SupervisorClient(
    api_key="sk-...",
    base_url="https://supervisor.gg",  # default
    timeout=30.0,                      # seconds, default
)
```

## Moderation Labels

| Label | Description |
|-------|-------------|
| `profanity` | Profanity |
| `toxicity` | Toxicity |
| `harassment` | Harassment |
| `hate` | Hate/Racism |
| `insult` | Insult |
| `sexual` | Sexual |
| `sexual/unlawful` | Sexual (Unlawful) |
| `sexual/explicit` | Sexual (Explicit) |
| `sensitive` | Sensitive Content |
| `violence` | Violence |
| `self-harm` | Self-Harm |
| `medical` | Medical/Injury |
| `spam` | Spam |
| `promotional` | Promotional |
| `scam` | Scam/Incoherent |
| `illegal` | Illegal Activity |

## Models

| Model | Cost | Description |
|-------|------|-------------|
| `auto` | Varies | Automatically selects based on available credits |
| `observer` | 1 credit/byte | Fastest, most affordable |
| `sentinel` | 3 credits/byte | Balanced accuracy and speed |
| `arbiter` | 9 credits/byte | Most accurate |

## Error Handling

```python
from supervisor import SupervisorClient, SupervisorError, AuthenticationError, RateLimitError

try:
    result = await client.moderate("text")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Too many requests")
except SupervisorError as e:
    print(f"API error [{e.status_code}]: {e.message}")
```

## License

MIT
