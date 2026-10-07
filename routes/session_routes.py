"""
Session Management Routes for PocketSmart AI.
Matches PDF page 20.
"""
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Request, Depends, HTTPException, status
from models.user import UserInDB
from services.auth_service import get_current_active_user, active_sessions

router = APIRouter()


@router.get("/session-info")
async def get_session_info(
    request: Request,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Retrieves metadata about current user session."""
    if current_user.username in active_sessions:
        session = active_sessions[current_user.username]
        duration_minutes = (datetime.utcnow() - session.login_time).total_seconds() // 60
        return {
            "username": session.username,
            "login_time": session.login_time.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "session_duration": int(duration_minutes),
            "user_data": session.user_data,
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active session found")


@router.post("/session-data")
async def update_session_data(
    data: Dict[str, Any],
    request: Request,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Updates user session data for personalized AI interaction."""
    if current_user.username in active_sessions:
        active_sessions[current_user.username].user_data.update(data)
        active_sessions[current_user.username].last_activity = datetime.utcnow()
        return {
            "message": "Session data updated",
            "data": active_sessions[current_user.username].user_data,
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active session found")
