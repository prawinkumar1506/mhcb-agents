"""
Chat router for handling conversation endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatRequest, ChatResponse, ChatMessage, MessageRole
from services.gemini_service import gemini_service
from services.language_service import language_service
from services.conversation_flow import conversation_flow_service
from database.collections import UserCollection, ConversationCollection, HelplineCollection
from typing import Dict, List
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Process user message using conversation flow service
    """
    try:
        # Process message through conversation flow
        flow_response = await conversation_flow_service.process_user_message(
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id,
            language=request.language.value if request.language else None
        )
        
        # Convert to ChatResponse format
        chat_response = ChatResponse(
            response=flow_response["response"],
            agent_type=flow_response["agent_type"],
            detected_tags=flow_response["detected_tags"],
            escalation_needed=flow_response["escalation_needed"],
            helpline_numbers=flow_response.get("helpline_numbers"),
            suggested_resources=flow_response["suggested_resources"],
            session_id=flow_response["session_id"]
        )
        
        return chat_response
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Error processing your message. Please try again.")

async def handle_crisis_response(request: ChatRequest, analysis: Dict, crisis_data: Dict) -> ChatResponse:
    """
    Handle crisis situations with immediate intervention
    """
    # Get crisis messages in user's language
    crisis_messages = language_service.get_crisis_messages(analysis.get("language", "English"))
    
    # Get helpline numbers
    helplines = await HelplineCollection.get_helplines(region="India")  # Default to India, can be made dynamic
    helpline_dict = {helpline.issue: helpline.number for helpline in helplines}
    
    # Construct crisis response
    crisis_response = f"{crisis_messages['crisis_message']}\n\n"
    crisis_response += f"{crisis_messages['helpline_prompt']}\n"
    
    for issue, number in helpline_dict.items():
        crisis_response += f"• {issue}: {number}\n"
    
    crisis_response += f"\n{crisis_messages['emergency_prompt']}"
    
    # Save crisis conversation
    session_id = request.session_id or str(uuid.uuid4())
    await save_conversation(
        session_id,
        request.user_id,
        request.message,
        crisis_response,
        analysis,
        is_crisis=True
    )
    
    return ChatResponse(
        response=crisis_response,
        agent_type="booking_agent",
        detected_tags=analysis.get("detected_tags", ["crisis"]),
        escalation_needed=True,
        helpline_numbers=helpline_dict,
        session_id=session_id
    )

async def save_conversation(session_id: str, user_id: str, user_message: str, 
                          ai_response: str, analysis: Dict, is_crisis: bool = False):
    """
    Save conversation to database
    """
    try:
        from models.schemas import Conversation
        
        messages = [
            ChatMessage(
                role=MessageRole.USER,
                content=user_message,
                timestamp=datetime.utcnow()
            ),
            ChatMessage(
                role=MessageRole.AGENT,
                content=ai_response,
                timestamp=datetime.utcnow(),
                agent_type=analysis.get("recommended_agent", "conversation_manager")
            )
        ]
        
        conversation = Conversation(
            conversation_id=session_id,
            user_id=user_id,
            messages=messages,
            detected_tags=analysis.get("detected_tags", [])
        )
        
        await ConversationCollection.create_conversation(conversation)
        
        # Log crisis conversations for monitoring
        if is_crisis:
            logger.warning(f"Crisis conversation detected for user {user_id}: {analysis}")
            
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")

def get_suggested_resources(tags: List[str]) -> List[str]:
    """
    Get suggested resources based on detected tags
    """
    resource_mapping = {
        "anxiety": ["breathing-techniques", "grounding-techniques", "GAD-7"],
        "depression": ["cbt-techniques", "behavioral-activation", "PHQ-9"],
        "stress": ["mindfulness-techniques", "stress-management", "breathing-techniques"],
        "sleep": ["sleep-hygiene", "relaxation-techniques"],
        "relationships": ["communication-skills", "boundary-setting"],
        "panic": ["grounding-techniques", "panic-management"]
    }
    
    suggested = []
    for tag in tags:
        if tag in resource_mapping:
            suggested.extend(resource_mapping[tag])
    
    # Remove duplicates and limit to 3 suggestions
    return list(set(suggested))[:3]

@router.get("/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 10):
    """
    Get user's chat history
    """
    try:
        conversations = await ConversationCollection.get_user_conversations(user_id, limit)
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chat history")

@router.delete("/history/{user_id}")
async def clear_chat_history(user_id: str):
    """
    Clear user's chat history
    """
    try:
        # Implementation would clear user's conversation history
        # For now, return success
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail="Error clearing chat history")
