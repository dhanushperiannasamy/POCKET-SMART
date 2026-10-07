"""
Party Budget Planner Schemas for PocketSmart AI.
Matches PDF pages 13-16.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PartyBudgetInput(BaseModel):
    total_budget: float = Field(..., gt=0, description="Total budget in INR")
    party_type: str = Field(..., min_length=1, description="Event type: Birthday, Wedding, Corporate, etc.")
    num_guests: int = Field(..., gt=0, description="Number of guests")
    venue_type: Optional[str] = Field(default="Not specified", description="Venue type")
    needs_catering: bool = Field(default=True, description="Catering required")
    needs_decoration: bool = Field(default=True, description="Decoration required")
    needs_entertainment: bool = Field(default=True, description="Entertainment required")
    additional_requirements: Optional[str] = Field(default=None, description="Special requests or theme")


class PartyBudgetItem(BaseModel):
    name: str
    description: str
    estimated_price: float
    quantity: int = 1
    search_terms: str
    shopping_links: Optional[Dict[str, str]] = None


class PartyBudgetCategory(BaseModel):
    category: str
    allocation: float
    items: List[PartyBudgetItem] = []


class VenueSuggestion(BaseModel):
    name: str
    type: str
    capacity: int
    estimated_cost: float
    search_terms: str
    search_links: Optional[Dict[str, str]] = None


class PartyCalculationRow(BaseModel):
    category: str
    items_count: int
    total_cost: float
    percentage_of_budget: float


class PartyBudgetResponse(BaseModel):
    total_budget: float
    budget_breakdown: List[PartyBudgetCategory]
    venue_suggestions: List[VenueSuggestion] = []
    calculation_table_inr: List[PartyCalculationRow] = []
    remaining_budget: float
    additional_suggestions: List[str] = []
