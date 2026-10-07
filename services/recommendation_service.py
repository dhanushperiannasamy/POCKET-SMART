"""
Recommendation Service coordinating AI calls, platform integration, and history tracking.
"""
from typing import Optional, Dict, Any
from gemini_utils import (
    get_home_recommendations,
    get_party_recommendations,
    get_jewelry_recommendations,
)
from services.history_service import save_to_history


def process_home_plan(username: str, budget_input) -> Dict[str, Any]:
    result = get_home_recommendations(budget_input)
    save_to_history(
        username=username,
        recommendation_type="home",
        input_data=budget_input.dict(),
        result=result
    )
    return result


def process_party_plan(username: str, budget_input) -> Dict[str, Any]:
    result = get_party_recommendations(budget_input)
    save_to_history(
        username=username,
        recommendation_type="party",
        input_data=budget_input.dict(),
        result=result
    )
    return result


def process_jewelry_plan(username: str, budget_input, image_path: Optional[str] = None, image_filename: Optional[str] = None) -> Dict[str, Any]:
    result = get_jewelry_recommendations(budget_input, image_path)
    input_dict = budget_input.dict()
    if image_filename:
        input_dict["image"] = image_filename
        input_dict["has_image"] = True
    save_to_history(
        username=username,
        recommendation_type="jewelry",
        input_data=input_dict,
        result=result
    )
    return result
