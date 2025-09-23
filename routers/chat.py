"""
Chat router for handling conversation endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatRequest, ChatResponse, ChatMessage, MessageRole
from services.gemini_service import gemini_service
from services.language_service import language_service
from services.conversation_flow import conversation_flow_service
from services.timetable_service import get_available_counselling_slots
from routers.booking import send_confirmation, send_reminder, bookings # Import bookings for session state
# from database.collections import UserCollection, ConversationCollection, HelplineCollection
from typing import Dict, List, Optional,Any
import uuid
from datetime import datetime, timedelta # Added timedelta for reminder scheduling
import logging
import re # For intent detection

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory session state for booking flow
# Stores {user_id: {"state": "awaiting_slot_selection" | "awaiting_confirmation", "available_slots": {...}, "selected_slot": "YYYY-MM-DD HH:MM"}}
booking_sessions: Dict[str, Dict[str, Any]] = {}

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Process user message using conversation flow service, including booking logic.
    """
    user_id = request.user_id
    user_message = request.message.lower()
    session_id = request.session_id or str(uuid.uuid4())

    # Check if user is in a booking flow
    if user_id in booking_sessions:
        session_state = booking_sessions[user_id]

        if session_state["state"] == "awaiting_slot_selection":
            # User is expected to select a slot (e.g., "book Monday 8:00")
            match = re.search(r"book (\w+) (\d{1,2}:\d{2})", user_message)
            if match:
                day_name = match.group(1).capitalize()
                time_str = match.group(2)
                
                # Find the full slot string from available slots
                selected_full_slot = None
                for date_str, times in session_state["available_slots"].items():
                    for t in times:
                        if day_name in datetime.strptime(date_str, "%Y-%m-%d").strftime("%A") and t.startswith(time_str):
                            selected_full_slot = f"{date_str} {t.split(' - ')[0]}"
                            break
                    if selected_full_slot:
                        break

                if selected_full_slot:
                    session_state["selected_slot"] = selected_full_slot
                    session_state["state"] = "awaiting_confirmation"
                    return ChatResponse(
                        response=f"You selected: {selected_full_slot}. Are you interested in booking this slot? (Yes/No)",
                        agent_type="booking_agent",
                        detected_tags=["booking"],
                        escalation_needed=False,
                        session_id=session_id
                    )
                else:
                    return ChatResponse(
                        response="I couldn't find that specific slot. Please choose from the available options or say 'no' to see other options.",
                        agent_type="booking_agent",
                        detected_tags=["booking"],
                        escalation_needed=False,
                        session_id=session_id
                    )
            elif "no" in user_message or "cancel" in user_message:
                del booking_sessions[user_id]
                return ChatResponse(
                    response="No problem. Would you like to see other available slots or try a different day?",
                    agent_type="booking_agent",
                    detected_tags=["booking"],
                    escalation_needed=False,
                    session_id=session_id
                )
            else:
                return ChatResponse(
                    response="Please select a slot by saying 'book [Day] [Time]' or say 'no' to cancel.",
                    agent_type="booking_agent",
                    detected_tags=["booking"],
                    escalation_needed=False,
                    session_id=session_id
                )

        elif session_state["state"] == "awaiting_confirmation":
            if "yes" in user_message:
                selected_slot = session_state["selected_slot"]
                student_email = "prawin2310095@ssn.edu.in" # Placeholder email

                try:
                    await send_confirmation(student_email, selected_slot)
                    # Schedule a reminder (e.g., 15 minutes before the session)
                    reminder_time = datetime.strptime(selected_slot, "%Y-%m-%d %H:%M") - timedelta(minutes=15)
                    # For demo, schedule 1 minute from now if session is in the future
                    if reminder_time < datetime.now():
                        reminder_time = datetime.now() + timedelta(minutes=1)
                    
                    await send_reminder(student_email, selected_slot) # Mock scheduling
                    
                    del booking_sessions[user_id]
                    return ChatResponse(
                        response=f"Booking confirmed for {selected_slot}. A confirmation email has been sent to {student_email}.",
                        agent_type="booking_agent",
                        detected_tags=["booking", "confirmed"],
                        escalation_needed=False,
                        session_id=session_id
                    )
                except Exception as e:
                    logger.exception("Failed to send confirmation email")
                    return ChatResponse(
                        response=f"Failed to confirm booking due to an email error. Please try again later. Error: {e}",
                        agent_type="booking_agent",
                        detected_tags=["booking", "error"],
                        escalation_needed=False,
                        session_id=session_id
                    )
            elif "no" in user_message or "cancel" in user_message:
                del booking_sessions[user_id]
                return ChatResponse(
                    response="No problem. Would you like to see other available slots or try a different day?",
                    agent_type="booking_agent",
                    detected_tags=["booking"],
                    escalation_needed=False,
                    session_id=session_id
                )
            else:
                return ChatResponse(
                    response="Please say 'yes' to confirm or 'no' to cancel the booking.",
                    agent_type="booking_agent",
                    detected_tags=["booking"],
                    escalation_needed=False,
                    session_id=session_id
                )

    # Detect booking intent
    booking_keywords = ["book", "appointment", "counselor", "session", "schedule"]
    if any(keyword in user_message for keyword in booking_keywords):
        available_slots = get_available_counselling_slots()
        if available_slots:
            response_message = "Here are some available slots with Dr. Nanda Ma'am:\n"
            for date, times in available_slots.items():
                response_message += f"\n**{date}**:\n"
                for time_slot in times:
                    response_message += f"- {time_slot}\n"
            response_message += "\nWhich slot would you like to book? Please say 'book [Day] [Time]' (e.g., 'book Monday 8:00')."
            
            booking_sessions[user_id] = {
                "state": "awaiting_slot_selection",
                "available_slots": available_slots,
                "selected_slot": None
            }
            return ChatResponse(
                response=response_message,
                agent_type="booking_agent",
                detected_tags=["booking"],
                escalation_needed=False,
                session_id=session_id
            )
        else:
            return ChatResponse(
                response="I couldn't find any available slots with Dr. Nanda Ma'am at this time. Would you like to try again later or explore other options?",
                agent_type="booking_agent",
                detected_tags=["booking"],
                escalation_needed=False,
                session_id=session_id
            )

    try:
        # Process message through conversation flow if no booking intent
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
    # helplines = await HelplineCollection.get_helplines(region="India")  # Default to India, can be made dynamic
    # helpline_dict = {helpline.issue: helpline.number for helpline in helplines}
    # Mock helplines since MongoDB is commented out
    helpline_dict = {
        "Suicidal Thoughts": "+91-9152987821",
        "Mental Health Crisis": "1075"
    }
    
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
        
        # await ConversationCollection.create_conversation(conversation)
        
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
        # conversations = await ConversationCollection.get_user_conversations(user_id, limit)
        # Mock empty list since MongoDB is commented out
        conversations = []
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
