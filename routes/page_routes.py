"""
General Page and System Routes for PocketSmart AI.
Matches PDF pages 25, 27, 28, 31.
"""
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from models.user import UserInDB
from services.auth_service import get_token, get_current_user, get_current_active_user, get_optional_current_user, active_sessions
from services.history_service import get_user_history

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Main landing page as per PDF page 27."""
    user = None
    try:
        token = await get_token(request)
        if token:
            user = await get_current_user(request, token)
    except Exception:
        pass

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"user": user, "title": "PocketSmart AI - Smart Budget & Recommendation Assistant"}
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request):
    """User Dashboard as per PDF page 31."""
    current_user = await get_optional_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    history_items = get_user_history(current_user.username)
    recent_recs = history_items[:6]

    total_budget_planned = 0.0
    total_remaining_budget = 0.0
    home_count = 0
    party_count = 0
    jewelry_count = 0

    for item in history_items:
        inp = item.input_data or {}
        res = item.result or {}
        b = float(inp.get("total_budget", 0) or res.get("total_budget", 0) or 0)
        rem = float(res.get("remaining_budget", 0) or 0)
        total_budget_planned += b
        total_remaining_budget += rem

        t = item.recommendation_type
        if t == "home":
            home_count += 1
        elif t == "party":
            party_count += 1
        elif t == "jewelry":
            jewelry_count += 1

    session_info = active_sessions.get(current_user.username)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": current_user,
            "recent_recs": recent_recs,
            "total_plans": len(history_items),
            "total_budget_planned": round(total_budget_planned, 2),
            "total_remaining_budget": round(total_remaining_budget, 2),
            "home_count": home_count,
            "party_count": party_count,
            "jewelry_count": jewelry_count,
            "session_info": session_info,
            "title": "User Dashboard - PocketSmart AI",
        }
    )


@router.get("/testimonials", response_class=HTMLResponse)
async def testimonials_page(request: Request):
    """Testimonials page as per PDF page 28."""
    user = None
    try:
        token = await get_token(request)
        if token:
            user = await get_current_user(request, token)
    except Exception:
        pass

    return templates.TemplateResponse(
        request=request,
        name="testimonials.html",
        context={"user": user, "title": "Testimonials - PocketSmart AI"}
    )


@router.get("/startup")
async def startup_status():
    """Startup verification endpoint as specified in PDF page 25."""
    return {
        "status": "online",
        "app": "PocketSmart AI",
        "version": "1.0.0",
        "model": "Gemini 1.5 Flash Pro",
        "framework": "FastAPI",
        "platforms": ["Amazon", "Flipkart", "IKEA", "Swiggy", "Zomato", "OYO"]
    }
