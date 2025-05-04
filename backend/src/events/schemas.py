from datetime import datetime
from pydantic import BaseModel
from typing import List
from src.db.models import Event

class EventCreateModel(BaseModel):
    name: str
    description: str
    type: str
    location: str
    date: datetime
    price: float
    
    
