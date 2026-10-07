"""
Services package for PocketSmart AI.
"""
from .auth_service import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_token,
    get_password_hash,
    verify_password,
    users_db,
    active_sessions,
    blacklisted_tokens,
)
from .history_service import (
    save_to_history,
    get_user_history,
    get_recommendation_details,
)
from .platform_service import (
    build_home_shopping_links,
    build_party_shopping_links,
    build_venue_search_links,
    build_jewelry_shopping_links,
)

__all__ = [
    "authenticate_user",
    "create_access_token",
    "get_current_user",
    "get_current_active_user",
    "get_token",
    "get_password_hash",
    "verify_password",
    "users_db",
    "active_sessions",
    "blacklisted_tokens",
    "save_to_history",
    "get_user_history",
    "get_recommendation_details",
    "build_home_shopping_links",
    "build_party_shopping_links",
    "build_venue_search_links",
    "build_jewelry_shopping_links",
]
