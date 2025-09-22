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
            
            # Determine primary agent
            primary_agent_type = analysis.get("recommended_agent", "conversation_manager")
            
            # Handle crisis situations immediately
            if analysis.get("crisis_indicators", False) or analysis.get("urgency_level") == "crisis":
                return await self._handle_crisis_situation(message, context)
            
            # Process with primary agent
            primary_response = await self._process_with_agent(
                primary_agent_type, message, context
            )
            
            # Determine if collaboration is needed
            collaboration_needed = self._should_collaborate(analysis, primary_response)
            
            if collaboration_needed:
                # Get collaborative response
                collaborative_response = await self._get_collaborative_response(
                    message, context, primary_agent_type, primary_response
                )
                return collaborative_response
            else:
                return {
                    "response": primary_response["response"],
                    "primary_agent": primary_agent_type,
                    "collaboration_used": False,
                    "techniques_suggested": primary_response.get("technique_taught") or primary_response.get("cbt_technique"),
                    "follow_up_needed": primary_response.get("follow_up_needed", False),
                    "escalation_needed": primary_response.get("escalation_completed", False)  # Added escalation status
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
    
    async def _get_collaborative_response(self, 
                                        message: str, 
                                        context: Dict[str, Any],
                                        primary_agent_type: str,
                                        primary_response: Dict[str, Any]) -> Dict[str, Any]:
        """Get collaborative response from multiple agents"""
        
        try:
            # Determine secondary agent based on tags
            secondary_agent_type = self._get_secondary_agent(
                context.get("detected_tags", []), 
                primary_agent_type
            )
            
            if secondary_agent_type and secondary_agent_type in self.agents:
                # Get secondary response
                secondary_response = await self._process_with_agent(
                    secondary_agent_type, message, context
                )
                
                # Create collaborative crew
                collaborative_response = await self._create_collaborative_crew(
                    message, context, primary_agent_type, secondary_agent_type,
                    primary_response, secondary_response
                )
                
                return collaborative_response
            else:
                # Return primary response if no suitable secondary agent
                return {
                    "response": primary_response["response"],
                    "primary_agent": primary_agent_type,
                    "collaboration_used": False
                }
                
        except Exception as e:
            logger.error(f"Error in collaborative response: {e}")
            return {
                "response": primary_response["response"],
                "primary_agent": primary_agent_type,
                "collaboration_used": False
            }
    
    async def _create_collaborative_crew(self, 
                                       message: str,
                                       context: Dict[str, Any],
                                       primary_agent_type: str,
                                       secondary_agent_type: str,
                                       primary_response: Dict[str, Any],
                                       secondary_response: Dict[str, Any]) -> Dict[str, Any]:
        """Create a collaborative crew response"""
        
        # Create integration task
        integration_task_description = f"""
        Two mental health specialists have provided responses to a user's message: "{message}"
        
        Primary Agent ({primary_agent_type}) Response: {primary_response['response']}
        Secondary Agent ({secondary_agent_type}) Response: {secondary_response['response']}
        
        User Context: {context}
        
        Create an integrated response that:
        1. Combines the best elements from both responses
        2. Maintains a coherent, supportive tone
        3. Provides comprehensive guidance addressing all user concerns
        4. Offers both immediate and long-term strategies
        5. Maintains the user's preferred communication style
        
        The integrated response should feel natural and unified, not like two separate responses.
        """
        
        # Use conversation manager for integration
        integration_agent = self.agents["conversation_manager"]
        integration_task = integration_agent.create_task(
            description=integration_task_description,
            expected_output="A unified, comprehensive response integrating both specialist perspectives"
        )
        
        # Create crew with both agents
        crew = Crew(
            agents=[
                self.agents[primary_agent_type].agent,
                self.agents[secondary_agent_type].agent,
                integration_agent.agent
            ],
            tasks=[integration_task],
            verbose=True
        )
        
        # Execute collaborative response
        result = crew.kickoff()
        
        return {
            "response": str(result),
            "primary_agent": primary_agent_type,
            "secondary_agent": secondary_agent_type,
            "collaboration_used": True,
            "techniques_suggested": [
                primary_response.get("technique_taught") or primary_response.get("cbt_technique"),
                secondary_response.get("technique_taught") or secondary_response.get("cbt_technique")
            ],
            "follow_up_needed": True
        }
    
    def _get_secondary_agent(self, tags: List[str], primary_agent: str) -> Optional[str]:
        """Determine secondary agent for collaboration"""
        
        # Don't use the same agent twice
        available_agents = [agent for agent in self.agents.keys() if agent != primary_agent]
        
        # Score agents based on tag relevance
        agent_scores = {}
        for agent_type in available_agents:
            if agent_type in self.agents:
                agent_tags = self.agents[agent_type].get_tags()
                score = len(set(tags) & set(agent_tags))
                if score > 0:
                    agent_scores[agent_type] = score
        
        # Return highest scoring agent
        if agent_scores:
            return max(agent_scores, key=agent_scores.get)
        
        return None
    
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
