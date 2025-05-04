from datetime import datetime

from fastapi import HTTPException
from .schemas import EventCreateModel
from src.db.models import Event, User
from bson import ObjectId

class EventService:
    def __init__(self, db):
        self.db = db
        self.events = db["events"]  # MongoDB collection
        print("Event collection initialized")

    async def get_all_events(self):
        events = await self.events.find().to_list(length=10)

        return [Event(**event) for event in events]
    
    async def create_event(self, event_data: EventCreateModel):
        event_dict = event_data.model_dump()
        event_dict["created_at"] = datetime.now()
        event_dict["general_attendee_ids"] = []
        event_dict["vip_attendee_ids"] = []

        result = await self.events.insert_one(event_dict)
        event_dict["_id"] = result.inserted_id

        return Event(**event_dict)
    
    async def get_event_by_id(self, event_id: str):
        event = await self.events.find_one({"_id": ObjectId(event_id)})
        return Event(**event)

    async def attend_event(self, event_id: str, user_id: str, ticket_type: str):
        event = await self.events.find_one({"_id": ObjectId(event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if ticket_type == "General":
            event["general_attendee_ids"].append(ObjectId(user_id))
        elif ticket_type == "VIP":
            event["vip_attendee_ids"].append(ObjectId(user_id))
        else:
            raise HTTPException(status_code=400, detail="Invalid ticket type")

        await self.events.update_one({"_id": ObjectId(event_id)}, {"$set": event})
        return Event(**event)
