from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging
import time

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""
    
    client: AsyncIOMotorClient = None
    
    async def connect_to_mongo(self):
        """Create database connection"""
        try:
            # Configure connection pooling
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=50,  # Maximum connections in pool
                minPoolSize=10,  # Minimum connections in pool
                maxIdleTimeMS=30000,  # Close idle connections after 30s
                serverSelectionTimeoutMS=5000,  # 5s timeout for server selection
                connectTimeoutMS=10000,  # 10s connection timeout
                socketTimeoutMS=20000,  # 20s socket timeout
            )
            logger.info("Connected to MongoDB with connection pooling")
            
            # Test connection performance
            start_time = time.time()
            await self.client.admin.command('ping')
            ping_time = time.time() - start_time
            logger.info(f"MongoDB ping time: {ping_time:.3f}s")
            
            # Initialize Beanie with the database
            await init_beanie(
                database=self.client[settings.DATABASE_NAME],
                document_models=[
                    # Import models
                    "app.models.candidate.Candidate",
                    "app.models.job.Job",
                    "app.models.auth.User",
                    "app.models.application.Application"
                ]
            )
            logger.info("Beanie initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def close_mongo_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Create database instance
db = Database()


async def init_db():
    """Initialize database connection"""
    await db.connect_to_mongo()


async def close_db():
    """Close database connection"""
    await db.close_mongo_connection() 