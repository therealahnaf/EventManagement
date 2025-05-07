import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from src.db.models import User

from .schemas import UserCreateModel
from .utils import generate_passwd_hash
from src.events.utils import TicketService

class UserService:
    def __init__(self, db):
        self.db = db
        self.users = db["users"]  # MongoDB collection
        print("User collection initialized")

    async def get_user_by_email(self, email: str):
        print(f"Attempting to find user with email: {email}")
        user = await self.users.find_one({"email": email})
        if user:
            print(f"User found: {email}")
            return User(**user)
        print(f"No user found with email: {email}")
        return None
    
    async def get_user_by_id(self, user_id: str):
        user = await self.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(**user)
        return None
    
    async def save_user_ticket(self, user_id: str, event_id: str):
        user = await self.get_user_by_id(user_id)
        try:
            ticket_token = user.tickets[event_id]
            ticket_service = TicketService()
            ticket_pdf = ticket_service.generate_ticket_and_save(ticket_token)
            return ticket_pdf
        except Exception as e:
            raise

    async def user_exists(self, email: str):
        exists = await self.get_user_by_email(email) is not None
        return exists

    async def create_user(self, user_data: UserCreateModel):
        user_data_dict = user_data.model_dump()
        user_data_dict["password_hash"] = generate_passwd_hash(user_data_dict["password"])
        user_data_dict["role"] = "user"
        
        # Remove the password field as we only store the hash
        del user_data_dict["password"]
        
        try:
            print(user_data_dict)
            result = await self.users.insert_one(user_data_dict)
            user_data_dict["_id"] = result.inserted_id
            print(f"User created successfully: {user_data.email}")
            return User(**user_data_dict)
        except Exception as e:
            raise

    async def update_user(self, user: User, user_data: dict):
        # Convert user to dict, excluding _id
        user_dict = user.model_dump(exclude={"_id"})
        
        # Update the fields
        for k, v in user_data.items():
            if k != "password":  # Skip password field
                user_dict[k] = v
        
        # If password is being updated, hash it
        if "password" in user_data:
            user_dict["password_hash"] = generate_passwd_hash(user_data["password"])
        
        try:
            # Update in MongoDB
            await self.users.update_one(
                {"_id": ObjectId(user.id)},
                {"$set": user_dict}
            )
            
            # Return updated user
            updated_user = await self.users.find_one({"_id": ObjectId(user.id)})
            return User(**updated_user)
        except Exception as e:
            raise