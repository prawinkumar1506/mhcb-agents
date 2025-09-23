"""
Gemini AI service for mental health chatbot
Handles all interactions with Google's Gemini API
"""
import google.generativeai as genai
from config.settings import settings
from typing import Dict, List, Optional, Tuple
import json
import re
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        """Initialize Gemini service with API key"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Safety settings for mental health context
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    
    async def analyze_intent_and_emotion(self, message: str, user_history: List[str] = None) -> Dict:
        """
        Analyze user message for intent, emotional state, and appropriate agent routing
        """
        history_context = ""
        if user_history:
            history_context = f"User's previous concerns: {', '.join(user_history[-5:])}"
        
        prompt = f"""
        You are a mental health conversation analyzer. Analyze the following user message and provide a JSON response.

        User message: "{message}"
        {history_context}

        Analyze and return JSON with:
        1. "emotional_state": primary emotion (anxious, depressed, stressed, angry, hopeful, neutral)
        2. "intensity": emotion intensity (low, medium, high, crisis)
        3. "detected_tags": list of relevant tags (anxiety, depression, relationships, sleep, stress, etc.)
        4. "communication_style": detected style (formal, genz, casual, distressed)
        5. "language": detected language (English, Hindi, Tamil, Spanish)
        6. "crisis_indicators": boolean - any suicidal/self-harm mentions
        7. "recommended_agent": best agent type (conversation_manager, cbt_therapist, mindfulness_coach, psychiatrist, relationship_counselor, booking_agent)
        8. "urgency_level": response urgency (low, medium, high, crisis)
        9. "key_concerns": list of main concerns mentioned

        Example response:
        {{
            "emotional_state": "anxious",
            "intensity": "medium", 
            "detected_tags": ["anxiety", "sleep", "exams"],
            "communication_style": "genz",
            "language": "English",
            "crisis_indicators": false,
            "recommended_agent": "cbt_therapist",
            "urgency_level": "medium",
            "key_concerns": ["exam anxiety", "sleep problems"]
        }}
        """
        
        try:
            response = await self._generate_content(prompt)
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback analysis
                return self._fallback_analysis(message)
                
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return self._fallback_analysis(message)
    
    async def generate_response(self, 
                              message: str, 
                              agent_type: str,
                              user_style: str,
                              language: str,
                              context: Dict = None) -> str:
        """
        Generate contextual response based on agent type and user preferences
        """
        
        # Agent-specific system prompts
        agent_prompts = {
            "conversation_manager": self._get_conversation_manager_prompt(),
            "cbt_therapist": self._get_cbt_therapist_prompt(),
            "mindfulness_coach": self._get_mindfulness_coach_prompt(),
            "psychiatrist": self._get_psychiatrist_prompt(),
            "relationship_counselor": self._get_relationship_counselor_prompt(),
            "booking_agent": self._get_booking_agent_prompt()
        }
        
        system_prompt = agent_prompts.get(agent_type, agent_prompts["conversation_manager"])
        
        # Style adaptation
        style_instructions = {
            "formal": "Use professional, respectful language. Be clear and structured.",
            "genz": "Use casual, relatable language. Include modern expressions but stay supportive. Use 'rn', 'fr', etc. naturally.",
            "empathetic": "Use warm, understanding language. Focus on validation and emotional support.",
            "clinical": "Use precise, evidence-based language. Reference therapeutic techniques and clinical approaches."
        }
        
        context_info = ""
        if context:
            context_info = f"Context: {json.dumps(context, indent=2)}"
        
        prompt = f"""
        {system_prompt}
        
        Communication Style: {style_instructions.get(user_style, style_instructions['empathetic'])}
        Language: Respond in {language}
        
        {context_info}
        
        User message: "{message}"
        
        Provide a helpful, supportive response that:
        1. Acknowledges the user's feelings
        2. Offers practical guidance or techniques
        3. Maintains appropriate boundaries
        4. Suggests next steps if needed
        5. Matches the requested communication style
        
        Keep response concise but thorough (2-4 sentences typically).
        """
        
        try:
            response = await self._generate_content(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm here to support you. Could you tell me more about what you're experiencing right now?"
    
    async def detect_crisis_situation(self, message: str) -> Tuple[bool, Dict]:
        """
        Specialized crisis detection with immediate response protocols
        """
        prompt = f"""
        You are a crisis detection system for mental health support. Analyze this message for immediate safety concerns.

        Message: "{message}"

        Return JSON with:
        1. "is_crisis": boolean - immediate safety concern detected
        2. "crisis_type": type if crisis (suicidal, self_harm, psychosis, severe_depression, panic)
        3. "confidence": confidence level (low, medium, high)
        4. "immediate_actions": list of immediate steps needed
        5. "helpline_needed": boolean - should helpline be provided immediately

        Crisis indicators include:
        - Suicidal ideation or plans
        - Self-harm intentions
        - Psychotic symptoms
        - Severe panic attacks
        - Immediate danger to self or others

        Example:
        {{
            "is_crisis": true,
            "crisis_type": "suicidal",
            "confidence": "high",
            "immediate_actions": ["provide_helpline", "connect_counselor", "safety_planning"],
            "helpline_needed": true
        }}
        """
        
        try:
            response = await self._generate_content(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                crisis_data = json.loads(json_match.group())
                return crisis_data.get("is_crisis", False), crisis_data
            else:
                return False, {"is_crisis": False, "confidence": "low"}
                
        except Exception as e:
            logger.error(f"Error in crisis detection: {e}")
            # Err on the side of caution - check for obvious crisis keywords
            crisis_keywords = ["suicide", "kill myself", "end it all", "don't want to live", "hurt myself"]
            has_crisis_keyword = any(keyword in message.lower() for keyword in crisis_keywords)
            return has_crisis_keyword, {
                "is_crisis": has_crisis_keyword,
                "crisis_type": "potential_suicidal" if has_crisis_keyword else "unknown",
                "confidence": "medium" if has_crisis_keyword else "low",
                "helpline_needed": has_crisis_keyword
            }
    
    async def _generate_content(self, prompt: str) -> str:
        """Generate content using Gemini API with safety settings"""
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
            )
            # Robustly handle multi-part responses or simple text responses
            if response.candidates:
                # Assuming the first candidate is the desired one
                candidate_content = response.candidates[0].content
                if candidate_content.parts:
                    full_text_response = "".join([part.text for part in candidate_content.parts if hasattr(part, 'text')])
                    return full_text_response
            # If no candidates or parts, raise an error
            raise ValueError("Gemini API response did not contain text content.")
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def _fallback_analysis(self, message: str) -> Dict:
        """Fallback analysis when Gemini API fails"""
        # Simple keyword-based analysis
        anxiety_keywords = ["anxious", "worried", "panic", "nervous", "stress"]
        depression_keywords = ["sad", "depressed", "hopeless", "empty", "worthless"]
        crisis_keywords = ["suicide", "kill myself", "hurt myself", "end it all"]
        
        detected_tags = []
        emotional_state = "neutral"
        urgency_level = "low"
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in crisis_keywords):
            urgency_level = "crisis"
            detected_tags.append("crisis")
            emotional_state = "crisis"
        elif any(word in message_lower for word in anxiety_keywords):
            detected_tags.append("anxiety")
            emotional_state = "anxious"
            urgency_level = "medium"
        elif any(word in message_lower for word in depression_keywords):
            detected_tags.append("depression")
            emotional_state = "depressed"
            urgency_level = "medium"
        
        return {
            "emotional_state": emotional_state,
            "intensity": "medium",
            "detected_tags": detected_tags,
            "communication_style": "empathetic",
            "language": "English",
            "crisis_indicators": urgency_level == "crisis",
            "recommended_agent": "booking_agent" if urgency_level == "crisis" else "conversation_manager",
            "urgency_level": urgency_level,
            "key_concerns": detected_tags
        }
    
    def _get_conversation_manager_prompt(self) -> str:
        return """
        You are a Conversation Manager for a mental health support chatbot. Your role is to:
        1. Provide initial empathetic response and assessment
        2. Route users to appropriate specialized agents when needed
        3. Adapt communication style to match user preferences
        4. Detect language and respond accordingly
        5. Maintain a warm, supportive tone while being professional
        
        You have access to specialized agents for CBT, mindfulness, psychiatry, and relationship counseling.
        Always prioritize user safety and well-being.
        """
    
    def _get_cbt_therapist_prompt(self) -> str:
        return """
        You are a CBT (Cognitive Behavioral Therapy) Therapist agent. Your expertise includes:
        1. Identifying negative thought patterns and cognitive distortions
        2. Teaching thought reframing techniques
        3. Providing behavioral activation strategies
        4. Offering structured exercises and homework
        5. Helping users challenge unhelpful thoughts
        
        Use evidence-based CBT techniques. Provide practical, actionable guidance.
        Focus on the connection between thoughts, feelings, and behaviors.
        """
    
    def _get_mindfulness_coach_prompt(self) -> str:
        return """
        You are a Mindfulness Coach specializing in stress management and wellness. Your expertise includes:
        1. Teaching breathing techniques and meditation
        2. Providing grounding exercises for anxiety and panic
        3. Offering sleep hygiene guidance
        4. Suggesting lifestyle balance strategies
        5. Teaching present-moment awareness techniques
        
        Focus on practical, immediate techniques users can apply right now.
        Emphasize self-compassion and non-judgmental awareness.
        """
    
    def _get_psychiatrist_prompt(self) -> str:
        return """
        You are a Psychiatrist Consultant agent. Your role is to:
        1. Assess when professional medical evaluation may be needed
        2. Identify symptoms that may require medication consultation
        3. Recognize severe mental health conditions
        4. Provide psychoeducation about mental health conditions
        5. Make appropriate referrals to human professionals
        
        You cannot prescribe medication or provide medical diagnosis.
        Focus on education and appropriate referral recommendations.
        """
    
    def _get_relationship_counselor_prompt(self) -> str:
        return """
        You are a Relationship Counselor specializing in interpersonal issues. Your expertise includes:
        1. Communication skills and conflict resolution
        2. Family dynamics and relationship patterns
        3. Workplace relationship challenges
        4. Boundary setting and assertiveness
        5. Social anxiety and interpersonal difficulties
        
        Focus on practical communication strategies and healthy relationship skills.
        Help users understand relationship dynamics and develop coping strategies.
        """
    
    def _get_booking_agent_prompt(self) -> str:
        return """
        You are a Booking Agent responsible for crisis intervention and professional referrals. Your role is to:
        1. Identify when immediate professional help is needed
        2. Provide crisis helpline numbers when appropriate
        3. Schedule appointments with student counselors
        4. Handle escalation to human professionals
        5. Ensure user safety is the top priority
        
        Always err on the side of caution. When in doubt, provide helpline resources.
        Connect users with human support when AI assistance is insufficient.
        """

# Global service instance
gemini_service = GeminiService()
