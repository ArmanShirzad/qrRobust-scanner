"""Pydantic schemas for subscription management."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SubscriptionPlan(BaseModel):
    """Schema for subscription plan."""
    id: str
    name: str
    description: str
    price_monthly: int  # Price in cents
    price_yearly: int  # Price in cents
    scan_limit: int
    features: List[str]
    stripe_price_id_monthly: str
    stripe_price_id_yearly: str


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription."""
    plan_id: str
    billing_cycle: str  # "monthly" or "yearly"
    payment_method_id: str


class SubscriptionResponse(BaseModel):
    """Schema for subscription response."""
    id: int
    user_id: int
    tier: str
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    monthly_scan_limit: int
    scans_used_this_month: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class BillingInfo(BaseModel):
    """Schema for billing information."""
    subscription: SubscriptionResponse
    next_billing_date: Optional[datetime]
    amount_due: Optional[int]
    currency: str = "usd"


class PaymentMethod(BaseModel):
    """Schema for payment method."""
    id: str
    type: str
    last4: str
    brand: str
    exp_month: int
    exp_year: int
    is_default: bool


class Invoice(BaseModel):
    """Schema for invoice."""
    id: str
    amount_paid: int
    amount_due: int
    currency: str
    status: str
    created: datetime
    due_date: Optional[datetime]
    invoice_pdf: Optional[str]


class WebhookEvent(BaseModel):
    """Schema for Stripe webhook events."""
    id: str
    type: str
    data: dict
