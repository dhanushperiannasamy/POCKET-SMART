"""
Recommendation History Routes for PocketSmart AI.
Matches PDF pages 23-25.
"""
from typing import Optional

from fastapi import APIRouter, Request, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from models.user import UserInDB
from services.auth_service import get_current_active_user, get_optional_current_user
from services.history_service import (
    user_recommendations,
    get_user_history,
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """Serve the history page to view past recommendations as per PDF page 25."""
    user = await get_optional_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    history_items = get_user_history(user.username)
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "user": user,
            "history_items": history_items,
            "title": "Recommendation History - PocketSmart AI"
        }
    )


@router.get("/recommendation-history")
async def get_recommendation_history(
    request: Request,
    current_user: Optional[UserInDB] = Depends(get_optional_current_user)
):
    """Get user recommendation history log in JSON format as per PDF page 23-24."""
    username = current_user.username if current_user else "guest"
    if username not in user_recommendations:
        return []

    history = sorted(
        user_recommendations[username],
        key=lambda x: x.timestamp,
        reverse=True
    )

    history_data = []
    for item in history:
        history_data.append({
            "id": item.id,
            "timestamp": item.timestamp,
            "type": item.recommendation_type,
            "input": item.input_summary,
            "summary": item.result_summary,
            "input_data": item.input_data,
            "full_result": item.result,
        })

    return history_data


@router.get("/recommendation-details/{recommendation_id}")
async def get_details_by_path(
    recommendation_id: str,
    request: Request,
    current_user: Optional[UserInDB] = Depends(get_optional_current_user)
):
    """Get full details for a specific recommendation by ID path as per PDF page 24."""
    username = current_user.username if current_user else None
    pool = []
    if username and username in user_recommendations:
        pool.extend(user_recommendations[username])
    for u, items in user_recommendations.items():
        if u != username:
            pool.extend(items)

    for item in pool:
        if item.id == recommendation_id:
            return {
                "id": item.id,
                "timestamp": item.timestamp,
                "type": item.recommendation_type,
                "input": item.input_summary,
                "input_data": item.input_data,
                "full_result": item.result,
            }

    raise HTTPException(status_code=404, detail="Recommendation not found")


@router.get("/recommendations-details")
async def get_details_by_query(
    request: Request,
    recommendation_id: Optional[str] = Query(None),
    id: Optional[str] = Query(None),
    current_user: Optional[UserInDB] = Depends(get_optional_current_user)
):
    """Query param endpoint for recommendation details as specified in route requirements."""
    target_id = recommendation_id or id
    if not target_id:
        username = current_user.username if current_user else "guest"
        history = get_user_history(username)
        if history:
            target_id = history[0].id
        else:
            raise HTTPException(status_code=404, detail="No recommendations found")

    return await get_details_by_path(target_id, request, current_user)
