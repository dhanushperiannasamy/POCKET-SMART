"""
Routes package for PocketSmart AI.
"""
from .auth_routes import router as auth_router
from .session_routes import router as session_router
from .home_routes import router as home_router
from .party_routes import router as party_router
from .jewelry_routes import router as jewelry_router
from .history_routes import router as history_router
from .page_routes import router as page_router

__all__ = [
    "auth_router",
    "session_router",
    "home_router",
    "party_router",
    "jewelry_router",
    "history_router",
    "page_router",
]
