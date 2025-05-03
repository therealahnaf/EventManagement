from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.config import Config

# Create MongoDB client
client = AsyncIOMotorClient(Config.DATABASE_URL)
db: AsyncIOMotorDatabase = client["event_management_db"]

async def get_db() -> AsyncIOMotorDatabase:
    return db
