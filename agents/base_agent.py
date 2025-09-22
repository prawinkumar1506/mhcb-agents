"""
Base agent class for mental health chatbot agents
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all mental health agents"""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        
        # Initialize Gemini LLM for CrewAI
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7
        )
        
        # Create CrewAI agent
        self.agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process user message and return response"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass
    
    @abstractmethod
    def get_tags(self) -> List[str]:
        """Return list of tags this agent handles"""
        pass
    
    def create_task(self, description: str, expected_output: str) -> Task:
        """Create a CrewAI task for this agent"""
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent
        )
    
    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> str:
        """Execute a task using CrewAI"""
        try:
            task = self.create_task(
                description=task_description,
                expected_output="A helpful, empathetic response addressing the user's concerns"
            )
            
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            logger.error(f"Error executing task for {self.name}: {e}")
            return "I'm here to help. Could you tell me more about what you're experiencing?"
