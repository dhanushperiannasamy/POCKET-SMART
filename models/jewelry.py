"""
Jewelry Budget Planner Schemas for PocketSmart AI.
Matches PDF pages 16-17.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class JewelryBudgetInput(BaseModel):
    total_budget: float = Field(..., gt=0, description="Total budget in INR")
    occasion: str = Field(..., min_length=1, description="Occasion: Wedding, Birthday, etc.")
    preferences: Optional[str] = Field(default="Not specified", description="Style preferences")
    image_path: Optional[str] = Field(default=None, description="Path to uploaded outfit image")


class OutfitAnalysis(BaseModel):
    colors: List[str] = []
    style: str = ""
    formality: str = ""


class JewelryItem(BaseModel):
    item_type: str
    description: str
    style: str
    estimated_price: float
    search_terms: str
    shopping_links: Optional[Dict[str, str]] = None


class JewelryBudgetResponse(BaseModel):
    total_budget: float
    outfit_analysis: Optional[OutfitAnalysis] = None
    jewelry_recommendations: List[JewelryItem] = []
    remaining_budget: float
    styling_tips: List[str] = []
