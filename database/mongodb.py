# from motor.motor_asyncio import AsyncIOMotorClient
# from config.settings import settings
# import logging

# logger = logging.getLogger(__name__)

# class MongoDB:
#     client: AsyncIOMotorClient = None
#     database = None

# mongodb = MongoDB()

# async def init_db():
#     """Initialize MongoDB connection"""
#     try:
#         mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
#         mongodb.database = mongodb.client[settings.DATABASE_NAME]
        
#         # Test connection
#         await mongodb.client.admin.command('ping')
#         logger.info("Successfully connected to MongoDB")
        
#         # Create indexes for better performance
#         await create_indexes()
        
#     except Exception as e:
#         logger.error(f"Failed to connect to MongoDB: {e}")
#         raise

# async def create_indexes():
#     """Create database indexes for better performance"""
#     try:
#         # Users collection indexes
#         await mongodb.database.users.create_index("user_id", unique=True)
        
#         # Conversations collection indexes
#         await mongodb.database.conversations.create_index("user_id")
#         await mongodb.database.conversations.create_index("created_at")
        
#         # Experts collection indexes
#         await mongodb.database.experts.create_index("expert_id", unique=True)
#         await mongodb.database.experts.create_index("tags")
        
#         logger.info("Database indexes created successfully")
        
#     except Exception as e:
#         logger.error(f"Failed to create indexes: {e}")

# async def get_database():
#     """Get database instance"""
#     return mongodb.database

# async def close_db():
#     """Close database connection"""
#     if mongodb.client:
#         mongodb.client.close()
#         logger.info("MongoDB connection closed")
