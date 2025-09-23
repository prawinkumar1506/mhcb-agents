# from database.mongodb import get_database
# from models.schemas import User, Expert, Helpline, Conversation, BookingRequest, AssessmentResult
# from typing import List, Optional, Dict, Any
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# class UserCollection:
#     @staticmethod
#     async def create_user(user: User) -> bool:
#         """Create a new user"""
#         try:
#             db = await get_database()
#             result = await db.users.insert_one(user.model_dump())
#             return result.inserted_id is not None
#         except Exception as e:
#             logger.error(f"Error creating user: {e}")
#             return False
    
#     @staticmethod
#     async def get_user(user_id: str) -> Optional[User]:
#         """Get user by ID"""
#         try:
#             db = await get_database()
#             user_data = await db.users.find_one({"user_id": user_id})
#             return User(**user_data) if user_data else None
#         except Exception as e:
#             logger.error(f"Error getting user: {e}")
#             return None
    
#     @staticmethod
#     async def update_user_history(user_id: str, tags: List[str]) -> bool:
#         """Update user's conversation history tags"""
#         try:
#             db = await get_database()
#             result = await db.users.update_one(
#                 {"user_id": user_id},
#                 {
#                     "$addToSet": {"history": {"$each": tags}},
#                     "$set": {"last_session": datetime.utcnow()}
#                 }
#             )
#             return result.modified_count > 0
#         except Exception as e:
#             logger.error(f"Error updating user history: {e}")
#             return False

# class ConversationCollection:
#     @staticmethod
#     async def create_conversation(conversation: Conversation) -> bool:
#         """Create a new conversation"""
#         try:
#             db = await get_database()
#             result = await db.conversations.insert_one(conversation.model_dump())
#             return result.inserted_id is not None
#         except Exception as e:
#             logger.error(f"Error creating conversation: {e}")
#             return False
    
#     @staticmethod
#     async def get_user_conversations(user_id: str, limit: int = 10) -> List[Conversation]:
#         """Get user's recent conversations"""
#         try:
#             db = await get_database()
#             cursor = db.conversations.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
#             conversations = []
#             async for doc in cursor:
#                 conversations.append(Conversation(**doc))
#             return conversations
#         except Exception as e:
#             logger.error(f"Error getting conversations: {e}")
#             return []
    
#     @staticmethod
#     async def update_conversation(conversation_id: str, messages: List[Dict], tags: List[str]) -> bool:
#         """Update conversation with new messages and tags"""
#         try:
#             db = await get_database()
#             result = await db.conversations.update_one(
#                 {"conversation_id": conversation_id},
#                 {
#                     "$set": {
#                         "messages": messages,
#                         "detected_tags": tags,
#                         "updated_at": datetime.utcnow()
#                     }
#                 }
#             )
#             return result.modified_count > 0
#         except Exception as e:
#             logger.error(f"Error updating conversation: {e}")
#             return False

# class ExpertCollection:
#     @staticmethod
#     async def get_available_experts(tags: List[str] = None) -> List[Expert]:
#         """Get available experts, optionally filtered by tags"""
#         try:
#             db = await get_database()
#             query = {"availability": True}
#             if tags:
#                 query["tags"] = {"$in": tags}
            
#             cursor = db.experts.find(query)
#             experts = []
#             async for doc in cursor:
#                 experts.append(Expert(**doc))
#             return experts
#         except Exception as e:
#             logger.error(f"Error getting experts: {e}")
#             return []

# class HelplineCollection:
#     @staticmethod
#     async def get_helplines(region: str = "India") -> List[Helpline]:
#         """Get helpline numbers for a region"""
#         try:
#             db = await get_database()
#             cursor = db.helplines.find({"region": region})
#             helplines = []
#             async for doc in cursor:
#                 helplines.append(Helpline(**doc))
#             return helplines
#         except Exception as e:
#             logger.error(f"Error getting helplines: {e}")
#             return []

# class BookingCollection:
#     @staticmethod
#     async def create_booking(booking: BookingRequest) -> bool:
#         """Create a new booking request"""
#         try:
#             db = await get_database()
#             booking_data = booking.model_dump()
#             booking_data["created_at"] = datetime.utcnow()
#             booking_data["status"] = "pending"
#             result = await db.bookings.insert_one(booking_data)
#             return result.inserted_id is not None
#         except Exception as e:
#             logger.error(f"Error creating booking: {e}")
#             return False
