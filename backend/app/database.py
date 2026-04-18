# app/database.py
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger(__name__)

# Global client and db references
client: AsyncIOMotorClient = None
db = None


async def connect_db():
    """Connect to MongoDB Atlas and initialise collections."""
    global client, db

    try:
        client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000
        )

        db = client[settings.mongodb_db_name]

        # Verify connection
        await client.admin.command("ping")
        logger.info("✅ MongoDB connected successfully")

        # Create indexes
        await create_indexes()

    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise


async def close_db():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


async def create_indexes():
    """Create all required indexes."""
    global db

    # TTL index on drug_cache — auto-expires after 7 days
    await db.drug_cache.create_index(
        "cached_at",
        expireAfterSeconds=settings.cache_ttl_days * 24 * 3600
    )

    # Index on medication_checks for fast user queries
    await db.medication_checks.create_index("user_id")
    await db.medication_checks.create_index("session_id")

    # Unique index on drug_cache pair key
    await db.drug_cache.create_index(
        "pair_key",
        unique=True,
        sparse=True
    )

    # Index on interaction_results for check_id lookup
    await db.interaction_results.create_index("check_id")

    logger.info("✅ MongoDB indexes created")


def get_db():
    """Return the database instance."""
    return db