import stripe
from fastapi import APIRouter, Request, Depends, HTTPException
from src.db.main import get_db
from src.events.service import EventService
from src.config import Config

payments_router = APIRouter()

@payments_router.get("/success")
async def payment_success(session_id: str, db=Depends(get_db)):
    try:
        stripe.api_key = Config.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)

        metadata = session.get("metadata", {})
        user_email = metadata.get("user_email")
        user_id = metadata.get("user_id")
        event_id = metadata.get("event_id")
        ticket_type = metadata.get("ticket_type")

        if not (user_email and event_id):
            raise HTTPException(status_code=400, detail="Missing metadata")

        event_service = EventService(db)
        await event_service.attend_event(event_id, user_id=user_id, ticket_type=ticket_type)

        return {"status": "success", "message": "Registration completed."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))