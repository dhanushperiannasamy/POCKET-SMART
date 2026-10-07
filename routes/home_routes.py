"""
Home Interior Budget Planner Routes for PocketSmart AI.
Matches PDF pages 11-13, 21.
"""
from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from typing import Optional
from models.home import HomeBudgetInput
from models.user import UserInDB
from services.auth_service import get_optional_current_user, active_sessions
from services.history_service import save_to_history
from gemini_utils import get_home_recommendations

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/home-budget", response_class=HTMLResponse)
@router.get("/home-planner", response_class=HTMLResponse)
async def home_planner(
    request: Request,
    current_user: Optional[UserInDB] = Depends(get_optional_current_user)
):
    """Serve the Home Budget Planner page as per PDF page 11."""
    return templates.TemplateResponse(
        request=request,
        name="home_planner.html",
        context={"user": current_user, "title": "Home Interior Budget Planner - PocketSmart AI"}
    )


@router.post("/generate-home")
@router.post("/home-budget")
async def plan_home_budget(
    budget_input: HomeBudgetInput,
    request: Request,
    current_user: Optional[UserInDB] = Depends(get_optional_current_user)
):
    """Generate home budget recommendations and persist to session & history as per PDF page 21."""
    if budget_input.total_budget <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total budget must be greater than zero."
        )

    username = current_user.username if current_user else "guest"

    if username in active_sessions:
        active_sessions[username].user_data["last_home_budget"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "budget": budget_input.total_budget,
            "requirements": {
                "lights": budget_input.num_lights,
                "fans": budget_input.num_fans,
                "furniture": budget_input.num_furniture,
                "dining_tables": budget_input.num_dining_tables,
                "has_living_room": budget_input.has_living_room,
                "has_kitchen": budget_input.has_kitchen,
                "has_bedroom": budget_input.has_bedroom,
            }
        }

    try:
        result = get_home_recommendations(budget_input)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

    save_to_history(
        username=username,
        recommendation_type="home",
        input_data=budget_input.dict(),
        result=result
    )

    return result
