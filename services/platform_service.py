"""
Platform search linking and integration service for PocketSmart AI.
Matches PDF pages 12, 14, 15, 17.
"""
import urllib.parse
from typing import Dict, List, Optional


CATEGORY_PLATFORMS = {
    "venue": ["google", "booking", "makemytrip", "oyorooms", "nobroker"],
    "catering": ["swiggy", "zomato"],
    "food": ["swiggy", "zomato", "bigbasket", "amazon", "flipkart"],
    "drinks": ["swiggy", "zomato", "bigbasket", "amazon", "flipkart"],
    "decoration": ["amazon", "flipkart", "meesho", "myntra"],
    "entertainment": ["bookmyshow", "amazon", "flipkart"],
    "gifts": ["amazon", "flipkart", "myntra", "meesho"],
    "photography": ["google", "amazon", "flipkart"],
    "music": ["amazon", "flipkart", "bookmyshow"],
    "games": ["amazon", "flipkart"],
    "accessories": ["amazon", "flipkart", "myntra", "meesho"],
    "transportation": ["makemytrip", "google"],
    "return_gifts": ["amazon", "flipkart", "myntra", "meesho"],
    "lighting": ["amazon", "flipkart", "ikea"],
    "furniture": ["ikea", "amazon", "flipkart"],
    "decor": ["amazon", "flipkart", "ikea", "myntra"],
}

DEFAULT_PLATFORMS = ["amazon", "flipkart", "google"]


def get_search_url_for_platform(platform: str, search_terms: str) -> Optional[str]:
    """Builds search URL for a given platform name and query string."""
    encoded = urllib.parse.quote_plus(search_terms.strip())
    p = platform.lower().strip()
    
    if p == "amazon":
        return f"https://www.amazon.in/s?k={encoded}"
    elif p == "flipkart":
        return f"https://www.flipkart.com/search?q={encoded}"
    elif p == "ikea":
        return f"https://www.ikea.com/in/en/search/?q={encoded}"
    elif p == "myntra":
        return f"https://www.myntra.com/search?q={encoded}"
    elif p == "ajio":
        return f"https://www.ajio.com/search/?text={encoded}"
    elif p == "swiggy":
        return f"https://www.swiggy.com/search?query={encoded}"
    elif p == "zomato":
        return f"https://www.zomato.com/search?q={encoded}"
    elif p == "bigbasket":
        return f"https://www.bigbasket.com/ps/?q={encoded}"
    elif p == "bookmyshow":
        return f"https://in.bookmyshow.com/search?q={encoded}"
    elif p == "meesho":
        return f"https://www.meesho.com/search?q={encoded}"
    elif p == "google":
        return f"https://www.google.com/search?q={encoded}"
    elif p == "booking":
        return f"https://www.booking.com/search.html?ss={encoded}"
    elif p == "makemytrip":
        return f"https://www.makemytrip.com/hotels/hotel-listing/?searchtext={encoded}"
    elif p == "oyorooms" or p == "oyo":
        return f"https://www.oyorooms.com/search/?location={encoded}"
    elif p == "nobroker":
        return f"https://www.nobroker.in/property/search?searchTerm={encoded}"
    elif p == "bluestone":
        return f"https://www.bluestone.com/search.html?query={encoded}"
    elif p == "tanishq":
        return f"https://www.tanishq.co.in/search?q={encoded}"
    elif p == "caratlane":
        return f"https://www.caratlane.com/search?q={encoded}"
    elif p == "melorra":
        return f"https://www.melorra.com/search?q={encoded}"
    return f"https://www.google.com/search?q={encoded}"


def build_home_shopping_links(search_terms: str) -> Dict[str, str]:
    """Generates shopping links for home interior items as per PDF page 12."""
    encoded = urllib.parse.quote_plus(search_terms.strip())
    return {
        "amazon": f"https://www.amazon.in/s?k={encoded}",
        "flipkart": f"https://www.flipkart.com/search?q={encoded}",
        "ikea": f"https://www.ikea.com/in/en/search/?q={encoded}",
        "myntra": f"https://www.myntra.com/search?q={encoded}",
        "ajio": f"https://www.ajio.com/search/?text={encoded}",
    }


def build_party_shopping_links(category: str, search_terms: str) -> Dict[str, str]:
    """Generates shopping links for party items as per PDF page 15."""
    cat_lower = category.lower().strip()
    relevant_platforms = CATEGORY_PLATFORMS.get(cat_lower, DEFAULT_PLATFORMS)
    
    links = {}
    for platform in relevant_platforms:
        url = get_search_url_for_platform(platform, search_terms)
        if url:
            links[platform] = url
    return links


def build_venue_search_links(search_terms: str) -> Dict[str, str]:
    """Generates search links for venue recommendations as per PDF page 16."""
    venue_platforms = ["google", "booking", "makemytrip", "oyorooms", "nobroker"]
    links = {}
    for platform in venue_platforms:
        url = get_search_url_for_platform(platform, search_terms)
        if url:
            links[platform] = url
    return links


def build_jewelry_shopping_links(search_terms: str) -> Dict[str, str]:
    """Generates shopping links for jewelry items as per PDF page 17."""
    encoded = urllib.parse.quote_plus(search_terms.strip())
    return {
        "amazon": f"https://www.amazon.in/s?k={encoded}",
        "flipkart": f"https://www.flipkart.com/search?q={encoded}",
        "bluestone": f"https://www.bluestone.com/search.html?query={encoded}",
        "tanishq": f"https://www.tanishq.co.in/search?q={encoded}",
        "caratlane": f"https://www.caratlane.com/search?q={encoded}",
        "melorra": f"https://www.melorra.com/search?q={encoded}",
        "meesho": f"https://www.meesho.com/search?q={encoded}",
    }
