"""
Conversation Manager Agent - Routes conversations and adapts communication style
"""
from agents.base_agent import BaseAgent
from typing import Dict, List, Any
from services.language_service import language_service
import logging

logger = logging.getLogger(__name__)

class ConversationManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Conversation Manager",
            role="Mental Health Conversation Manager and Router",
            goal="Provide empathetic initial responses, detect user needs, and route to appropriate specialized agents while adapting communication style to user preferences",
            backstory="""You are an experienced mental health conversation manager with expertise in:
            - Empathetic communication and active listening
            - Crisis detection and immediate response protocols
            - Multi-cultural and multilingual mental health support
            - Adaptive communication styles (formal, casual, clinical, empathetic)
            - Routing users to appropriate specialized mental health professionals
            
            You serve as the first point of contact for users seeking mental health support.
            Your primary goal is to make users feel heard, understood, and safely guided
            to the most appropriate form of help for their specific situation."""
        )
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process initial user message and provide routing decision"""
        
        user_style = context.get("communication_style", "empathetic")
        language = context.get("language", "English")
        emotional_state = context.get("emotional_state", "neutral")
        detected_tags = context.get("detected_tags", [])

        # Step 1: Handle very simple greetings immediately
        lower_message = message.lower().strip()
        simple_greetings = ["hi", "hello", "hey", "hii daa", "hola", "namaste", "daa"] # Added "daa"

        if any(greeting in lower_message for greeting in simple_greetings) and len(lower_message) <= 10: # Slightly increased length for flexibility
            logger.info("Very simple greeting detected. Returning templated response.")
            greeting_text = language_service.get_greeting_templates(language, user_style)
            return {
                "response": greeting_text,
                "options": ["What's on your mind?", "How are you feeling?", "Tell me more."],
                "recommended_agent": "conversation_manager",
                "routing_confidence": "high",
                "immediate_actions": ["continue_conversation"]
            }
        
        # Create task description based on context
        task_description = f"""
        Analyze the user's message: "{message}" with context: emotional_state={emotional_state}, style={user_style}, language={language}, concerns={', '.join(detected_tags)}.
        
        Your task is to generate a JSON object with two keys: "response_text" and "response_options".
        
        1.  **response_text**: 
            - Acknowledge the user's feelings empathetically.
            - Keep it concise and use bullet points or short paragraphs.
            - Adapt to the user's communication style ({user_style}).
            - Bold each point's heading.
        
        2.  **response_options**: 
            - Provide 2-3 relevant, short follow-up options.
            - Examples: "Tell me more about it.", "What's on your mind?", "Suggest a coping strategy."
        
        Example for a distressed user:
        {{
            "response_text": "It sounds like you're going through a lot. I'm here for you.\\n\\n- **Acknowledge Feelings**: It's okay to feel this way.\\n- **Next Steps**: We can explore what's happening together.",
            "response_options": ["I want to talk more.", "Help me calm down.", "I'm not sure what to do."]
        }}
        """
        
        try:
            import json
            import re
            response_str = await self.execute_task(task_description, context)
            
            # Extract JSON from markdown code block if present
            json_match = re.search(r"```json\n(.*?)```", response_str, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
            else:
                json_content = response_str # Assume it's pure JSON if no markdown block
            
            response_json = json.loads(json_content)
            
            # Determine recommended next agent based on tags
            recommended_agent = self._determine_next_agent(detected_tags, emotional_state)
            
            return {
                "response": response_json.get("response_text"),
                "options": response_json.get("response_options", []),
                "recommended_agent": recommended_agent,
                "routing_confidence": self._calculate_routing_confidence(detected_tags),
                "immediate_actions": self._get_immediate_actions(detected_tags, emotional_state)
            }
            
        except Exception as e:
            logger.error(f"Error in conversation manager: {e}")
            # Fallback response
            greeting = language_service.get_greeting_templates(language, user_style)
            return {
                "response": greeting,
                "options": ["Tell me what's on your mind.", "I'm here to listen."],
                "recommended_agent": "conversation_manager",
                "routing_confidence": "low",
                "immediate_actions": ["continue_conversation"]
            }
    
    def get_capabilities(self) -> List[str]:
        return [
            "Empathetic initial response",
            "Communication style adaptation",
            "Multilingual support",
            "Crisis detection",
            "Agent routing",
            "Immediate coping strategy suggestions"
        ]
    
    def get_tags(self) -> List[str]:
        return ["general", "routing", "multilingual", "adaptation", "initial_contact"]
    
    def _determine_next_agent(self, tags: List[str], emotional_state: str) -> str:
        """Determine the most appropriate next agent based on user needs"""
        
        # Crisis situations always go to booking agent
        if emotional_state == "crisis" or any(tag in ["crisis", "suicidal", "self_harm"] for tag in tags):
            return "booking_agent"
        
        # Severe conditions need psychiatrist consultation
        if any(tag in ["severe_depression", "bipolar", "psychosis", "medication"] for tag in tags):
            return "psychiatrist"
        
        # CBT-appropriate conditions
        if any(tag in ["anxiety", "depression", "negative_thoughts", "panic", "phobia"] for tag in tags):
            return "cbt_therapist"
        
        # Mindfulness and stress management
        if any(tag in ["stress", "sleep", "focus", "lifestyle", "mindfulness"] for tag in tags):
            return "mindfulness_coach"
        
        # Relationship issues
        if any(tag in ["relationships", "family", "workplace", "communication"] for tag in tags):
            return "relationship_counselor"
        
        # Default to conversation manager for general support
        return "conversation_manager"
    
    def _calculate_routing_confidence(self, tags: List[str]) -> str:
        """Calculate confidence level for agent routing"""
        if len(tags) == 0:
            return "low"
        elif len(tags) <= 2:
            return "medium"
        else:
            return "high"
    
    def _get_immediate_actions(self, tags: List[str], emotional_state: str) -> List[str]:
        """Get immediate actions based on user state"""
        actions = []
        
        if emotional_state == "crisis":
            actions.extend(["provide_helpline", "connect_counselor", "safety_check"])
        elif emotional_state in ["anxious", "panic"]:
            actions.extend(["breathing_exercise", "grounding_technique"])
        elif emotional_state == "depressed":
            actions.extend(["validation", "hope_instillation", "small_step_planning"])
        elif "stress" in tags:
            actions.extend(["stress_assessment", "immediate_relief_techniques"])
        
        if not actions:
            actions.append("continue_conversation")
        
        return actions
