"""
Jewelry Budget Planner Routes for PocketSmart AI.
Matches PDF pages 16-17, 23.
Supports multimodal analysis with optional outfit image upload.
"""
import os
import shutil
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models.jewelry import JewelryBudgetInput
from models.user import UserInDB
from services.auth_service import get_optional_current_user, active_sessions
from services.history_service import save_to_history
from gemini_utils import get_jewelry_recommendations

router = APIRouter()
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload_file(upload_file: UploadFile) -> str:
    """Saves uploaded outfit image to static/uploads/."""
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    clean_name = os.path.basename(upload_file.filename or "outfit.jpg").replace(" ", "_")
    saved_filename = f"{ts}_{clean_name}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path


@router.get("/jewelry-budget", response_class=HTMLResponse)
@router.get("/jewelry-planner", response_class=HTMLResponse)
async def jewelry_planner(
    request: Request,
    current_user: Optional[UserInDB] = Depends(get_optional_current_user)
):
    """Serve the Jewelry Budget Planner page as per PDF page 16."""
    return templates.TemplateResponse(
        request=request,
        name="jewelry_planner.html",
        context={"user": current_user, "title": "Jewelry Budget Planner - PocketSmart AI"}
    )


@router.post("/generate-jewelry")
@router.post("/jewelry-budget")
async def plan_jewelry_budget(
    request: Request,
    total_budget: float = Form(...),
    occasion: str = Form(...),
    preferences: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: Optional[UserInDB] = Depends(get_optional_current_user)
):
    """Generate personalized jewelry recommendations with optional outfit image upload as per PDF page 23."""
    if total_budget <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total budget must be greater than zero."
        )

    budget_input = JewelryBudgetInput(
        total_budget=total_budget,
        occasion=occasion,
        preferences=preferences or "Not specified",
    )

    image_path = None
    image_filename = None
    if image and image.filename:
        try:
            image_path = save_upload_file(image)
            image_filename = os.path.basename(image_path)
            budget_input.image_path = image_path
        except Exception:
            pass

    username = current_user.username if current_user else "guest"

    if username in active_sessions:
        active_sessions[username].user_data["last_jewelry_budget"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "budget": budget_input.total_budget,
            "occasion": budget_input.occasion,
            "has_image": image_filename is not None,
            "image_url": f"/static/uploads/{image_filename}" if image_filename else None,
        }

    try:
        result = get_jewelry_recommendations(budget_input, image_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

    if image_filename:
        result["outfit_image_url"] = f"/static/uploads/{image_filename}"

    input_data = budget_input.dict()
    if image_filename:
        input_data["image"] = image_filename
        input_data["image_url"] = f"/static/uploads/{image_filename}"

    save_to_history(
        username=username,
        recommendation_type="jewelry",
        input_data=input_data,
        result=result
    )

    return result
