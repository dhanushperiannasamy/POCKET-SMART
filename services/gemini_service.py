"""
Gemini Service wrapper exposing recommendation generators.
"""
from gemini_utils import (
    get_home_recommendations,
    get_party_recommendations,
    get_jewelry_recommendations,
    usd_to_inr,
    configure_gemini,
)

__all__ = [
    "get_home_recommendations",
    "get_party_recommendations",
    "get_jewelry_recommendations",
    "usd_to_inr",
    "configure_gemini",
]
