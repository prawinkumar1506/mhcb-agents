"""
Conversation Flow Service - Manages the complete conversation lifecycle
"""
from typing import Dict, List, Any, Optional, Tuple
from services.gemini_service import gemini_service
from services.language_service import language_service
from agents.agent_orchestrator import agent_orchestrator
# from database.collections import UserCollection, ConversationCollection, HelplineCollection
from models.schemas import User, ChatMessage, MessageRole, UserStyle, Language
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConversationFlowService:
    def __init__(self):
        self.session_memory = {}  # In-memory session storage
        self.max_conversation_history = 10
    
    async def process_user_message(self, 
                                 user_id: str, 
                                 message: str,
                                 session_id: Optional[str] = None,
                                 language: Optional[str] = None) -> Dict[str, Any]:
        """
        Main conversation processing pipeline
        """
        try:
            # Step 1: Initialize or retrieve session
            session_id = session_id or str(uuid.uuid4())
            session_context = await self._get_or_create_session(session_id, user_id)
            
            # Step 2: Get or create user profile
            # user = await self._get_or_create_user(user_id, language)
            # Mock user since MongoDB is commented out
            user = User(
                user_id=user_id,
                language=Language(language) if language else Language.ENGLISH,
                preferred_style=UserStyle.EMPATHETIC,
                history=[]
            )
            
            # Step 3: Detect language and update if needed
            detected_language = language_service.detect_language(message)
            if detected_language != user.language.value:
                user.language = Language(detected_language)
                # await UserCollection.update_user_history(user_id, [])  # Trigger user update
            
            # Step 4: Analyze message intent and emotion
            analysis = await gemini_service.analyze_intent_and_emotion(
                message, user.history
            )
            
            # Step 5: Check for crisis situation
            is_crisis, crisis_data = await gemini_service.detect_crisis_situation(message)
            
            if is_crisis:
                return await self._handle_crisis_flow(
                    user_id, message, session_id, analysis, crisis_data, user
                )
            
            # Step 6: Update session context with analysis
            session_context.update({
                "last_message": message,
                "last_analysis": analysis,
                "conversation_turn": session_context.get("conversation_turn", 0) + 1
            })
            
            # Step 7: Determine conversation stage
            conversation_stage = self._determine_conversation_stage(session_context, analysis)
            
            # Step 8: Process with appropriate flow
            if conversation_stage == "greeting":
                response_data = await self._handle_greeting_flow(user, message, analysis, session_context)
            elif conversation_stage == "assessment":
                response_data = await self._handle_assessment_flow(user, message, analysis, session_context)
            elif conversation_stage == "intervention":
                response_data = await self._handle_intervention_flow(user, message, analysis, session_context)
            elif conversation_stage == "follow_up":
                response_data = await self._handle_follow_up_flow(user, message, analysis, session_context)
            else:
                response_data = await self._handle_general_flow(user, message, analysis, session_context)
            
            # Step 9: Update conversation history
            await self._update_conversation_history(
                session_id, user_id, message, response_data["response"], analysis
            )
            
            # Step 10: Update user profile
            # await UserCollection.update_user_history(user_id, analysis.get("detected_tags", []))
            
            # Step 11: Update session memory
            self._update_session_memory(session_id, session_context, response_data)
            
            # Step 12: Prepare final response
            final_response = {
                "response": response_data["response"],
                "session_id": session_id,
                "agent_type": response_data.get("primary_agent", "conversation_manager"),
                "detected_tags": analysis.get("detected_tags", []),
                "emotional_state": analysis.get("emotional_state", "neutral"),
                "conversation_stage": conversation_stage,
                "escalation_needed": response_data.get("escalation_needed", False),
                "suggested_resources": response_data.get("suggested_resources", []),
                "follow_up_needed": response_data.get("follow_up_needed", False),
                "techniques_suggested": response_data.get("techniques_suggested", []),
                "next_steps": response_data.get("next_steps", [])
            }
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error in conversation flow: {e}")
            return await self._handle_error_flow(user_id, message, session_id)
    
    async def _get_or_create_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Get existing session or create new one"""
        
        if session_id in self.session_memory:
            return self.session_memory[session_id]
        
        # Create new session
        session_context = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "conversation_turn": 0,
            "conversation_stage": "greeting",
            "active_agent": "conversation_manager",
            "session_summary": "",
            "techniques_used": [],
            "assessments_completed": [],
            "escalation_history": []
        }
        
        self.session_memory[session_id] = session_context
        return session_context
    
    async def _get_or_create_user(self, user_id: str, language: Optional[str] = None) -> User:
        """Get existing user or create new one"""
        
        # user = await UserCollection.get_user(user_id)
        # if not user:
        user = User(
            user_id=user_id,
            language=Language(language) if language else Language.ENGLISH,
            preferred_style=UserStyle.EMPATHETIC,
            history=[]
        )
            # await UserCollection.create_user(user)
        
        return user
    
    def _determine_conversation_stage(self, session_context: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Determine current conversation stage"""
        
        turn_count = session_context.get("conversation_turn", 0)
        emotional_state = analysis.get("emotional_state", "neutral")
        urgency_level = analysis.get("urgency_level", "low")
        
        # Crisis always takes priority
        if urgency_level == "crisis" or analysis.get("crisis_indicators", False):
            return "crisis"
        
        # First interaction is greeting
        if turn_count <= 1:
            return "greeting"
        
        # High urgency goes to intervention
        if urgency_level == "high":
            return "intervention"
        
        # Assessment stage for new concerns
        if turn_count <= 3 and emotional_state in ["anxious", "depressed", "stressed"]:
            return "assessment"
        
        # Intervention stage for active support
        if turn_count <= 8 and urgency_level == "medium":
            return "intervention"
        
        # Follow-up for ongoing conversations
        if turn_count > 8:
            return "follow_up"
        
        return "general"
    
    async def _handle_greeting_flow(self, user: User, message: str, analysis: Dict[str, Any], session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initial greeting and welcome flow"""
        
        # Use agent orchestrator for greeting
        response_data = await agent_orchestrator.process_conversation(
            message, user.user_id, analysis, session_context
        )
        
        # Add welcome-specific elements
        welcome_additions = self._get_welcome_additions(user, analysis)
        response_data.update(welcome_additions)
        
        return response_data
    
    async def _handle_assessment_flow(self, user: User, message: str, analysis: Dict[str, Any], session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle assessment and information gathering flow"""
        
        # Process with agent orchestrator
        response_data = await agent_orchestrator.process_conversation(
            message, user.user_id, analysis, session_context
        )
        
        # Add assessment-specific elements
        assessment_additions = await self._get_assessment_additions(analysis, session_context)
        response_data.update(assessment_additions)
        
        return response_data
    
    async def _handle_intervention_flow(self, user: User, message: str, analysis: Dict[str, Any], session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle active intervention and technique delivery flow"""
        
        # Process with agent orchestrator
        response_data = await agent_orchestrator.process_conversation(
            message, user.user_id, analysis, session_context
        )
        
        # Add intervention-specific elements
        intervention_additions = self._get_intervention_additions(analysis, session_context)
        response_data.update(intervention_additions)
        
        return response_data
    
    async def _handle_follow_up_flow(self, user: User, message: str, analysis: Dict[str, Any], session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle follow-up and progress tracking flow"""
        
        # Process with agent orchestrator
        response_data = await agent_orchestrator.process_conversation(
            message, user.user_id, analysis, session_context
        )
        
        # Add follow-up specific elements
        follow_up_additions = await self._get_follow_up_additions(user, session_context)
        response_data.update(follow_up_additions)
        
        return response_data
    
    async def _handle_general_flow(self, user: User, message: str, analysis: Dict[str, Any], session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general conversation flow"""
        
        return await agent_orchestrator.process_conversation(
            message, user.user_id, analysis, session_context
        )
    
    async def _handle_crisis_flow(self, user_id: str, message: str, session_id: str, 
                                analysis: Dict[str, Any], crisis_data: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Handle crisis situations with immediate intervention"""
        
        # Get crisis messages in user's language
        crisis_messages = language_service.get_crisis_messages(user.language.value)
        
        # Get helpline numbers
        # helplines = await HelplineCollection.get_helplines(region="India")
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
        crisis_response += "\n\nI'm also connecting you with a counselor who can provide immediate support."
        
        # Log crisis event
        logger.warning(f"Crisis situation detected for user {user_id}: {crisis_data}")
        
        # Update session with crisis flag
        session_context = self.session_memory.get(session_id, {})
        session_context.update({
            "crisis_detected": True,
            "crisis_type": crisis_data.get("crisis_type", "unknown"),
            "crisis_timestamp": datetime.utcnow(),
            "immediate_intervention_needed": True
        })
        
        return {
            "response": crisis_response,
            "session_id": session_id, # Added session_id for consistency with ChatResponse
            "primary_agent": "booking_agent",
            "agent_type": "booking_agent", # Added agent_type for consistency with ChatResponse
            "detected_tags": analysis.get("detected_tags", ["crisis"]), # Added detected_tags
            "escalation_needed": True,
            "crisis_intervention": True,
            "helpline_numbers": helpline_dict,
            "suggested_resources": [], # Added suggested_resources for consistency with ChatResponse
            "immediate_actions": ["provide_helpline", "connect_counselor", "safety_planning"],
            "follow_up_needed": True,
            "next_steps": ["Contact helpline immediately", "Wait for counselor connection", "Create safety plan"]
        }
    
    async def _handle_error_flow(self, user_id: str, message: str, session_id: Optional[str]) -> Dict[str, Any]:
        """Handle errors gracefully"""
        
        return {
            "response": "I'm here to support you, but I'm having some technical difficulties right now. Your wellbeing is important - if you're in crisis, please contact emergency services or a crisis helpline immediately. Otherwise, please try again in a moment.",
            "session_id": session_id or str(uuid.uuid4()),
            "agent_type": "conversation_manager",
            "detected_tags": ["technical_error"],
            "emotional_state": "neutral",
            "conversation_stage": "error",
            "escalation_needed": False,
            "error_occurred": True
        }
    
    def _get_welcome_additions(self, user: User, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get welcome-specific additions to response"""
        
        return {
            "welcome_message": True,
            "user_preferences_detected": {
                "language": user.language.value,
                "communication_style": analysis.get("communication_style", "empathetic")
            },
            "available_resources": ["Assessment tools", "Coping techniques", "Professional support"],
            "next_steps": ["Share what's on your mind", "Take an assessment", "Learn coping techniques"]
        }
    
    async def _get_assessment_additions(self, analysis: Dict[str, Any], session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get assessment-specific additions"""
        
        detected_tags = analysis.get("detected_tags", [])
        suggested_assessments = []
        
        if "anxiety" in detected_tags:
            suggested_assessments.append("GAD-7 Anxiety Assessment")
        if "depression" in detected_tags:
            suggested_assessments.append("PHQ-9 Depression Assessment")
        if "stress" in detected_tags:
            suggested_assessments.append("Stress Level Assessment")
        
        return {
            "assessment_stage": True,
            "suggested_assessments": suggested_assessments,
            "information_gathering": True,
            "next_steps": ["Complete suggested assessment", "Share more details", "Try coping technique"]
        }
    
    def _get_intervention_additions(self, analysis: Dict[str, Any], session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get intervention-specific additions"""
        
        return {
            "intervention_stage": True,
            "active_support": True,
            "technique_delivery": True,
            "next_steps": ["Practice suggested technique", "Report back on progress", "Try additional strategies"]
        }
    
    async def _get_follow_up_additions(self, user: User, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get follow-up specific additions"""
        
        techniques_used = session_context.get("techniques_used", [])
        
        return {
            "follow_up_stage": True,
            "progress_tracking": True,
            "techniques_review": techniques_used,
            "next_steps": ["Review progress", "Adjust techniques", "Consider professional support"],
            "session_summary_available": True
        }
    
    async def _update_conversation_history(self, session_id: str, user_id: str, 
                                         user_message: str, ai_response: str, analysis: Dict[str, Any]):
        """Update conversation history in database"""
        
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
        
        # Try to update existing conversation or create new one
        # existing_conversations = await ConversationCollection.get_user_conversations(user_id, 1)
        
        # if existing_conversations and existing_conversations[0].conversation_id == session_id:
        #     # Update existing conversation
        #     existing_messages = existing_conversations[0].messages
        #     existing_messages.extend(messages)
        #     await ConversationCollection.update_conversation(
        #         session_id, 
        #         [msg.model_dump() for msg in existing_messages],
        #         analysis.get("detected_tags", [])
        #     )
        # else:
        #     # Create new conversation
        #     from models.schemas import Conversation
        #     conversation = Conversation(
        #         conversation_id=session_id,
        #         user_id=user_id,
        #         messages=messages,
        #         detected_tags=analysis.get("detected_tags", [])
        #     )
        #     await ConversationCollection.create_conversation(conversation)
            
    
    def _update_session_memory(self, session_id: str, session_context: Dict[str, Any], response_data: Dict[str, Any]):
        """Update session memory with latest interaction"""
        
        session_context.update({
            "last_response": response_data.get("response", ""),
            "last_agent": response_data.get("primary_agent", "conversation_manager"),
            "updated_at": datetime.utcnow()
        })
        
        # Add techniques used
        if "techniques_suggested" in response_data:
            techniques = session_context.get("techniques_used", [])
            new_techniques = response_data["techniques_suggested"]
            if isinstance(new_techniques, list):
                techniques.extend(new_techniques)
            else:
                techniques.append(new_techniques)
            session_context["techniques_used"] = list(set(techniques))  # Remove duplicates
        
        # Update session memory
        self.session_memory[session_id] = session_context
        
        # Clean up old sessions (keep last 100)
        if len(self.session_memory) > 100:
            oldest_sessions = sorted(
                self.session_memory.items(),
                key=lambda x: x[1].get("updated_at", datetime.min)
            )[:50]
            
            for session_id, _ in oldest_sessions:
                del self.session_memory[session_id]

# Global service instance
conversation_flow_service = ConversationFlowService()
