from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreateModel(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponseModel(BaseModel):
    id: str
    email: EmailStr
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)