"""Stripe service for payment processing and subscription management."""

import stripe
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.schemas.subscriptions import SubscriptionPlan

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


class StripeService:
    """Service for handling Stripe operations."""
    
    # Subscription plans configuration
    PLANS = {
        "free": SubscriptionPlan(
            id="free",
            name="Free",
            description="Basic QR code scanning",
            price_monthly=0,
            price_yearly=0,
            scan_limit=100,
            features=["100 scans/month", "Basic analytics", "Standard support"],
            stripe_price_id_monthly="",
            stripe_price_id_yearly=""
        ),
        "pro": SubscriptionPlan(
            id="pro",
            name="Pro",
            description="Advanced features for professionals",
            price_monthly=900,  # $9.00
            price_yearly=9000,   # $90.00 (2 months free)
            scan_limit=10000,
            features=["10,000 scans/month", "Advanced analytics", "Custom QR designs", "Priority support"],
            stripe_price_id_monthly="price_pro_monthly",  # TODO: Replace with actual Stripe price IDs
            stripe_price_id_yearly="price_pro_yearly"
        ),
        "business": SubscriptionPlan(
            id="business",
            name="Business",
            description="Perfect for growing businesses",
            price_monthly=2900,  # $29.00
            price_yearly=29000,  # $290.00 (2 months free)
            scan_limit=50000,
            features=["50,000 scans/month", "API access", "Dynamic QR codes", "Team management", "White-label options"],
            stripe_price_id_monthly="price_business_monthly",
            stripe_price_id_yearly="price_business_yearly"
        ),
        "enterprise": SubscriptionPlan(
            id="enterprise",
            name="Enterprise",
            description="Custom solutions for large organizations",
            price_monthly=9900,  # $99.00
            price_yearly=99000,  # $990.00 (2 months free)
            scan_limit=999999,  # Effectively unlimited
            features=["Unlimited scans", "Custom integrations", "Dedicated support", "SLA guarantee", "On-premise deployment"],
            stripe_price_id_monthly="price_enterprise_monthly",
            stripe_price_id_yearly="price_enterprise_yearly"
        )
    }
    
    @classmethod
    def get_plans(cls) -> List[SubscriptionPlan]:
        """Get all available subscription plans."""
        return list(cls.PLANS.values())
    
    @classmethod
    def get_plan(cls, plan_id: str) -> Optional[SubscriptionPlan]:
        """Get a specific subscription plan."""
        return cls.PLANS.get(plan_id)
    
    @classmethod
    def create_customer(cls, email: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Create a Stripe customer."""
        customer_data = {
            "email": email,
        }
        if name:
            customer_data["name"] = name
            
        return stripe.Customer.create(**customer_data)
    
    @classmethod
    def create_subscription(
        cls, 
        customer_id: str, 
        price_id: str, 
        payment_method_id: str
    ) -> Dict[str, Any]:
        """Create a Stripe subscription."""
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            default_payment_method=payment_method_id,
            expand=["latest_invoice.payment_intent"]
        )
    
    @classmethod
    def cancel_subscription(cls, subscription_id: str, at_period_end: bool = True) -> Dict[str, Any]:
        """Cancel a Stripe subscription."""
        if at_period_end:
            return stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        else:
            return stripe.Subscription.delete(subscription_id)
    
    @classmethod
    def get_subscription(cls, subscription_id: str) -> Dict[str, Any]:
        """Get a Stripe subscription."""
        return stripe.Subscription.retrieve(subscription_id)
    
    @classmethod
    def get_customer(cls, customer_id: str) -> Dict[str, Any]:
        """Get a Stripe customer."""
        return stripe.Customer.retrieve(customer_id)
    
    @classmethod
    def get_payment_methods(cls, customer_id: str) -> List[Dict[str, Any]]:
        """Get customer payment methods."""
        return stripe.PaymentMethod.list(
            customer=customer_id,
            type="card"
        ).data
    
    @classmethod
    def get_invoices(cls, customer_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get customer invoices."""
        return stripe.Invoice.list(
            customer=customer_id,
            limit=limit
        ).data
    
    @classmethod
    def create_payment_intent(
        cls, 
        amount: int, 
        currency: str = "usd", 
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a payment intent for one-time payments."""
        intent_data = {
            "amount": amount,
            "currency": currency,
        }
        if customer_id:
            intent_data["customer"] = customer_id
            
        return stripe.PaymentIntent.create(**intent_data)
    
    @classmethod
    def construct_webhook_event(cls, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Construct webhook event from payload and signature."""
        return stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    
    @classmethod
    def handle_webhook_event(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Stripe webhook events."""
        event_type = event["type"]
        
        handlers = {
            "customer.subscription.created": cls._handle_subscription_created,
            "customer.subscription.updated": cls._handle_subscription_updated,
            "customer.subscription.deleted": cls._handle_subscription_deleted,
            "invoice.payment_succeeded": cls._handle_payment_succeeded,
            "invoice.payment_failed": cls._handle_payment_failed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return handler(event)
        
        return {"status": "ignored", "event_type": event_type}
    
    @classmethod
    def _handle_subscription_created(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription created event."""
        # TODO: Update database with new subscription
        return {"status": "processed", "action": "subscription_created"}
    
    @classmethod
    def _handle_subscription_updated(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updated event."""
        # TODO: Update database with subscription changes
        return {"status": "processed", "action": "subscription_updated"}
    
    @classmethod
    def _handle_subscription_deleted(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription deleted event."""
        # TODO: Update database to mark subscription as cancelled
        return {"status": "processed", "action": "subscription_deleted"}
    
    @classmethod
    def _handle_payment_succeeded(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment event."""
        # TODO: Update database with successful payment
        return {"status": "processed", "action": "payment_succeeded"}
    
    @classmethod
    def _handle_payment_failed(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment event."""
        # TODO: Handle failed payment (notify user, etc.)
        return {"status": "processed", "action": "payment_failed"}
