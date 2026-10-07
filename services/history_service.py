"""
Recommendation History Service for PocketSmart AI.
Matches PDF pages 23-25.
"""
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from models.history import RecommendationHistoryItem

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "history_db.json")
user_recommendations: Dict[str, List[RecommendationHistoryItem]] = {}


def load_history():
    """Loads past recommendations from history_db.json."""
    global user_recommendations
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for uname, items in data.items():
                    user_recommendations[uname] = [
                        RecommendationHistoryItem(**item) for item in items
                    ]
        except Exception:
            pass


def save_history_to_disk():
    """Persists recommendation history to disk."""
    try:
        data = {
            uname: [item.dict() for item in items]
            for uname, items in user_recommendations.items()
        }
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


load_history()


def generate_input_summary(rec_type: str, input_data: Dict[str, Any]) -> str:
    """Creates a user-friendly summary of the input parameters."""
    if rec_type == "home":
        rooms = []
        if input_data.get("has_living_room"): rooms.append("Living Room")
        if input_data.get("has_kitchen"): rooms.append("Kitchen")
        if input_data.get("has_bedroom"): rooms.append("Bedroom")
        room_str = ", ".join(rooms) if rooms else "General"
        lights = input_data.get("num_lights", 0)
        fans = input_data.get("num_fans", 0)
        furniture = input_data.get("num_furniture", 0)
        return f"Rooms: {room_str} | Lights: {lights}, Fans: {fans}, Furniture: {furniture}"
    elif rec_type == "party":
        ptype = input_data.get("party_type", "Party")
        guests = input_data.get("num_guests", 0)
        venue = input_data.get("venue_type", "Any")
        return f"Type: {ptype} | Guests: {guests} | Venue: {venue}"
    elif rec_type == "jewelry":
        occ = input_data.get("occasion", "General")
        pref = input_data.get("preferences", "None")
        has_img = "Yes" if input_data.get("image") or input_data.get("has_image") else "No"
        return f"Occasion: {occ} | Style: {pref} | With outfit image: {has_img}"
    return "Budget Plan"


def generate_result_summary(rec_type: str, result: Dict[str, Any]) -> str:
    """Creates a summary of results."""
    rem = result.get("remaining_budget", 0.0)
    if rec_type == "home":
        bd = result.get("budget_breakdown", [])
        total_items = sum(len(c.get("items", [])) for c in bd)
        return f"{total_items} items recommended. Remaining: ₹{rem:,.2f}"
    elif rec_type == "party":
        bd = result.get("budget_breakdown", [])
        venues = result.get("venue_suggestions", [])
        return f"{len(bd)} categories allocated, {len(venues)} venue suggestions. Remaining: ₹{rem:,.2f}"
    elif rec_type == "jewelry":
        recs = result.get("jewelry_recommendations", [])
        return f"{len(recs)} jewelry pieces recommended. Remaining: ₹{rem:,.2f}"
    return f"Completed. Remaining budget: ₹{rem:,.2f}"


def save_to_history(username: str, recommendation_type: str, input_data: dict, result: dict) -> RecommendationHistoryItem:
    """Saves a recommendation query to user's history."""
    if username not in user_recommendations:
        user_recommendations[username] = []
        
    rec_item = RecommendationHistoryItem(
        id=str(uuid.uuid4()),
        username=username,
        timestamp=datetime.utcnow().strftime("%b %d, %Y, %I:%M %p"),
        recommendation_type=recommendation_type,
        input_data=input_data,
        result=result,
        input_summary=generate_input_summary(recommendation_type, input_data),
        result_summary=generate_result_summary(recommendation_type, result),
    )
    
    user_recommendations[username].append(rec_item)
    save_history_to_disk()
    return rec_item


def get_user_history(username: str) -> List[RecommendationHistoryItem]:
    """Returns sorted history for user (newest first)."""
    items = user_recommendations.get(username, [])
    return sorted(items, key=lambda x: x.timestamp, reverse=True)


def get_recommendation_details(username: str, recommendation_id: str) -> Optional[RecommendationHistoryItem]:
    """Finds a specific recommendation by ID for a user."""
    items = user_recommendations.get(username, [])
    for it in items:
        if it.id == recommendation_id:
            return it
    return None
