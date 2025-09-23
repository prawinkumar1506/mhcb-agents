"""
CBT Therapist Agent - Provides cognitive behavioral therapy techniques
"""
from agents.base_agent import BaseAgent
from typing import Dict, List, Any
import logging
import re # Added import for regex

logger = logging.getLogger(__name__)

# Define a custom exception for agent execution limits
class AgentExecutionLimitError(Exception):
    """Custom exception for when the agent stops due to iteration/time limit."""
    pass

class CBTTherapistAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CBT Therapist",
            role="Cognitive Behavioral Therapy Specialist",
            goal="Help users identify and challenge negative thought patterns, provide structured CBT exercises, and teach coping strategies for anxiety and depression",
            backstory="""You are a licensed cognitive behavioral therapist with extensive experience in:
            - Identifying cognitive distortions and negative thought patterns
            - Teaching thought reframing and cognitive restructuring techniques
            - Providing behavioral activation strategies for depression
            - Offering structured homework assignments and exercises
            - Helping users understand the connection between thoughts, feelings, and behaviors
            
            You use evidence-based CBT techniques and always provide practical, actionable guidance.
            Your approach is structured, educational, and empowering, helping users develop
            long-term coping skills and resilience."""
        )
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message using CBT techniques"""
        
        emotional_state = context.get("emotional_state", "neutral")
        detected_tags = context.get("detected_tags", [])
        user_style = context.get("communication_style", "empathetic")
        
        # Determine CBT intervention based on tags and emotional state
        cbt_focus = self._determine_cbt_focus(detected_tags, emotional_state)
        
        task_description = f"""
        A user is experiencing {emotional_state} emotions. Message: "{message}". 
        Concerns: {', '.join(detected_tags)}. Style: {user_style}. CBT Focus: {cbt_focus}.

        Generate ONLY a JSON object with "response_text" and "response_options". Do not include any other text or formatting outside the JSON object.

        1.  **response_text**:
            - Validate their experience concisely.
            - Introduce a relevant CBT technique ({cbt_focus}) with clear, bullet-pointed steps.
            - Bold each point's heading.
            - Suggest a small, actionable homework task.

        2.  **response_options**:
            - Provide 2-3 short, relevant options.
            - Examples: "Explain this more.", "I'm ready to try.", "What if I can't do it?".

        Example for Behavioral Activation:
        {{
            "response_text": "It's tough feeling this way, but we can take small steps together.\\n\\n- **CBT Technique**: Let's try Behavioral Activation to gently re-engage with positive activities.\\n- **First Step**: Pick one small, enjoyable activity to do today, like listening to a favorite song.\\n- **Homework**: Try scheduling one such activity each day for the next three days.",
            "response_options": ["Tell me more about this.", "I'll give it a try.", "I don't feel motivated."]
        }}
        """
        
        response_str = await self.execute_task(task_description, context)

        # Explicitly check for the known error message immediately after receiving response_str
        if "Agent stopped due to iteration limit or time limit." in response_str:
            logger.error(f"Agent execution failed due to iteration/time limit. Raw response: {response_str}")
            return {
                "response": "I'm sorry, I'm having trouble processing your request right now. It seems like there was an issue with the underlying system. Could you please try again or rephrase your concern?",
                "options": ["Try again.", "Rephrase my concern.", "What happened?"],
                "cbt_technique": "system_error",
                "homework_assigned": "Take a moment to relax and try again later",
                "follow_up_needed": True
            }

        try:
            import json
            response_json = None
            json_str = None
            
            # First, try to parse the response directly, assuming it's clean JSON
            try:
                json_str = response_str.strip()
                response_json = json.loads(json_str)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON using regex
                json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```|(\{[\s\S]*?\})', response_str)
                
                if json_match:
                    if json_match.group(1): # Matched with ```json ... ``` block
                        json_str = json_match.group(1)
                    elif json_match.group(2): # Matched with a standalone {...} block
                        json_str = json_match.group(2)
                    response_json = json.loads(json_str)
            
            if response_json:
                return {
                    "response": response_json.get("response_text"),
                    "options": response_json.get("response_options", []),
                    "cbt_technique": cbt_focus,
                    "homework_assigned": self._get_homework_suggestion(cbt_focus),
                    "progress_tracking": self._get_progress_metrics(cbt_focus),
                    "follow_up_needed": True
                }
            else:
                logger.error(f"No valid JSON object found in agent's response after all attempts. Raw response: {response_str}")
                raise ValueError("No valid JSON object found in agent's response.")
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error in CBT therapist: {e}. Response string: {json_str if json_str else response_str}")
            return {
                "response": "I'm having a little trouble understanding your thoughts right now. Could you try rephrasing or focusing on one main concern?",
                "options": ["Yes, I can.", "I'm not sure.", "Where do I start?"],
                "cbt_technique": "clarification",
                "homework_assigned": "Reflect on the most pressing thought or feeling",
                "follow_up_needed": True
            }
        except ValueError as e: # Catch the specific ValueError for no JSON found
            logger.error(f"ValueError in CBT therapist: {e}. Raw response (repr): {repr(response_str)}")
            return {
                "response": "I'm having a little trouble processing that. It seems like the information isn't in the format I expected. Can you tell me more about what you're feeling?",
                "options": ["Yes, I can.", "I'm not sure.", "Where do I start?"],
                "cbt_technique": "clarification",
                "homework_assigned": "Describe your feelings in more detail",
                "follow_up_needed": True
            }
        except Exception as e:
            logger.error(f"General error in CBT therapist: {e}. Raw response (repr): {repr(response_str)}")
            return {
                "response": "I understand you're going through a difficult time. Let's work together to identify some thoughts and feelings you're experiencing. Can you tell me what thoughts are going through your mind right now?",
                "options": ["Yes, I can.", "I'm not sure.", "Where do I start?"],
                "cbt_technique": "thought_identification",
                "homework_assigned": "Keep a simple thought diary for the next day",
                "follow_up_needed": True
            }
    
    def get_capabilities(self) -> List[str]:
        return [
            "Cognitive distortion identification",
            "Thought challenging and reframing",
            "Behavioral activation planning",
            "Exposure therapy guidance",
            "Problem-solving skills training",
            "CBT homework assignments",
            "Progress tracking and monitoring"
        ]
    
    def get_tags(self) -> List[str]:
        return ["anxiety", "depression", "negative_thoughts", "behavioral_issues", "cbt", "cognitive_distortions"]
    
    def _determine_cbt_focus(self, tags: List[str], emotional_state: str) -> str:
        """Determine the most appropriate CBT intervention"""
        
        if "anxiety" in tags or emotional_state == "anxious":
            return "anxiety_management"
        elif "depression" in tags or emotional_state == "depressed":
            return "behavioral_activation"
        elif "negative_thoughts" in tags:
            return "thought_challenging"
        elif "panic" in tags:
            return "panic_management"
        elif "behavioral_issues" in tags:
            return "behavior_modification"
        else:
            return "general_cbt"
    
    def _get_homework_suggestion(self, cbt_focus: str) -> str:
        """Get appropriate homework assignment based on CBT focus"""
        
        homework_map = {
            "anxiety_management": "Practice the 4-7-8 breathing technique twice daily and record anxiety levels before/after",
            "behavioral_activation": "Schedule one pleasant activity for tomorrow and rate your mood before/after",
            "thought_challenging": "Complete a thought record when you notice negative thoughts, identifying evidence for/against",
            "panic_management": "Practice grounding techniques daily and create a panic attack action plan",
            "behavior_modification": "Track target behavior for 3 days and identify triggers/patterns",
            "general_cbt": "Keep a daily mood and thought diary, noting connections between thoughts and feelings"
        }
        
        return homework_map.get(cbt_focus, homework_map["general_cbt"])
    
    def _get_progress_metrics(self, cbt_focus: str) -> List[str]:
        """Get relevant progress tracking metrics"""
        
        metrics_map = {
            "anxiety_management": ["anxiety_level_1_10", "frequency_of_panic", "avoidance_behaviors"],
            "behavioral_activation": ["mood_rating", "activity_completion", "energy_levels"],
            "thought_challenging": ["negative_thought_frequency", "belief_in_thoughts", "alternative_thoughts_generated"],
            "panic_management": ["panic_attack_frequency", "panic_intensity", "recovery_time"],
            "behavior_modification": ["target_behavior_frequency", "trigger_identification", "coping_strategy_use"],
            "general_cbt": ["overall_mood", "coping_skill_usage", "goal_progress"]
        }
        
        return metrics_map.get(cbt_focus, metrics_map["general_cbt"])
