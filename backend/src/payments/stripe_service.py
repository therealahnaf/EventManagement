import stripe
from fastapi import HTTPException
from src.config import Config

class StripeService:
    def __init__(self):
        stripe.api_key = Config.STRIPE_SECRET_KEY

    def create_checkout_session(self, user_email: str, amount: int, event_name: str, ticket_type: str, metadata: dict):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"{ticket_type} Ticket for Event {event_name}",
                            },
                            "unit_amount": int(amount * 100),  # amount in cents
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                customer_email=user_email,
                success_url = f"http://localhost:8000/api/v1/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url="http://localhost:3000/cancel",
                metadata=metadata
            )

            return session.url
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
