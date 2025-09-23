"""
Booking router for appointment scheduling and escalation
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from models.schemas import BookingRequest, Expert
# from database.collections import BookingCollection, ExpertCollection
from services.escalation_service import escalation_service
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv
from email.message import EmailMessage
import ssl # Import ssl module
from aiosmtplib import SMTP
from config.settings import settings # Import the settings object

load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter()

bookings = {} # In-memory storage for bookings

async def send_email(to_email: str, subject: str, body: str):
    """Sends an email using aiosmtplib."""
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD or not settings.MAIL_SERVER or not settings.MAIL_PORT:
        logger.error("Email configuration is incomplete. Cannot send email.")
        raise ValueError("Email configuration is incomplete.")

    message = EmailMessage()
    message["From"] = settings.MAIL_USERNAME
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        # Create a custom SSL context to explicitly set minimum TLS version
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2 # Ensure TLS 1.2 or higher
        context.check_hostname = True # Explicitly enable hostname checking

        smtp = SMTP(
            hostname=settings.MAIL_SERVER,
            port=settings.MAIL_PORT,
            start_tls=True,    # Use STARTTLS for port 587
            use_tls=False,     # Do not use implicit TLS here
            tls_context=context,
            validate_certs=True
        )
        await smtp.connect()
        await smtp.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        await smtp.send_message(message)
        await smtp.quit()
        logger.info(f"Email sent successfully to {to_email} with subject '{subject}'")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise

async def send_confirmation(student_email: str, slot_dt_str: str):
    """Sends a confirmation email."""
    subject = "Counselling Confirmation"
    body = f"Your counselling session is confirmed for {slot_dt_str}."
    await send_email(student_email, subject, body)

async def send_reminder(student_email: str, slot_dt_str: str):
    """Sends a reminder email."""
    subject = "Counselling Reminder"
    body = f"Reminder: Your counselling session is at {slot_dt_str}."
    await send_email(student_email, subject, body)

@router.post("/request")
async def create_booking_request(booking: BookingRequest):
    """Create a new booking request"""
    
    try:
        # success = await BookingCollection.create_booking(booking)
        success = False # Mock success since MongoDB is commented out
        
        if success:
            # Trigger escalation if urgent
            if booking.urgency_level in ["crisis", "urgent"]:
                escalation_context = {
                    "detected_tags": ["booking_request"],
                    "urgency_level": booking.urgency_level,
                    "expert_type": booking.expert_type,
                    "notes": booking.notes
                }
                
                await escalation_service.trigger_escalation(
                    booking.user_id,
                    booking.urgency_level,
                    escalation_context,
                    f"Booking request: {booking.notes}"
                )
            
            return {
                "message": "Booking request created successfully",
                "booking_id": f"BOOK_{booking.user_id}_{int(datetime.utcnow().timestamp())}",
                "urgency_level": booking.urgency_level,
                "escalation_triggered": booking.urgency_level in ["crisis", "urgent"]
            }
        else:
            # raise HTTPException(status_code=500, detail="Failed to create booking request")
            return {
                "message": "Booking request not created (MongoDB commented out)",
                "booking_id": f"MOCK_BOOK_{booking.user_id}_{int(datetime.utcnow().timestamp())}",
                "urgency_level": booking.urgency_level,
                "escalation_triggered": booking.urgency_level in ["crisis", "urgent"]
            }
            
    except Exception as e:
        logger.error(f"Error creating booking request: {e}")
        raise HTTPException(status_code=500, detail="Error processing booking request")

@router.get("/experts/available")
async def get_available_experts(specialties: Optional[List[str]] = None):
    """Get available experts, optionally filtered by specialties"""
    
    try:
        # experts = await ExpertCollection.get_available_experts(specialties)
        # Mock empty list since MongoDB is commented out
        experts = []
        
        return {
            "experts": [
                # {
                #     "expert_id": expert.expert_id,
                #     "name": expert.name,
                #     "profession": expert.profession,
                #     "specialties": expert.tags,
                #     "availability": expert.availability
                # }
                # for expert in experts
            ],
            "total_available": len(experts),
            "filtered_by": specialties or []
        }
        
    except Exception as e:
        logger.error(f"Error getting available experts: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving expert information")

@router.post("/escalate")
async def trigger_manual_escalation(escalation_request: Dict[str, Any]):
    """Manually trigger escalation for a user"""
    
    try:
        user_id = escalation_request.get("user_id")
        level = escalation_request.get("level", "normal")
        context = escalation_request.get("context", {})
        message = escalation_request.get("message", "")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        if level not in ["crisis", "urgent", "high", "normal"]:
            raise HTTPException(status_code=400, detail="Invalid escalation level")
        
        result = await escalation_service.trigger_escalation(user_id, level, context, message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering manual escalation: {e}")
        raise HTTPException(status_code=500, detail="Error processing escalation request")

@router.get("/bookings/{user_id}")
async def get_user_bookings(user_id: str):
    """Get booking history for a user"""
    
    try:
        # from database.mongodb import get_database
        # db = await get_database()
        
        # cursor = db.bookings.find({"user_id": user_id}).sort("created_at", -1)
        bookings = []
        # Mock data since MongoDB is commented out
        bookings.append({
            "booking_id": "MOCK_BOOK_123",
            "expert_type": "student_counselor",
            "urgency_level": "normal",
            "status": "pending",
            "created_at": datetime.utcnow(),
            "notes": "Mock booking from commented out MongoDB"
        })
        
        # async for booking in cursor:
        #     bookings.append({
        #         "booking_id": str(booking.get("_id", "")),
        #         "expert_type": booking.get("expert_type", ""),
        #         "urgency_level": booking.get("urgency_level", ""),
        #         "status": booking.get("status", "pending"),
        #         "created_at": booking.get("created_at", ""),
        #         "notes": booking.get("notes", "")
        #     })
        
        return {
            "user_id": user_id,
            "bookings": bookings,
            "total_bookings": len(bookings)
        }
        
    except Exception as e:
        logger.error(f"Error getting user bookings: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving booking history")

@router.get("/escalations/{user_id}")
async def get_user_escalations(user_id: str):
    """Get escalation history for a user"""
    
    try:
        # from database.mongodb import get_database
        # db = await get_database()
        
        cursor = db.escalations.find({"user_id": user_id}).sort("triggered_at", -1)
        escalations = []
        
        async for escalation in cursor:
            escalations.append({
                "escalation_id": escalation.get("escalation_id", ""),
                "level": escalation.get("level", ""),
                "status": escalation.get("status", ""),
                "triggered_at": escalation.get("triggered_at", ""),
                "actions_taken": escalation.get("actions_taken", {}),
                "expected_response_by": escalation.get("expected_response_by", "")
            })
        
        return {
            "user_id": user_id,
            "escalations": escalations,
            "total_escalations": len(escalations)
        }
        
    except Exception as e:
        logger.error(f"Error getting user escalations: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving escalation history")

@router.put("/booking/{booking_id}/status")
async def update_booking_status(booking_id: str, status_update: Dict[str, str]):
    """Update booking status (for counselor/admin use)"""
    
    try:
        new_status = status_update.get("status")
        notes = status_update.get("notes", "")
        
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        valid_statuses = ["pending", "confirmed", "in_progress", "completed", "cancelled"]
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # from database.mongodb import get_database
        # db = await get_database()
        
        # result = await db.bookings.update_one(
        #     {"booking_id": booking_id},
        #     {
        #         "$set": {
        #             "status": new_status,
        #             "updated_at": datetime.utcnow(),
        #             "status_notes": notes
        #         }
        #     }
        # )
        
        # if result.modified_count == 0:
        #     raise HTTPException(status_code=404, detail="Booking not found")
        
        return {
            "booking_id": booking_id,
            "status": new_status,
            "updated_at": datetime.utcnow(),
            "message": "Booking status updated successfully (mocked)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating booking status: {e}")
        raise HTTPException(status_code=500, detail="Error updating booking status")

@router.get("/stats/escalations")
async def get_escalation_stats():
    """Get escalation statistics (for admin/monitoring)"""
    
    try:
        # from database.mongodb import get_database
        # db = await get_database()
        
        # Get escalation counts by level
        pipeline = [
            {
                "$group": {
                    "_id": "$level",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        cursor = db.escalations.aggregate(pipeline)
        level_counts = {}
        
        async for result in cursor:
            level_counts[result["_id"]] = result["count"]
        
        # Get recent escalations (last 24 hours)
        recent_escalations = await db.escalations.count_documents({
            "triggered_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
        })
        
        # Get active escalations
        active_escalations = await db.escalations.count_documents({
            "status": "active"
        })
        
        return {
            "escalation_counts_by_level": level_counts,
            "recent_escalations_24h": recent_escalations,
            "active_escalations": active_escalations,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting escalation stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving escalation statistics")
