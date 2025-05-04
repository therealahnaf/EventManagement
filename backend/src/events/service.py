from datetime import datetime
from .schemas import EventCreateModel
from src.db.models import Event

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
        event_dict["attendee_ids"] = []

        result = await self.events.insert_one(event_dict)
        event_dict["_id"] = result.inserted_id

        return Event(**event_dict)
