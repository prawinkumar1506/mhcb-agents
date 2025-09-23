"""
Additional seed data for mental health chatbot
"""
import asyncio
# from database.mongodb import get_database
from datetime import datetime

async def create_conversation_templates():
    """Create conversation templates for different scenarios"""
    # db = await get_database()
    
    templates = [
        {
            "template_id": "anxiety_greeting",
            "agent_type": "conversation_manager",
            "triggers": ["anxiety", "worried", "nervous", "panic"],
            "responses": {
                "formal": "I understand you're experiencing anxiety. I'm here to help you work through these feelings. Would you like to try some immediate coping techniques, or would you prefer to talk about what's causing your anxiety?",
                "genz": "Hey, I can see you're feeling anxious rn. That's totally valid and you're not alone in this. Want to try some quick anxiety hacks, or do you wanna talk about what's got you stressed?",
                "empathetic": "I hear that you're feeling anxious, and I want you to know that what you're experiencing is real and valid. You've taken a brave step by reaching out. How can I best support you right now?",
                "clinical": "You've indicated symptoms consistent with anxiety. Let's work together to identify effective coping strategies. Would you prefer cognitive techniques or somatic interventions to begin with?"
            }
        },
        {
            "template_id": "depression_greeting", 
            "agent_type": "conversation_manager",
            "triggers": ["depressed", "sad", "hopeless", "empty", "worthless"],
            "responses": {
                "formal": "Thank you for sharing that you're feeling depressed. Depression is a serious condition, but there are effective ways to manage it. I'm here to provide support and guidance. What would be most helpful for you right now?",
                "genz": "I'm really glad you reached out about feeling depressed. That takes courage, and I'm here for you. Depression is tough but you don't have to face it alone. What's been the hardest part lately?",
                "empathetic": "I'm so sorry you're going through this difficult time. Depression can feel overwhelming, but please know that you matter and there is hope. I'm here to listen and support you. What feels most important to address first?",
                "clinical": "You've reported symptoms suggestive of depression. This is a treatable condition with evidence-based interventions available. Shall we begin with a brief assessment to better understand your current state and develop an appropriate support plan?"
            }
        },
        {
            "template_id": "crisis_response",
            "agent_type": "booking_agent",
            "triggers": ["suicide", "kill myself", "end it all", "don't want to live", "hurt myself"],
            "responses": {
                "immediate": "I'm very concerned about what you've shared. Your life has value and there are people who want to help you right now. Please reach out to a crisis helpline immediately:",
                "helplines": {
                    "India": "+91-9152987821 (24/7 Suicide Prevention)",
                    "USA": "988 (National Suicide Prevention Lifeline)",
                    "Emergency": "If you're in immediate danger, please call emergency services (911/112)"
                },
                "follow_up": "I'm also connecting you with a counselor who can provide immediate support. You don't have to go through this alone."
            }
        }
    ]
    
    # Clear existing templates
    # await db.conversation_templates.delete_many({})
    
    # Insert new templates
    # result = await db.conversation_templates.insert_many(templates)
    # print(f"Created {len(result.inserted_ids)} conversation templates")

async def create_agent_configurations():
    """Create agent configuration data"""
    # db = await get_database()
    
    agent_configs = [
        {
            "agent_type": "conversation_manager",
            "name": "Conversation Manager",
            "description": "Routes conversations and adapts communication style",
            "capabilities": [
                "Intent detection",
                "Emotional state analysis", 
                "Style adaptation",
                "Language detection",
                "Agent routing"
            ],
            "tags": ["general", "routing", "multilingual", "adaptation"],
            "priority": 1
        },
        {
            "agent_type": "cbt_therapist",
            "name": "CBT Therapist",
            "description": "Provides cognitive behavioral therapy techniques",
            "capabilities": [
                "Thought pattern analysis",
                "Cognitive restructuring",
                "Behavioral activation",
                "Homework assignments",
                "Progress tracking"
            ],
            "tags": ["anxiety", "depression", "negative-thoughts", "behavioral-issues"],
            "priority": 2
        },
        {
            "agent_type": "mindfulness_coach",
            "name": "Mindfulness Coach", 
            "description": "Teaches mindfulness and stress management techniques",
            "capabilities": [
                "Meditation guidance",
                "Breathing exercises",
                "Grounding techniques",
                "Sleep hygiene",
                "Lifestyle coaching"
            ],
            "tags": ["stress", "sleep", "focus", "lifestyle", "mindfulness"],
            "priority": 2
        },
        {
            "agent_type": "psychiatrist",
            "name": "Psychiatrist Consultant",
            "description": "Identifies need for medical evaluation",
            "capabilities": [
                "Symptom assessment",
                "Medication consultation referral",
                "Crisis identification",
                "Medical history review",
                "Professional referrals"
            ],
            "tags": ["severe-depression", "bipolar", "medication", "crisis"],
            "priority": 3
        },
        {
            "agent_type": "relationship_counselor",
            "name": "Relationship Counselor",
            "description": "Provides relationship and interpersonal guidance",
            "capabilities": [
                "Communication skills",
                "Conflict resolution",
                "Boundary setting",
                "Family dynamics",
                "Workplace relationships"
            ],
            "tags": ["relationships", "family", "workplace", "communication"],
            "priority": 2
        },
        {
            "agent_type": "booking_agent",
            "name": "Booking Agent",
            "description": "Handles escalation and appointment scheduling",
            "capabilities": [
                "Crisis detection",
                "Helpline routing",
                "Appointment scheduling",
                "Escalation management",
                "Emergency protocols"
            ],
            "tags": ["appointment", "escalation", "crisis", "emergency"],
            "priority": 4
        }
    ]
    
    # Clear existing configurations
    # await db.agent_configs.delete_many({})
    
    # Insert new configurations
    # result = await db.agent_configs.insert_many(agent_configs)
    # print(f"Created {len(result.inserted_ids)} agent configurations")

async def main():
    """Seed additional database data"""
    print("Seeding additional database data...")
    
    try:
        await create_conversation_templates()
        print("✓ Conversation templates created")
        
        await create_agent_configurations()
        print("✓ Agent configurations created")
        
        print("\n🌱 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())
