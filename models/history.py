"""
Recommendation History Data Models for PocketSmart AI.
Matches PDF pages 23-25.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class RecommendationHistoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().strftime("%b %d, %Y, %I:%M %p"))
    recommendation_type: str  # "home", "party", "jewelry"
    input_data: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)
    input_summary: str = ""
    result_summary: str = ""
