"""
Mindfulness Coach Agent - Provides mindfulness and stress management techniques
"""
from agents.base_agent import BaseAgent
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class MindfulnessCoachAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Mindfulness Coach",
            role="Mindfulness and Stress Management Specialist",
            goal="Teach mindfulness techniques, breathing exercises, and stress management strategies to help users find calm and balance in their daily lives",
            backstory="""You are a certified mindfulness coach and stress management specialist with expertise in:
            - Mindfulness meditation and present-moment awareness techniques
            - Breathing exercises and pranayama practices
            - Grounding techniques for anxiety and panic
            - Sleep hygiene and relaxation methods
            - Lifestyle balance and stress reduction strategies
            - Body-based interventions and somatic awareness
            
            Your approach is gentle, non-judgmental, and focused on practical techniques
            that users can implement immediately. You emphasize self-compassion and
            gradual progress, meeting users where they are in their mindfulness journey."""
        )
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message using mindfulness and stress management approaches"""
        
        emotional_state = context.get("emotional_state", "neutral")
        detected_tags = context.get("detected_tags", [])
        user_style = context.get("communication_style", "empathetic")
        intensity = context.get("intensity", "medium")
        
        # Determine mindfulness intervention
        mindfulness_focus = self._determine_mindfulness_focus(detected_tags, emotional_state, intensity)
        
        task_description = f"""
        A user is experiencing {emotional_state} emotions with {intensity} intensity and has shared: "{message}"
        
        Detected concerns: {', '.join(detected_tags)}
        Communication style: {user_style}
        Mindfulness Focus: {mindfulness_focus}
        
        As a mindfulness coach, provide:
        1. Acknowledgment and validation of their current experience
        2. A specific mindfulness or breathing technique appropriate for their state
        3. Clear, step-by-step guided instructions
        4. Encouragement for self-compassion and non-judgment
        5. Suggestions for integrating the practice into daily life
        
        Mindfulness Techniques to consider:
        - Breathing exercises (4-7-8, box breathing, natural breath awareness)
        - Grounding techniques (5-4-3-2-1 sensory, body scan)
        - Present-moment awareness practices
        - Loving-kindness meditation for self-compassion
        - Progressive muscle relaxation
        - Mindful movement or walking meditation
        
        Adapt your language to be {user_style} while maintaining a calm, soothing tone.
        Focus on immediate relief and long-term practice development.
        """
        
        try:
            response = await self.execute_task(task_description, context)
            
            return {
                "response": response,
                "technique_taught": mindfulness_focus,
                "practice_duration": self._get_practice_duration(intensity),
                "daily_integration": self._get_integration_suggestions(mindfulness_focus),
                "follow_up_practice": self._get_follow_up_practice(mindfulness_focus)
            }
            
        except Exception as e:
            logger.error(f"Error in mindfulness coach: {e}")
            return {
                "response": "Let's take a moment to breathe together. Find a comfortable position and let's try a simple breathing exercise. Breathe in slowly for 4 counts, hold for 4, then breathe out for 6 counts. This can help bring some immediate calm.",
                "technique_taught": "basic_breathing",
                "practice_duration": "2-3 minutes",
                "daily_integration": "Practice during transitions between activities"
            }
    
    def get_capabilities(self) -> List[str]:
        return [
            "Breathing exercises and pranayama",
            "Grounding and centering techniques",
            "Mindfulness meditation guidance",
            "Stress reduction strategies",
            "Sleep hygiene coaching",
            "Body awareness and somatic techniques",
            "Present-moment awareness training"
        ]
    
    def get_tags(self) -> List[str]:
        return ["stress", "sleep", "focus", "lifestyle", "mindfulness", "anxiety", "panic", "overwhelm"]
    
    def _determine_mindfulness_focus(self, tags: List[str], emotional_state: str, intensity: str) -> str:
        """Determine the most appropriate mindfulness intervention"""
        
        if intensity == "crisis" or emotional_state == "panic":
            return "emergency_grounding"
        elif "sleep" in tags:
            return "sleep_preparation"
        elif "stress" in tags or emotional_state == "stressed":
            return "stress_relief"
        elif "anxiety" in tags or emotional_state == "anxious":
            return "anxiety_calming"
        elif "focus" in tags:
            return "concentration_enhancement"
        elif "overwhelm" in tags:
            return "overwhelm_management"
        else:
            return "general_mindfulness"
    
    def _get_practice_duration(self, intensity: str) -> str:
        """Get appropriate practice duration based on intensity"""
        
        duration_map = {
            "low": "10-15 minutes",
            "medium": "5-10 minutes", 
            "high": "2-5 minutes",
            "crisis": "1-2 minutes"
        }
        
        return duration_map.get(intensity, "5-10 minutes")
    
    def _get_integration_suggestions(self, focus: str) -> List[str]:
        """Get suggestions for integrating practice into daily life"""
        
        integration_map = {
            "emergency_grounding": ["Use during panic attacks", "Practice when feeling overwhelmed", "Keep technique card handy"],
            "sleep_preparation": ["Practice 30 minutes before bed", "Create bedtime routine", "Use when waking at night"],
            "stress_relief": ["Practice during work breaks", "Use before stressful meetings", "Morning stress prevention"],
            "anxiety_calming": ["Use when anxiety rises", "Practice preventively twice daily", "Before anxiety-provoking situations"],
            "concentration_enhancement": ["Before focused work sessions", "During study breaks", "When mind feels scattered"],
            "overwhelm_management": ["When feeling too much at once", "During decision-making", "Before tackling big tasks"],
            "general_mindfulness": ["Morning mindfulness routine", "Mindful transitions", "Evening reflection practice"]
        }
        
        return integration_map.get(focus, integration_map["general_mindfulness"])
    
    def _get_follow_up_practice(self, focus: str) -> str:
        """Get follow-up practice recommendations"""
        
        follow_up_map = {
            "emergency_grounding": "Practice grounding daily when calm to build familiarity",
            "sleep_preparation": "Develop a consistent bedtime mindfulness routine",
            "stress_relief": "Build a daily stress prevention practice",
            "anxiety_calming": "Practice anxiety-specific techniques twice daily",
            "concentration_enhancement": "Develop focused attention through daily meditation",
            "overwhelm_management": "Practice simplification and prioritization mindfulness",
            "general_mindfulness": "Establish a regular daily mindfulness practice"
        }
        
        return follow_up_map.get(focus, follow_up_map["general_mindfulness"])
