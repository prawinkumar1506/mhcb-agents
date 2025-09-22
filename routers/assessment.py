"""
Assessment router for mental health assessments
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from database.mongodb import get_database
from models.schemas import AssessmentResult
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/available")
async def get_available_assessments():
    """Get list of available mental health assessments"""
    
    try:
        db = await get_database()
        cursor = db.assessments.find({})
        assessments = []
        
        async for assessment in cursor:
            assessments.append({
                "assessment_id": assessment["assessment_id"],
                "name": assessment["name"],
                "description": assessment["description"],
                "question_count": len(assessment["questions"])
            })
        
        return {
            "assessments": assessments,
            "total_assessments": len(assessments)
        }
        
    except Exception as e:
        logger.error(f"Error getting assessments: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving assessments")

@router.get("/assessment/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Get specific assessment details"""
    
    try:
        db = await get_database()
        assessment = await db.assessments.find_one({"assessment_id": assessment_id})
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        return assessment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assessment: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving assessment")

@router.post("/assessment/{assessment_id}/submit")
async def submit_assessment(assessment_id: str, submission: Dict[str, Any]):
    """Submit assessment responses and get results"""
    
    try:
        user_id = submission.get("user_id")
        responses = submission.get("responses", [])
        
        if not user_id or not responses:
            raise HTTPException(status_code=400, detail="User ID and responses are required")
        
        # Get assessment details
        db = await get_database()
        assessment = await db.assessments.find_one({"assessment_id": assessment_id})
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Calculate score
        total_score = sum(responses)
        
        # Determine severity level based on scoring
        severity_level = _determine_severity_level(assessment_id, total_score, assessment.get("scoring", {}))
        
        # Generate recommendations
        recommendations = _generate_recommendations(assessment_id, severity_level, total_score)
        
        # Create assessment result
        result = AssessmentResult(
            user_id=user_id,
            assessment_type=assessment_id,
            score=total_score,
            severity_level=severity_level,
            recommendations=recommendations
        )
        
        # Save result to database
        await db.assessment_results.insert_one(result.model_dump())
        
        return {
            "assessment_id": assessment_id,
            "score": total_score,
            "severity_level": severity_level,
            "recommendations": recommendations,
            "next_steps": _get_next_steps(severity_level, assessment_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting assessment: {e}")
        raise HTTPException(status_code=500, detail="Error processing assessment")

@router.get("/results/{user_id}")
async def get_user_assessment_results(user_id: str, limit: int = 10):
    """Get user's assessment history"""
    
    try:
        db = await get_database()
        cursor = db.assessment_results.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        
        results = []
        async for result in cursor:
            results.append(result)
        
        return {
            "user_id": user_id,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error getting assessment results: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving assessment results")

def _determine_severity_level(assessment_id: str, score: int, scoring: Dict[str, str]) -> str:
    """Determine severity level based on assessment score"""
    
    # Convert scoring ranges to numeric comparisons
    for range_str, level in scoring.items():
        if "-" in range_str:
            min_score, max_score = map(int, range_str.split("-"))
            if min_score <= score <= max_score:
                return level
    
    # Default severity levels based on common assessments
    if assessment_id == "GAD-7":
        if score <= 4:
            return "Minimal anxiety"
        elif score <= 9:
            return "Mild anxiety"
        elif score <= 14:
            return "Moderate anxiety"
        else:
            return "Severe anxiety"
    elif assessment_id == "PHQ-9":
        if score <= 4:
            return "Minimal depression"
        elif score <= 9:
            return "Mild depression"
        elif score <= 14:
            return "Moderate depression"
        elif score <= 19:
            return "Moderately severe depression"
        else:
            return "Severe depression"
    
    return "Unknown"

def _generate_recommendations(assessment_id: str, severity_level: str, score: int) -> List[str]:
    """Generate recommendations based on assessment results"""
    
    recommendations = []
    
    if "severe" in severity_level.lower():
        recommendations.extend([
            "Consider speaking with a mental health professional",
            "Contact a crisis helpline if you're having thoughts of self-harm",
            "Reach out to trusted friends or family for support"
        ])
    elif "moderate" in severity_level.lower():
        recommendations.extend([
            "Practice stress management techniques daily",
            "Consider counseling or therapy",
            "Maintain regular sleep and exercise routines"
        ])
    elif "mild" in severity_level.lower():
        recommendations.extend([
            "Try relaxation techniques like deep breathing",
            "Engage in regular physical activity",
            "Practice mindfulness or meditation"
        ])
    else:
        recommendations.extend([
            "Continue healthy lifestyle habits",
            "Stay connected with supportive people",
            "Monitor your mental health regularly"
        ])
    
    # Add assessment-specific recommendations
    if assessment_id == "GAD-7":
        recommendations.append("Practice anxiety management techniques")
    elif assessment_id == "PHQ-9":
        recommendations.append("Focus on behavioral activation and pleasant activities")
    
    return recommendations

def _get_next_steps(severity_level: str, assessment_id: str) -> List[str]:
    """Get next steps based on severity level"""
    
    if "severe" in severity_level.lower():
        return [
            "Schedule appointment with counselor",
            "Contact crisis support if needed",
            "Implement immediate coping strategies"
        ]
    elif "moderate" in severity_level.lower():
        return [
            "Try recommended coping techniques",
            "Consider professional support",
            "Monitor symptoms daily"
        ]
    else:
        return [
            "Practice self-care techniques",
            "Continue monitoring symptoms",
            "Maintain healthy routines"
        ]
