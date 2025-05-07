from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if isinstance(v, ObjectId):
            return str(v)
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str
    password_hash: str
    role: str = "user"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    tickets: dict[PyObjectId, str] = Field(default_factory=dict)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True 

class Event(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    description: str
    type: str
    location:str
    date: datetime
    created_at: datetime
    general_price: float
    vip_price: float
    general_attendee_ids: list[PyObjectId] = Field(default_factory=list)
    vip_attendee_ids: list[PyObjectId] = Field(default_factory=list)

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
