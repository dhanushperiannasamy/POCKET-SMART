"""
Session Data Models for PocketSmart AI.
Matches PDF page 20.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserSession(BaseModel):
    username: str
    login_time: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    token: Optional[str] = None
    user_data: Dict[str, Any] = Field(default_factory=dict)
