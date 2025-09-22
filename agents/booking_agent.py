"""
Booking Agent - Handles escalation and appointment scheduling
"""
from agents.base_agent import BaseAgent
from typing import Dict, List, Any
from database.collections import ExpertCollection, BookingCollection, HelplineCollection
from models.schemas import BookingRequest
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BookingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Booking Agent",
            role="Crisis Intervention and Professional Referral Specialist",
            goal="Identify crisis situations, provide immediate safety resources, and connect users with appropriate human mental health professionals",
            backstory="""You are a specialized crisis intervention and booking agent with expertise in:
            - Crisis detection and immediate safety assessment
            - Emergency protocol implementation and helpline referrals
            - Professional mental health service coordination
            - Appointment scheduling with student counselors and therapists
            - Escalation management for high-risk situations
            - Safety planning and immediate intervention strategies
            
            Your primary responsibility is user safety. You always err on the side of caution
            and prioritize immediate professional intervention when there are any safety concerns.
            You serve as the bridge between AI support and human professional care."""
        )
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message with focus on crisis intervention and professional referral"""
        
        emotional_state = context.get("emotional_state", "neutral")
        detected_tags = context.get("detected_tags", [])
        urgency_level = context.get("urgency_level", "low")
        user_id = context.get("user_id", "unknown")
        
        # Determine intervention type
        intervention_type = self._determine_intervention_type(emotional_state, detected_tags, urgency_level)
        
        task_description = f"""
        A user requires professional intervention support. Message: "{message}"
        
        Context:
        - Emotional state: {emotional_state}
        - Urgency level: {urgency_level}
        - Detected concerns: {', '.join(detected_tags)}
        - Intervention type needed: {intervention_type}
        
        As a booking and crisis intervention agent, provide:
        1. Immediate safety assessment and validation
        2. Crisis intervention if needed (helpline numbers, emergency contacts)
        3. Professional referral recommendations
        4. Appointment scheduling guidance
        5. Safety planning if appropriate
        6. Clear next steps for getting human support
        
        Intervention Types:
        - Crisis: Immediate safety concerns, provide helplines and emergency contacts
        - Urgent: Same-day professional support needed
        - Scheduled: Regular appointment booking with counselor
        - Referral: Specialized professional referral needed
        
        Always prioritize user safety and provide concrete, actionable steps.
        Be direct and clear about available resources and how to access them.
        """
        
        try:
            response = await self.execute_task(task_description, context)
            
            # Get appropriate resources based on intervention type
            resources = await self._get_intervention_resources(intervention_type, context)
            
            # Create booking if needed
            booking_created = False
            if intervention_type in ["urgent", "scheduled"]:
                booking_created = await self._create_booking_request(user_id, intervention_type, context)
            
            return {
                "response": response,
                "intervention_type": intervention_type,
                "resources_provided": resources,
                "booking_created": booking_created,
                "immediate_action_required": intervention_type == "crisis",
                "follow_up_needed": True,
                "escalation_completed": True
            }
            
        except Exception as e:
            logger.error(f"Error in booking agent: {e}")
            # Crisis fallback - always provide safety resources
            return await self._crisis_fallback_response(context)
    
    def get_capabilities(self) -> List[str]:
        return [
            "Crisis detection and intervention",
            "Emergency helpline provision",
            "Professional referral coordination",
            "Appointment scheduling",
            "Safety planning",
            "Escalation management",
            "Emergency protocol implementation"
        ]
    
    def get_tags(self) -> List[str]:
        return ["appointment", "escalation", "crisis", "emergency", "professional_referral", "safety"]
    
    def _determine_intervention_type(self, emotional_state: str, tags: List[str], urgency_level: str) -> str:
        """Determine the type of intervention needed"""
        
        # Crisis indicators
        crisis_tags = ["crisis", "suicidal", "self_harm", "psychosis", "immediate_danger"]
        if (emotional_state == "crisis" or 
            urgency_level == "crisis" or 
            any(tag in crisis_tags for tag in tags)):
            return "crisis"
        
        # Urgent professional support needed
        urgent_tags = ["severe_depression", "severe_anxiety", "panic_disorder", "bipolar", "medication_needed"]
        if (urgency_level == "high" or 
            any(tag in urgent_tags for tag in tags)):
            return "urgent"
        
        # Specialized referral needed
        referral_tags = ["medication", "psychiatric_evaluation", "specialized_therapy"]
        if any(tag in referral_tags for tag in tags):
            return "referral"
        
        # Regular appointment scheduling
        return "scheduled"
    
    async def _get_intervention_resources(self, intervention_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get appropriate resources based on intervention type"""
        
        resources = {
            "helplines": [],
            "experts": [],
            "immediate_actions": [],
            "follow_up_actions": []
        }
        
        try:
            # Get helplines for crisis situations
            if intervention_type == "crisis":
                helplines = await HelplineCollection.get_helplines()
                resources["helplines"] = [
                    {"issue": h.issue, "number": h.number, "description": h.description}
                    for h in helplines
                ]
                resources["immediate_actions"] = [
                    "Call crisis helpline immediately",
                    "Contact emergency services if in immediate danger",
                    "Reach out to trusted friend or family member",
                    "Go to nearest emergency room if needed"
                ]
            
            # Get available experts
            relevant_tags = context.get("detected_tags", [])
            experts = await ExpertCollection.get_available_experts(relevant_tags)
            resources["experts"] = [
                {
                    "name": expert.name,
                    "profession": expert.profession,
                    "specialties": expert.tags,
                    "available": expert.availability
                }
                for expert in experts[:3]  # Limit to top 3 matches
            ]
            
            # Set follow-up actions based on intervention type
            if intervention_type == "urgent":
                resources["follow_up_actions"] = [
                    "Schedule same-day appointment",
                    "Monitor symptoms closely",
                    "Use coping strategies while waiting"
                ]
            elif intervention_type == "scheduled":
                resources["follow_up_actions"] = [
                    "Schedule appointment within 1-2 weeks",
                    "Continue self-care practices",
                    "Track mood and symptoms"
                ]
            elif intervention_type == "referral":
                resources["follow_up_actions"] = [
                    "Get referral to specialist",
                    "Schedule evaluation appointment",
                    "Prepare questions for specialist"
                ]
            
        except Exception as e:
            logger.error(f"Error getting intervention resources: {e}")
        
        return resources
    
    async def _create_booking_request(self, user_id: str, intervention_type: str, context: Dict[str, Any]) -> bool:
        """Create a booking request for professional support"""
        
        try:
            urgency_mapping = {
                "crisis": "crisis",
                "urgent": "urgent", 
                "scheduled": "normal",
                "referral": "normal"
            }
            
            booking = BookingRequest(
                user_id=user_id,
                expert_type="student_counselor",  # Default to student counselor
                urgency_level=urgency_mapping.get(intervention_type, "normal"),
                notes=f"Auto-generated booking from {intervention_type} intervention. "
                      f"Detected concerns: {', '.join(context.get('detected_tags', []))}"
            )
            
            success = await BookingCollection.create_booking(booking)
            
            if success:
                logger.info(f"Booking created for user {user_id} with urgency {intervention_type}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating booking request: {e}")
            return False
    
    async def _crisis_fallback_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback response for crisis situations when other processing fails"""
        
        try:
            # Get helplines as fallback
            helplines = await HelplineCollection.get_helplines()
            helpline_text = "\n".join([f"• {h.issue}: {h.number}" for h in helplines[:3]])
            
            crisis_response = f"""I'm very concerned about your safety. Please reach out for immediate help:

{helpline_text}

If you're in immediate danger, please call emergency services (911/112).

I'm also connecting you with a counselor who can provide immediate support."""
            
            return {
                "response": crisis_response,
                "intervention_type": "crisis",
                "immediate_action_required": True,
                "escalation_completed": True,
                "resources_provided": {"helplines": [h.model_dump() for h in helplines]},
                "follow_up_needed": True
            }
            
        except Exception as e:
            logger.error(f"Error in crisis fallback: {e}")
            return {
                "response": "I'm concerned about your wellbeing. Please contact emergency services (911/112) or a crisis helpline immediately if you're in danger.",
                "intervention_type": "crisis",
                "immediate_action_required": True,
                "escalation_completed": True
            }
