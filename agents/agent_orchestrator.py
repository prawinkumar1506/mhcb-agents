"""
Agent Orchestrator - Manages multi-agent collaboration using CrewAI
"""
from typing import Dict, List, Any, Optional
from crewai import Crew, Task
from agents.conversation_manager import ConversationManagerAgent
from agents.cbt_therapist import CBTTherapistAgent
from agents.mindfulness_coach import MindfulnessCoachAgent
from agents.booking_agent import BookingAgent
from database.collections import UserCollection
import logging

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        """Initialize all agents"""
        self.agents = {
            "conversation_manager": ConversationManagerAgent(),
            "cbt_therapist": CBTTherapistAgent(),
            "mindfulness_coach": MindfulnessCoachAgent(),
            "booking_agent": BookingAgent(),  # Added booking agent
            # Additional agents can be added here
        }
        
        self.agent_priority = {
            "conversation_manager": 1,
            "cbt_therapist": 2,
            "mindfulness_coach": 2,
            "psychiatrist": 3,
            "relationship_counselor": 2,
            "booking_agent": 4
        }
    
    async def process_conversation(self, 
                                 message: str, 
                                 user_id: str,
                                 analysis: Dict[str, Any],
                                 session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Orchestrate multi-agent conversation processing
        """
        try:
            # Get user context
            user = await UserCollection.get_user(user_id)
            user_context = {
                "user_history": user.history if user else [],
                "preferred_style": user.preferred_style.value if user else "empathetic",
                "language": user.language.value if user else "English",
                "user_id": user_id  # Added user_id to context
            }
            
            # Merge contexts
            context = {**analysis, **user_context, **(session_context or {})}
            
            # Handle crisis situations immediately
            if analysis.get("crisis_indicators", False) or analysis.get("urgency_level") == "crisis":
                return await self._handle_crisis_situation(message, context)

            # Step 1: Check for simple questions to be handled by ConversationManagerAgent
            if self._is_simple_query(analysis):
                logger.info("Simple query detected. Routing to ConversationManagerAgent.")
                conversation_manager_agent = self.agents["conversation_manager"]
                response = await conversation_manager_agent.process_message(message, context)
                return {
                    "response": response["response"],
                    "primary_agent": "conversation_manager",
                    "collaboration_used": False,
                    "techniques_suggested": response.get("technique_taught"),
                    "follow_up_needed": response.get("follow_up_needed", False),
                    "escalation_needed": response.get("escalation_completed", False)
                }

            # Step 2: Determine primary agent for complex queries
            primary_agent_type = analysis.get("recommended_agent", "conversation_manager")
            logger.info(f"Complex query detected. Routing to primary agent: {primary_agent_type}")

            # Process with primary agent (only one agent should respond)
            primary_response = await self._process_with_agent(
                primary_agent_type, message, context
            )

            return {
                "response": primary_response["response"],
                "primary_agent": primary_agent_type,
                "collaboration_used": False, # Collaboration is explicitly disabled as per user request
                "techniques_suggested": primary_response.get("technique_taught") or primary_response.get("cbt_technique"),
                "follow_up_needed": primary_response.get("follow_up_needed", False),
                "escalation_needed": primary_response.get("escalation_completed", False)
            }
        except Exception as e:
            logger.error(f"Error in agent orchestration: {e}")
            return await self._fallback_response(message, context)
    
    async def _process_with_agent(self, agent_type: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message with specific agent"""
        
        if agent_type not in self.agents:
            # Fallback to conversation manager
            agent_type = "conversation_manager"
        
        agent = self.agents[agent_type]
        return await agent.process_message(message, context)
    
    async def _handle_crisis_situation(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle crisis situations with immediate intervention"""
        
        booking_agent = self.agents["booking_agent"]
        crisis_response = await booking_agent.process_message(message, context)
        
        return {
            "response": crisis_response["response"],
            "primary_agent": "booking_agent",
            "collaboration_used": False,
            "crisis_intervention": True,
            "immediate_actions": crisis_response.get("resources_provided", {}).get("immediate_actions", []),
            "follow_up_needed": True,
            "escalation_needed": True,
            "intervention_type": crisis_response.get("intervention_type", "crisis")
        }
    
    def _should_collaborate(self, analysis: Dict[str, Any], primary_response: Dict[str, Any]) -> bool:
        """Determine if multi-agent collaboration would be beneficial"""
        
        # Collaborate if multiple high-confidence tags are detected
        detected_tags = analysis.get("detected_tags", [])
        if len(detected_tags) >= 3:
            return True
        
        # Collaborate if primary agent suggests it
        if primary_response.get("collaboration_recommended", False):
            return True
        
        # Collaborate for complex emotional states
        emotional_state = analysis.get("emotional_state", "neutral")
        if emotional_state in ["overwhelmed", "mixed", "complex"]:
            return True
        
        return False

    def _is_simple_query(self, analysis: Dict[str, Any]) -> bool:
        """
        Determines if a query is simple enough to be handled directly by the ConversationManagerAgent.
        A query is considered simple if:
        - The detected intent is a greeting, general inquiry, or small talk.
        - The emotional state is neutral or positive.
        - There are no crisis indicators or high urgency levels.
        - The recommended agent is already the conversation manager, or no specific agent is strongly recommended.
        """
        intent = analysis.get("intent", "general_inquiry")
        emotional_state = analysis.get("emotional_state", "neutral")
        urgency_level = analysis.get("urgency_level", "low")
        recommended_agent = analysis.get("recommended_agent", "conversation_manager")

        simple_intents = ["greeting", "general_inquiry", "small_talk", "acknowledgement"]
        neutral_positive_emotions = ["neutral", "positive", "calm", "curious"]

        if (intent in simple_intents and
            emotional_state in neutral_positive_emotions and
            urgency_level == "low" and
            not analysis.get("crisis_indicators", False) and
            (recommended_agent == "conversation_manager" or recommended_agent is None)):
            return True
        return False

    async def _fallback_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback response when orchestration fails"""

        return {
            "response": "I'm here to support you. Could you tell me more about what you're experiencing right now?",
            "primary_agent": "conversation_manager",
            "collaboration_used": False,
            "error_occurred": True,
            "follow_up_needed": True
        }

# Global orchestrator instance
agent_orchestrator = AgentOrchestrator()
