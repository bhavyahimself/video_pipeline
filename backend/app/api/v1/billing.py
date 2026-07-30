"""
ClipEngine — Billing Endpoints
Stripe checkout, portal, webhook, usage.
"""

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User, PlanTier
from app.models.video import Subscription
from app.schemas import PlanInfo, CheckoutRequest, CheckoutResponse, UsageResponse
from app.services.auth_service import get_current_user

router = APIRouter()
settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY

PLANS = {
    "free": PlanInfo(
        name="Free",
        price_monthly=0,
        videos_per_month=3,
        channels="3 basic channels",
        features=[
            "3 videos per month",
            "3 basic channel templates",
            "Default voice only",
            "720p output",
            "ClipEngine watermark",
        ],
    ),
    "creator": PlanInfo(
        name="Creator",
        price_monthly=29,
        videos_per_month=30,
        channels="All 11 channels",
        features=[
            "30 videos per month",
            "All 11 channel templates",
            "Custom voice selection",
            "1080p output",
            "No watermark",
            "YouTube direct upload",
            "Script version history",
            "Email support",
        ],
    ),
    "studio": PlanInfo(
        name="Studio",
        price_monthly=99,
        videos_per_month="Unlimited",
        channels="All + custom channels",
        features=[
            "Unlimited videos",
            "All channels + create custom",
            "Voice cloning support",
            "Team collaboration (5 members)",
            "API access (1000 req/day)",
            "Batch generation (10 at once)",
            "Priority render queue",
            "A/B thumbnail testing",
            "Advanced analytics + export",
            "Template marketplace",
            "Priority support",
        ],
    ),
    "enterprise": PlanInfo(
        name="Enterprise",
        price_monthly=299,
        videos_per_month="Unlimited",
        channels="All + white-label",
        features=[
            "Everything in Studio",
            "Unlimited team members",
            "White-label (no branding)",
            "Dedicated rendering workers",
            "API access (10,000 req/day)",
            "Scheduled publishing",
            "Custom integrations",
            "Dedicated Slack support",
            "99.9% SLA",
        ],
    ),
}


@router.get("/plans", response_model=dict[str, PlanInfo])
async def list_plans():
    """Get all available plans."""
    return PLANS


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    body: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe Checkout session for a plan upgrade."""
    if body.plan not in ("creator", "studio", "enterprise"):
        raise HTTPException(status_code=400, detail="Invalid plan")

    price_map = {
        "creator": settings.STRIPE_PRICE_CREATOR,
        "studio": settings.STRIPE_PRICE_STUDIO,
        "enterprise": settings.STRIPE_PRICE_ENTERPRISE,
    }

    price_id = price_map[body.plan]
    if not price_id:
        raise HTTPException(status_code=500, detail="Stripe price not configured for this plan")

    # Get or create Stripe customer
    if not current_user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.name,
            metadata={"user_id": str(current_user.id)},
        )
        current_user.stripe_customer_id = customer.id
        await db.flush()

    # Create checkout session
    session = stripe.checkout.Session.create(
        customer=current_user.stripe_customer_id,
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=body.success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=body.cancel_url,
        metadata={"user_id": str(current_user.id), "plan": body.plan},
    )

    return CheckoutResponse(checkout_url=session.url)


@router.post("/portal")
async def create_portal(
    current_user: User = Depends(get_current_user),
):
    """Create a Stripe Customer Portal session for managing subscription."""
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=f"{settings.ALLOWED_ORIGINS.split(',')[0]}/settings/billing",
    )

    return {"portal_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        plan = session["metadata"]["plan"]

        # Update user plan
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.plan = PlanTier(plan)
            user.videos_used_this_period = 0

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]

        result = await db.execute(
            select(User).where(User.stripe_customer_id == customer_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.plan = PlanTier.FREE

    return {"status": "ok"}


@router.get("/usage", response_model=UsageResponse)
async def get_usage(current_user: User = Depends(get_current_user)):
    """Get current billing period usage."""
    limit_map = {
        PlanTier.FREE: settings.FREE_VIDEO_LIMIT,
        PlanTier.CREATOR: settings.CREATOR_VIDEO_LIMIT,
        PlanTier.STUDIO: "Unlimited",
        PlanTier.ENTERPRISE: "Unlimited",
    }

    return UsageResponse(
        plan=current_user.plan.value,
        videos_used=current_user.videos_used_this_period,
        videos_limit=limit_map[current_user.plan],
        period_start=None,
        period_end=current_user.period_reset_date,
    )

