"""
Home Interior Budget Planner Schemas for PocketSmart AI.
Matches PDF page 12.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class HomeBudgetInput(BaseModel):
    total_budget: float = Field(..., gt=0, description="Total budget in INR")
    num_lights: int = Field(default=0, ge=0, description="Number of lights/fixtures")
    num_fans: int = Field(default=0, ge=0, description="Number of ceiling fans")
    num_furniture: int = Field(default=0, ge=0, description="Number of furniture pieces")
    num_dining_tables: int = Field(default=0, ge=0, description="Number of dining tables")
    has_living_room: bool = Field(default=True, description="Living room included")
    has_kitchen: bool = Field(default=False, description="Kitchen included")
    has_bedroom: bool = Field(default=False, description="Bedroom included")
    additional_requirements: Optional[str] = Field(default=None, description="Custom requirements or styles")


class HomeBudgetItem(BaseModel):
    name: str
    description: str
    estimated_price: float
    quantity: int = 1
    search_terms: str
    shopping_links: Optional[Dict[str, str]] = None


class HomeBudgetCategory(BaseModel):
    category: str
    allocation: float
    items: List[HomeBudgetItem] = []


class HomeCalculationRow(BaseModel):
    category: str
    items_count: int
    total_cost: float
    percentage_of_budget: float


class HomeBudgetResponse(BaseModel):
    total_budget: float
    budget_breakdown: List[HomeBudgetCategory]
    calculation_table: List[HomeCalculationRow]
    remaining_budget: float
    additional_suggestions: List[str] = []
