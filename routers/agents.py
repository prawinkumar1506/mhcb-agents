"""
Agents router for agent-specific endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from agents.agent_orchestrator import agent_orchestrator
from database.collections import ExpertCollection
from models.schemas import Expert
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/available")
async def get_available_agents():
    """Get list of available agents and their capabilities"""
    
    try:
        agents_info = {}
        
        for agent_type, agent in agent_orchestrator.agents.items():
            agents_info[agent_type] = {
                "name": agent.name,
                "role": agent.role,
                "capabilities": agent.get_capabilities(),
                "tags": agent.get_tags(),
                "priority": agent_orchestrator.agent_priority.get(agent_type, 5)
            }
        
        return {
            "agents": agents_info,
            "total_agents": len(agents_info)
        }
        
    except Exception as e:
        logger.error(f"Error getting available agents: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving agent information")

@router.get("/experts")
async def get_available_experts(tags: List[str] = None):
    """Get available human experts"""
    
    try:
        experts = await ExpertCollection.get_available_experts(tags)
        return {
            "experts": [expert.model_dump() for expert in experts],
            "total_experts": len(experts)
        }
        
    except Exception as e:
        logger.error(f"Error getting experts: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving expert information")

@router.post("/route")
async def route_to_agent(request: Dict[str, Any]):
    """Route message to specific agent for testing"""
    
    try:
        message = request.get("message", "")
        agent_type = request.get("agent_type", "conversation_manager")
        user_id = request.get("user_id", "test_user")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Mock analysis for testing
        mock_analysis = {
            "emotional_state": request.get("emotional_state", "neutral"),
            "detected_tags": request.get("detected_tags", []),
            "communication_style": request.get("communication_style", "empathetic"),
            "language": request.get("language", "English"),
            "recommended_agent": agent_type
        }
        
        # Process with agent orchestrator
        response_data = await agent_orchestrator.process_conversation(
            message, user_id, mock_analysis
        )
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error routing to agent: {e}")
        raise HTTPException(status_code=500, detail="Error processing agent request")

@router.get("/agent/{agent_type}/info")
async def get_agent_info(agent_type: str):
    """Get detailed information about a specific agent"""
    
    try:
        if agent_type not in agent_orchestrator.agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent = agent_orchestrator.agents[agent_type]
        
        return {
            "agent_type": agent_type,
            "name": agent.name,
            "role": agent.role,
            "goal": agent.goal,
            "backstory": agent.backstory,
            "capabilities": agent.get_capabilities(),
            "tags": agent.get_tags(),
            "priority": agent_orchestrator.agent_priority.get(agent_type, 5)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving agent information")
