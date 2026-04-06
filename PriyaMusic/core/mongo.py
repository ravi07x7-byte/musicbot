from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI
from ..logging import LOGGER

LOGGER(__name__).info("Connecting to MongoDB...")
try:
    _client = AsyncIOMotorClient(MONGO_DB_URI)
    mongodb = _client.PriyaMusic
    LOGGER(__name__).info("MongoDB connected.")
except Exception as e:
    LOGGER(__name__).error(f"MongoDB connection failed: {e}")
    exit(1)
