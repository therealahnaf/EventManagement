from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, status, Query
from fastapi.exceptions import HTTPException

from src.auth.dependencies import AccessTokenFromCookie, RoleChecker, get_current_user_with_cookie
from src.events.service import EventService
from src.db.main import get_db
from src.db.models import Event, User
from src.payments.stripe_service import StripeService
from .schemas import EventCreateModel, RegistrationRequest

from motor.motor_asyncio import AsyncIOMotorDatabase

events_router = APIRouter()

role_checker = RoleChecker(["admin", "user"])

@events_router.get("/events", dependencies=[Depends(role_checker)])
async def get_all_events(
    db: AsyncIOMotorDatabase = Depends(get_db),
    type: Optional[str] = Query(None),
    date: Optional[datetime] = Query(None),
    location: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
):
    filters = {}

    if type:
        filters["type"] = type
    if date:
        filters["date"] = date
    if location:
        filters["location"] = location

    # Add a price range filter (checking both general and VIP prices)
    if min_price is not None or max_price is not None:
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price

        filters["$or"] = [
            {"general_price": price_filter},
            {"vip_price": price_filter}
        ]

    event_service = EventService(db)
    return await event_service.get_all_events(filters)

@events_router.post("/create-event", dependencies=[Depends(RoleChecker(["admin"]))])
async def create_event(
    event_data: EventCreateModel,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    event_service = EventService(db)
    return await event_service.create_event(event_data)

@events_router.get("/{event_id}", dependencies=[Depends(role_checker)])
async def get_event_by_id(
    event_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    event_service = EventService(db)
    return await event_service.get_event_by_id(event_id)

@events_router.post("/{event_id}/attend", dependencies=[Depends(role_checker)])
async def attend_event(
    request: RegistrationRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: User = Depends(get_current_user_with_cookie),
):
    event_service = EventService(db)
    event = await event_service.get_event_by_id(request.event_id)
    if request.type == "General":
        fee = event.general_price
    elif request.type == "VIP":
        fee = event.vip_price
    else:
        raise HTTPException(status_code=400, detail="Invalid ticket type")
    
    if fee == 0:
        return await event_service.attend_event(request.event_id, user.id, user.first_name, user.last_name, request.type)
    else:
        # Strip payment integration
        stripe_service = StripeService()
        checkout_url = stripe_service.create_checkout_session(
            user_email=user.email,
            amount=fee,
            event_name=event.name,
            ticket_type=request.type,
            metadata={
                "user_email": user.email,
                "user_id": user.id,
                "event_id": request.event_id,
                "ticket_type": request.type
            }
        )
        return {"checkout_url": checkout_url}

@events_router.get("/{user_id}/events/{event_id}/get-ticket")
async def get_ticket_by_user_id(
    user_id: str,
    event_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    event_service = EventService(db)
    return await event_service.get_ticket_by_user_id(user_id, event_id)

@events_router.put("/{event_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def update_event(
    event_id: str,
    event_data: EventCreateModel,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    event_service = EventService(db)
    return await event_service.update_event(event_id, event_data)

@events_router.delete("/{event_id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_event(
    event_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    event_service = EventService(db)
    return await event_service.delete_event(event_id)

