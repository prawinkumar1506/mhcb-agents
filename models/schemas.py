from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserStyle(str, Enum):
    FORMAL = "formal"
    GENZ = "genz"
    EMPATHETIC = "empathetic"
    CLINICAL = "clinical"

class Language(str, Enum):
    ENGLISH = "English"
    HINDI = "Hindi"
    TAMIL = "Tamil"
    SPANISH = "Spanish"

class AgentType(str, Enum):
    CONVERSATION_MANAGER = "conversation_manager"
    CBT_THERAPIST = "cbt_therapist"
    MINDFULNESS_COACH = "mindfulness_coach"
    PSYCHIATRIST = "psychiatrist"
    RELATIONSHIP_COUNSELOR = "relationship_counselor"
    BOOKING_AGENT = "booking_agent"

class MessageRole(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_type: Optional[AgentType] = None

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None
    language: Optional[Language] = Language.ENGLISH

class ChatResponse(BaseModel):
    response: str
    agent_type: AgentType
    detected_tags: List[str]
    escalation_needed: bool = False
    helpline_numbers: Optional[Dict[str, str]] = None
    suggested_resources: Optional[List[str]] = None
    session_id: str

class User(BaseModel):
    user_id: str
    name: Optional[str] = None
    language: Language = Language.ENGLISH
    preferred_style: UserStyle = UserStyle.EMPATHETIC
    history: List[str] = []
    last_session: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Expert(BaseModel):
    expert_id: str
    name: str
    profession: str
    tags: List[str]
    availability: bool = True
    contact_info: Optional[str] = None

class Helpline(BaseModel):
    issue: str
    number: str
    region: str
    description: Optional[str] = None

class Conversation(BaseModel):
    conversation_id: str
    user_id: str
    messages: List[ChatMessage]
    detected_tags: List[str]
    session_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BookingRequest(BaseModel):
    user_id: str
    expert_type: str = "student_counselor"
    preferred_time: Optional[str] = None
    urgency_level: str = "normal"  # normal, urgent, crisis
    notes: Optional[str] = None

class AssessmentResult(BaseModel):
    user_id: str
    assessment_type: str  # GAD-7, PHQ-9, etc.
    score: int
    severity_level: str
    recommendations: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
