"""
PocketSmart AI: Your Smart Budget & Recommendation Assistant
Main FastAPI Application (app.py)
Matches PDF pages 10-11, 25.
"""
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from gemini_utils import configure_gemini
configure_gemini()

app = FastAPI(
    title="PocketSmart: AI Budget Planner",
    description="GenAI-powered cross-platform recommendation system for home interior, party, and jewelry budgeting.",
    version="1.0.0"
)

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_pocketsmart_ai_2025")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/uploads", exist_ok=True)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

from routes.auth_routes import router as auth_router
from routes.session_routes import router as session_router
from routes.home_routes import router as home_router
from routes.party_routes import router as party_router
from routes.jewelry_routes import router as jewelry_router
from routes.history_routes import router as history_router
from routes.page_routes import router as page_router
from services.auth_service import active_sessions

app.include_router(page_router)
app.include_router(auth_router)
app.include_router(session_router)
app.include_router(home_router)
app.include_router(party_router)
app.include_router(jewelry_router)
app.include_router(history_router)


@app.on_event("startup")
async def setup_session_cleanup():
    """Background task to clean up expired sessions as per PDF page 25."""
    async def cleanup_expired_sessions():
        while True:
            try:
                current_time = datetime.utcnow()
                expired_sessions = [
                    username for username, session in active_sessions.items()
                    if (current_time - session.last_activity).total_seconds() > (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
                ]
                for username in expired_sessions:
                    if username in active_sessions:
                        print(f"Removing expired session for {username}")
                        del active_sessions[username]
            except Exception as e:
                print(f"Session cleanup error: {e}")
            await asyncio.sleep(300)

    asyncio.create_task(cleanup_expired_sessions())


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting PocketSmart: AI Budget Planner on http://{host}:{port} ...")
    uvicorn.run(app, host=host, port=port)
