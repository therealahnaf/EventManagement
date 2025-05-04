from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from src.auth.dependencies import AccessTokenFromCookie, RoleChecker
from src.events.service import EventService
from src.db.main import get_db
from src.db.models import Event
from .schemas import EventCreateModel

from motor.motor_asyncio import AsyncIOMotorDatabase

events_router = APIRouter()

role_checker = RoleChecker(["admin", "user"])

@events_router.get("/events", dependencies=[Depends(role_checker)])
async def get_all_events(
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    event_service = EventService(db)
    return await event_service.get_all_events()

@events_router.post("/create-event", dependencies=[Depends(RoleChecker(["admin"]))])
async def create_event(
    event_data: EventCreateModel,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    event_service = EventService(db)
    return await event_service.create_event(event_data)
    
