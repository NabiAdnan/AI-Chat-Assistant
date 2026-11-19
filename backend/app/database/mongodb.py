import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import settings

logger = logging.getLogger("nexus_ai.database")


class MongoDBManager:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


db_manager = MongoDBManager()


async def connect_to_mongo() -> None:
    """Initialize asynchronous connection to MongoDB and ensure indexes."""
    try:
        logger.info("Connecting to MongoDB at %s...", settings.MONGODB_URI)
        db_manager.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
        )
        # Verify connection by pinging
        await db_manager.client.admin.command("ping")
        db_manager.db = db_manager.client[settings.DATABASE_NAME]
        logger.info("Connected to MongoDB database: %s", settings.DATABASE_NAME)

        # Create indexes
        conversations_col = db_manager.db["conversations"]
        await conversations_col.create_index([("updated_at", DESCENDING)])
        logger.info("Ensured index on 'conversations.updated_at' (DESCENDING).")
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        logger.error("Failed to connect to MongoDB: %s", exc)
        raise exc
    except Exception as exc:
        logger.error("Unexpected error during MongoDB connection: %s", exc)
        raise exc


async def close_mongo_connection() -> None:
    """Close MongoDB connection pool."""
    if db_manager.client:
        logger.info("Closing MongoDB connection...")
        db_manager.client.close()
        db_manager.client = None
        db_manager.db = None
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """Return the active MongoDB database instance."""
    if db_manager.db is None:
        raise RuntimeError("Database connection has not been initialized.")
    return db_manager.db


def get_conversations_collection():
    """Return the conversations collection."""
    db = get_database()
    return db["conversations"]
