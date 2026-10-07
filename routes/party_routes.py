"""
Party Budget Planner Routes for PocketSmart AI.
Matches PDF pages 13-16, 22.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models.party import PartyBudgetInput
from models.user import UserInDB
from services.auth_service import get_optional_current_user, active_sessions
from services.history_service import save_to_history
from gemini_utils import get_party_recommendations

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/party-budget", response_class=HTMLResponse)
@router.get("/party-planner", response_class=HTMLResponse)
async def party_planner(
    request: Request,
    current_user: Optional[UserInDB] = Depends(get_optional_current_user)
):
    """Serve the Party Budget Planner page as per PDF page 13."""
    return templates.TemplateResponse(
        request=request,
        name="party_planner.html",
        context={"user": current_user, "title": "Party Budget Planner - PocketSmart AI"}
    )


@router.post("/generate-party")
@router.post("/party-budget")
async def plan_party_budget(
    budget_input: PartyBudgetInput,
    request: Request,
    current_user: Optional[UserInDB] = Depends(get_optional_current_user)
):
    """Generate party budget recommendations as per PDF page 22."""
    if budget_input.total_budget <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total budget must be greater than zero."
        )
    if budget_input.num_guests <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of guests must be at least 1."
        )

    username = current_user.username if current_user else "guest"

    if username in active_sessions:
        active_sessions[username].user_data["last_party_budget"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "budget": budget_input.total_budget,
            "party_type": budget_input.party_type,
            "guests": budget_input.num_guests,
            "venue_type": budget_input.venue_type,
        }

    try:
        result = get_party_recommendations(budget_input)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

    save_to_history(
        username=username,
        recommendation_type="party",
        input_data=budget_input.dict(),
        result=result
    )

    return result
