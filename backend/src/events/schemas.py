from datetime import datetime
from pydantic import BaseModel
from typing import List, Literal
from src.db.models import Event

class EventCreateModel(BaseModel):
    name: str
    description: str
    type: str
    location: str
    date: datetime
    general_price: float
    vip_price: float
    
class RegistrationRequest(BaseModel):
    event_id: str
    type: Literal["General", "VIP"]
    
