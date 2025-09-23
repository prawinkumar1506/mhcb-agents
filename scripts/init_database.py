"""
Initialize MongoDB with sample data for mental health chatbot
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from database.mongodb import init_db, get_database
# from models.schemas import Expert, Helpline
# from datetime import datetime

# async def create_sample_experts():
#     """Create sample expert data"""
#     db = await get_database()
    
#     experts = [
#         {
#             "expert_id": "E001",
#             "name": "Dr. Sarah Johnson",
#             "profession": "Student Counselor",
#             "tags": ["General", "Escalation", "Student Issues", "Academic Stress"],
#             "availability": True,
#             "contact_info": "sarah.johnson@university.edu"
#         },
#         {
#             "expert_id": "E002", 
#             "name": "Dr. Michael Chen",
#             "profession": "Clinical Psychologist",
#             "tags": ["CBT", "Anxiety", "Depression", "Cognitive Therapy"],
#             "availability": True,
#             "contact_info": "michael.chen@clinic.com"
#         },
#         {
#             "expert_id": "E003",
#             "name": "Dr. Priya Sharma",
#             "profession": "Mindfulness Coach",
#             "tags": ["Mindfulness", "Stress", "Sleep", "Meditation", "Lifestyle"],
#             "availability": True,
#             "contact_info": "priya.sharma@wellness.com"
#         },
#         {
#             "expert_id": "E004",
#             "name": "Dr. Robert Williams",
#             "profession": "Psychiatrist",
#             "tags": ["Severe Depression", "Bipolar", "Medication", "Crisis Intervention"],
#             "availability": True,
#             "contact_info": "robert.williams@hospital.com"
#         },
#         {
#             "expert_id": "E005",
#             "name": "Dr. Lisa Martinez",
#             "profession": "Relationship Counselor", 
#             "tags": ["Relationships", "Family", "Workplace", "Communication"],
#             "availability": True,
#             "contact_info": "lisa.martinez@therapy.com"
#         }
#     ]
    
#     # Clear existing experts
#     # await db.experts.delete_many({})
    
#     # Insert new experts
#     # result = await db.experts.insert_many(experts)
#     # print(f"Created {len(result.inserted_ids)} expert profiles")

# async def create_helplines():
#     """Create helpline data"""
#     db = await get_database()
    
#     helplines = [
#         {
#             "issue": "Suicidal Thoughts",
#             "number": "+91-9152987821",
#             "region": "India",
#             "description": "24/7 suicide prevention helpline"
#         },
#         {
#             "issue": "Mental Health Crisis",
#             "number": "1075",
#             "region": "India", 
#             "description": "Kiran Mental Health Helpline"
#         },
#         {
#             "issue": "Depression Support",
#             "number": "+91-80-25497777",
#             "region": "India",
#             "description": "Sneha India Foundation"
#         },
#         {
#             "issue": "Suicide Prevention",
#             "number": "988",
#             "region": "USA",
#             "description": "National Suicide Prevention Lifeline"
#         },
#         {
#             "issue": "Crisis Text Line",
#             "number": "741741",
#             "region": "USA",
#             "description": "Text HOME to 741741"
#         },
#         {
#             "issue": "Student Mental Health",
#             "number": "+91-9820466726",
#             "region": "India",
#             "description": "iCall Psychosocial Helpline"
#         }
#     ]
    
#     # Clear existing helplines
#     # await db.helplines.delete_many({})
    
#     # Insert new helplines
#     # result = await db.helplines.insert_many(helplines)
#     # print(f"Created {len(result.inserted_ids)} helpline entries")

# async def create_assessment_templates():
#     """Create assessment templates"""
#     db = await get_database()
    
#     assessments = [
#         {
#             "assessment_id": "GAD-7",
#             "name": "Generalized Anxiety Disorder 7-item",
#             "description": "Screening tool for anxiety disorders",
#             "questions": [
#                 "Feeling nervous, anxious, or on edge",
#                 "Not being able to stop or control worrying", 
#                 "Worrying too much about different things",
#                 "Trouble relaxing",
#                 "Being so restless that it is hard to sit still",
#                 "Becoming easily annoyed or irritable",
#                 "Feeling afraid, as if something awful might happen"
#             ],
#             "scoring": {
#                 "0-4": "Minimal anxiety",
#                 "5-9": "Mild anxiety", 
#                 "10-14": "Moderate anxiety",
#                 "15-21": "Severe anxiety"
#             }
#         },
#         {
#             "assessment_id": "PHQ-9",
#             "name": "Patient Health Questionnaire-9",
#             "description": "Depression screening tool",
#             "questions": [
#                 "Little interest or pleasure in doing things",
#                 "Feeling down, depressed, or hopeless",
#                 "Trouble falling or staying asleep, or sleeping too much",
#                 "Feeling tired or having little energy",
#                 "Poor appetite or overeating",
#                 "Feeling bad about yourself or that you are a failure",
#                 "Trouble concentrating on things",
#                 "Moving or speaking slowly or being fidgety/restless",
#                 "Thoughts that you would be better off dead or hurting yourself"
#             ],
#             "scoring": {
#                 "0-4": "Minimal depression",
#                 "5-9": "Mild depression",
#                 "10-14": "Moderate depression", 
#                 "15-19": "Moderately severe depression",
#                 "20-27": "Severe depression"
#             }
#         }
#     ]
    
#     # Clear existing assessments
#     # await db.assessments.delete_many({})
    
#     # Insert new assessments
#     # result = await db.assessments.insert_many(assessments)
#     # print(f"Created {len(result.inserted_ids)} assessment templates")

# async def create_coping_resources():
#     """Create coping resources and techniques"""
#     db = await get_database()
    
#     resources = [
#         {
#             "resource_id": "breathing-techniques",
#             "category": "Mindfulness",
#             "title": "Breathing Techniques for Anxiety",
#             "description": "Simple breathing exercises to manage anxiety",
#             "techniques": [
#                 {
#                     "name": "4-7-8 Breathing",
#                     "steps": [
#                         "Inhale through nose for 4 counts",
#                         "Hold breath for 7 counts", 
#                         "Exhale through mouth for 8 counts",
#                         "Repeat 3-4 times"
#                     ]
#                 },
#                 {
#                     "name": "Box Breathing",
#                     "steps": [
#                         "Inhale for 4 counts",
#                         "Hold for 4 counts",
#                         "Exhale for 4 counts", 
#                         "Hold for 4 counts",
#                         "Repeat for 2-3 minutes"
#                     ]
#                 }
#             ],
#             "tags": ["anxiety", "stress", "mindfulness"]
#         },
#         {
#             "resource_id": "cbt-techniques",
#             "category": "CBT",
#             "title": "Cognitive Behavioral Techniques",
#             "description": "Thought reframing and behavioral strategies",
#             "techniques": [
#                 {
#                     "name": "Thought Record",
#                     "steps": [
#                         "Identify the triggering situation",
#                         "Notice your automatic thoughts",
#                         "Identify emotions and their intensity",
#                         "Examine evidence for and against the thought",
#                         "Create a balanced, realistic thought"
#                     ]
#                 },
#                 {
#                     "name": "Behavioral Activation",
#                     "steps": [
#                         "List activities you used to enjoy",
#                         "Rate each activity's potential pleasure (1-10)",
#                         "Schedule one small activity for today",
#                         "Complete the activity regardless of mood",
#                         "Rate actual pleasure experienced"
#                     ]
#                 }
#             ],
#             "tags": ["depression", "anxiety", "cbt", "negative-thoughts"]
#         },
#         {
#             "resource_id": "grounding-techniques",
#             "category": "Crisis Management",
#             "title": "Grounding Techniques for Panic",
#             "description": "Techniques to manage panic attacks and overwhelming emotions",
#             "techniques": [
#                 {
#                     "name": "5-4-3-2-1 Technique",
#                     "steps": [
#                         "Name 5 things you can see",
#                         "Name 4 things you can touch",
#                         "Name 3 things you can hear",
#                         "Name 2 things you can smell",
#                         "Name 1 thing you can taste"
#                     ]
#                 },
#                 {
#                     "name": "Progressive Muscle Relaxation",
#                     "steps": [
#                         "Start with your toes, tense for 5 seconds",
#                         "Release and notice the relaxation",
#                         "Move up to calves, thighs, abdomen",
#                         "Continue through arms, shoulders, face",
#                         "End with whole body relaxation"
#                     ]
#                 }
#             ],
#             "tags": ["panic", "crisis", "grounding", "anxiety"]
#         }
#     ]
    
#     # Clear existing resources
#     # await db.resources.delete_many({})
    
#     # Insert new resources
#     # result = await db.resources.insert_many(resources)
#     # print(f"Created {len(result.inserted_ids)} coping resources")

# async def main():
#     """Initialize database with all sample data"""
#     print("Initializing Mental Health Chatbot Database...")
    
#     try:
#         # Initialize database connection
#         # await init_db()
#         print("✓ Database connection established")
        
#         # Create sample data
#         # await create_sample_experts()
#         print("✓ Expert profiles created")
        
#         # await create_helplines()
#         print("✓ Helpline numbers added")
        
#         # await create_assessment_templates()
#         print("✓ Assessment templates created")
        
#         # await create_coping_resources()
#         print("✓ Coping resources added")
        
#         print("\n🎉 Database initialization completed successfully!")
#         print("The mental health chatbot database is ready to use.")
        
#     except Exception as e:
#         print(f"❌ Error initializing database: {e}")
#         return False
    
#     return True

# if __name__ == "__main__":
#     asyncio.run(main())
