"""Subscription management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import User, Subscription
from app.utils.dependencies import get_current_user
from app.schemas.subscriptions import (
    SubscriptionPlan, SubscriptionCreate, SubscriptionResponse,
    BillingInfo, PaymentMethod, Invoice, WebhookEvent
)
from app.services.stripe_service import StripeService

router = APIRouter()


@router.get("/plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans():
    """Get all available subscription plans."""
    return StripeService.get_plans()


@router.get("/plan/{plan_id}", response_model=SubscriptionPlan)
async def get_subscription_plan(plan_id: str):
    """Get a specific subscription plan."""
    plan = StripeService.get_plan(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    return plan


@router.post("/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new subscription."""
    
    # Get the plan
    plan = StripeService.get_plan(subscription_data.plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    # Check if user already has an active subscription
    existing_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_(["active", "trialing"])
    ).first()
    
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active subscription"
        )
    
    try:
        # Create or get Stripe customer
        stripe_customer = None
        if current_user.email:
            try:
                stripe_customer = StripeService.create_customer(current_user.email)
            except Exception:
                # Customer might already exist, try to retrieve
                pass
        
        if not stripe_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create Stripe customer"
            )
        
        # Get the correct price ID based on billing cycle
        if subscription_data.billing_cycle == "yearly":
            price_id = plan.stripe_price_id_yearly
        else:
            price_id = plan.stripe_price_id_monthly
        
        # Create Stripe subscription
        stripe_subscription = StripeService.create_subscription(
            customer_id=stripe_customer.id,
            price_id=price_id,
            payment_method_id=subscription_data.payment_method_id
        )
        
        # Create database subscription record
        db_subscription = Subscription(
            user_id=current_user.id,
            stripe_customer_id=stripe_customer.id,
            stripe_subscription_id=stripe_subscription.id,
            tier=plan.id,
            status=stripe_subscription.status,
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
            monthly_scan_limit=plan.scan_limit,
            scans_used_this_month=0,
            last_reset_date=datetime.utcnow()
        )
        
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
        
        # Update user tier
        current_user.tier = plan.id
        db.commit()
        
        return db_subscription
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    return subscription


@router.post("/cancel")
async def cancel_subscription(
    at_period_end: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel current subscription."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status.in_(["active", "trialing"])
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    try:
        # Cancel Stripe subscription
        StripeService.cancel_subscription(
            subscription.stripe_subscription_id,
            at_period_end=at_period_end
        )
        
        # Update database
        subscription.cancel_at_period_end = at_period_end
        if not at_period_end:
            subscription.status = "canceled"
        
        db.commit()
        
        return {"message": "Subscription cancelled successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.get("/billing", response_model=BillingInfo)
async def get_billing_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get billing information for current user."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    try:
        # Get Stripe customer and subscription details
        stripe_customer = StripeService.get_customer(subscription.stripe_customer_id)
        stripe_subscription = StripeService.get_subscription(subscription.stripe_subscription_id)
        
        # Get plan details
        plan = StripeService.get_plan(subscription.tier)
        
        return BillingInfo(
            subscription=subscription,
            next_billing_date=subscription.current_period_end,
            amount_due=plan.price_monthly if plan else 0,
            currency="usd"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get billing info: {str(e)}"
        )


@router.get("/payment-methods", response_model=List[PaymentMethod])
async def get_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's payment methods."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    try:
        payment_methods = StripeService.get_payment_methods(subscription.stripe_customer_id)
        
        return [
            PaymentMethod(
                id=pm.id,
                type=pm.type,
                last4=pm.card.last4,
                brand=pm.card.brand,
                exp_month=pm.card.exp_month,
                exp_year=pm.card.exp_year,
                is_default=pm.id == subscription.stripe_customer_id
            )
            for pm in payment_methods
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get payment methods: {str(e)}"
        )


@router.get("/invoices", response_model=List[Invoice])
async def get_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get user's invoices."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    try:
        invoices = StripeService.get_invoices(subscription.stripe_customer_id, limit)
        
        return [
            Invoice(
                id=invoice.id,
                amount_paid=invoice.amount_paid,
                amount_due=invoice.amount_due,
                currency=invoice.currency,
                status=invoice.status,
                created=datetime.fromtimestamp(invoice.created),
                due_date=datetime.fromtimestamp(invoice.due_date) if invoice.due_date else None,
                invoice_pdf=invoice.invoice_pdf
            )
            for invoice in invoices
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get invoices: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header"
        )
    
    try:
        # Verify webhook signature
        event = StripeService.construct_webhook_event(payload, sig_header)
        
        # Handle the event
        result = StripeService.handle_webhook_event(event)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}"
        )
