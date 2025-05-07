from datetime import datetime
import uuid

from fastapi import HTTPException
from .schemas import EventCreateModel
from src.db.models import Event, User
from .utils import TicketService
from bson import ObjectId
from src.auth.service import UserService

class EventService:
    def __init__(self, db):
        self.db = db
        self.events = db["events"]  # MongoDB collection
        print("Event collection initialized")

    async def get_all_events(self, filters: dict = {}):
        events = await self.events.find(filters).to_list(length=10)

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

    async def attend_event(self, event_id: str, user_id: str, first_name: str, last_name: str, ticket_type: str):
        user_service = UserService(self.db)
        user = await user_service.get_user_by_id(user_id)
        print("Found user")
        event = await self.events.find_one({"_id": ObjectId(event_id)})
        print("Found event")
        ticket_token = await self._generate_ticket(event_id, user_id, first_name, last_name, ticket_type)
        print("Ticket generated")
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if ticket_type == "General":
            event["general_attendee_ids"].append(ObjectId(user_id))
        elif ticket_type == "VIP":
            event["vip_attendee_ids"].append(ObjectId(user_id))
        else:
            raise HTTPException(status_code=400, detail="Invalid ticket type")
        
        user.tickets[event_id] = ticket_token
        await user_service.update_user(user, user.model_dump())
        await self.events.update_one({"_id": ObjectId(event_id)}, {"$set": event})
        return Event(**event)
    
    async def update_event(self, event_id: str, event_data: EventCreateModel):
        event_dict = event_data.model_dump()
        event_dict["updated_at"] = datetime.now()
        await self.events.update_one({"_id": ObjectId(event_id)}, {"$set": event_dict})
        return Event(**event_dict)
    
    async def delete_event(self, event_id: str):
        await self.events.delete_one({"_id": ObjectId(event_id)})
        return {"message": "Event deleted successfully"}
    
    async def _generate_ticket(self, event_id: str, user_id: str, first_name: str, last_name: str, ticket_type: str):
        ticket_id = str(uuid.uuid4())
        event = await self.get_event_by_id(event_id)
        ticket_data = {
            "ticket_id": ticket_id,
            "event_id": event_id,
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "ticket_type": ticket_type,
            "event_name": event.name,
            "event_date": event.date,
            "event_location": event.location
        }
        ticket_generator = TicketService()
        token = ticket_generator.generate_ticket_token(ticket_data)
        return token
