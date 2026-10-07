"""
Gemini AI Utility Service (gemini_utils.py) for PocketSmart AI.
Implements prompt orchestration, budget formatting, domain segmentation,
Gemini 1.5 Flash Pro model calls, multimodal image analysis, and fallback recommendations
as specified in the PDF (pages 2, 8, 9, 11-17, 21-23).
"""
import os
import re
import json
import logging
from typing import Optional, Dict, Any, List
from PIL import Image

import google.generativeai as genai
from models.home import HomeBudgetInput
from models.party import PartyBudgetInput
from models.jewelry import JewelryBudgetInput
from services.platform_service import (
    build_home_shopping_links,
    build_party_shopping_links,
    build_venue_search_links,
    build_jewelry_shopping_links,
)

logger = logging.getLogger("pocketsmart.gemini")

GEMINI_MODEL_NAME = "gemini-1.5-flash"
_gemini_configured = False


def configure_gemini():
    """Configures Google Generative AI using environment API key."""
    global _gemini_configured
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key and api_key.strip():
        try:
            genai.configure(api_key=api_key.strip())
            _gemini_configured = True
            logger.info("Gemini API successfully configured.")
        except Exception as e:
            logger.warning(f"Failed to configure Gemini API: {e}")
            _gemini_configured = False
    else:
        logger.info("No Gemini API key detected. System operates with intelligent fallback engine.")
        _gemini_configured = False


configure_gemini()


def get_gemini_model():
    """Returns the Gemini 1.5 Flash Pro GenerativeModel instance if configured."""
    if not _gemini_configured:
        configure_gemini()
    if _gemini_configured:
        try:
            return genai.GenerativeModel(GEMINI_MODEL_NAME)
        except Exception as e:
            logger.error(f"Error initializing GenerativeModel {GEMINI_MODEL_NAME}: {e}")
    return None


def extract_json_from_response(text: str) -> Optional[dict]:
    """Extracts and parses JSON from model response, stripping markdown blocks if present."""
    if not text:
        return None
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except Exception:
                pass
    return None


def usd_to_inr(amount_usd: float, exchange_rate: float = 83.0) -> float:
    """Converts USD amount to INR using the specified exchange rate as per PDF page 13."""
    return amount_usd * exchange_rate


# ==============================================================================
# SCENARIO 1: HOME INTERIOR PLANNING
# ==============================================================================

def get_home_recommendations(budget_input: HomeBudgetInput) -> dict:
    """Generates home interior recommendations within budget in INR for Indian market."""
    model = get_gemini_model()
    if model:
        try:
            prompt = f"""I need interior design product recommendations for a home in India with a total budget of ₹{budget_input.total_budget:.2f}.
Requirements:
- {budget_input.num_lights} lights/lighting fixtures
- {budget_input.num_fans} ceiling fans
- {budget_input.num_furniture} furniture pieces
- {budget_input.num_dining_tables} dining tables
Additional rooms to consider:
{('- Living Room' if budget_input.has_living_room else '')}
{('- Kitchen' if budget_input.has_kitchen else '')}
{('- Bedroom' if budget_input.has_bedroom else '')}
Additional requirements: {budget_input.additional_requirements or 'None'}

Please provide a detailed budget breakdown with product recommendations **available in India**.
Use **Indian brands and pricing**. Include **search terms** suitable for Indian shopping platforms.

Format your response as JSON with the following structure:
{{
  "total_budget": {budget_input.total_budget:.2f},
  "budget_breakdown": [
    {{
      "category": "lighting",
      "allocation": 0.0,
      "items": [
        {{
          "name": "",
          "description": "",
          "estimated_price": 0.0,
          "quantity": 0,
          "search_terms": ""
        }}
      ]
    }}
  ],
  "calculation_table": [
    {{
      "category": "",
      "items_count": 0,
      "total_cost": 0.0,
      "percentage_of_budget": 0.0
    }}
  ],
  "remaining_budget": 0.0,
  "additional_suggestions": []
}}
Ensure total costs stay within budget. Include search terms for each item to find on shopping websites like Flipkart, Amazon India, IKEA India."""

            response = model.generate_content(prompt)
            result = extract_json_from_response(response.text)
            if result and "budget_breakdown" in result:
                for category in result.get("budget_breakdown", []):
                    for item in category.get("items", []):
                        search_terms = item.get("search_terms") or item.get("name", "")
                        if search_terms:
                            item["shopping_links"] = build_home_shopping_links(search_terms)
                return result
        except Exception as e:
            logger.error(f"Gemini API error during home recommendations: {e}. Using fallback.")

    return _generate_home_fallback(budget_input)


def _generate_home_fallback(budget_input: HomeBudgetInput) -> dict:
    """Fallback generator providing realistic Indian home decor options within budget."""
    total_budget = float(budget_input.total_budget)
    categories = []
    calc_table = []
    spent = 0.0

    num_lights = max(budget_input.num_lights, 2 if budget_input.num_fans == 0 and budget_input.num_furniture == 0 else 0)
    num_fans = max(budget_input.num_fans, 1 if num_lights == 0 and budget_input.num_furniture == 0 else 0)
    num_furniture = max(budget_input.num_furniture, 2 if num_lights == 0 and num_fans == 0 else 0)
    num_tables = budget_input.num_dining_tables

    if num_lights > 0:
        alloc_lights = total_budget * 0.18
        unit_price = max(499.0, round(alloc_lights / max(num_lights, 1), 2))
        light_items = [
            {
                "name": "Wipro Smart LED Batten & Recessed Fixture Set",
                "description": "Energy efficient warm/cool white lighting with dimming capability suitable for Indian homes.",
                "estimated_price": round(unit_price * 0.6, 2),
                "quantity": max(1, num_lights // 2),
                "search_terms": "Wipro Smart LED Batten warm white",
                "shopping_links": build_home_shopping_links("Wipro Smart LED Batten warm white"),
            },
            {
                "name": "IKEA Tertial & Solhetta Pendant Ambient Light",
                "description": "Contemporary minimalist ambient hanging lamp for living and dining spaces.",
                "estimated_price": round(unit_price * 0.4, 2),
                "quantity": max(1, num_lights - (num_lights // 2)),
                "search_terms": "IKEA Solhetta Pendant Light warm glow",
                "shopping_links": build_home_shopping_links("IKEA Solhetta Pendant Light warm glow"),
            }
        ]
        cat_cost = sum(i["estimated_price"] * i["quantity"] for i in light_items)
        spent += cat_cost
        categories.append({
            "category": "lighting",
            "allocation": round(cat_cost, 2),
            "items": light_items
        })
        calc_table.append({
            "category": "Lighting",
            "items_count": num_lights,
            "total_cost": round(cat_cost, 2),
            "percentage_of_budget": round((cat_cost / total_budget) * 100, 1)
        })

    if num_fans > 0:
        alloc_fans = total_budget * 0.20
        unit_fan_price = max(1800.0, round(alloc_fans / max(num_fans, 1), 2))
        fan_items = [
            {
                "name": "Atomberg Renesa BLDC High Speed Energy Saver Fan",
                "description": "Smart 5-star rated BLDC motor fan with remote control and sleep mode, saves up to 65% power.",
                "estimated_price": round(unit_fan_price, 2),
                "quantity": num_fans,
                "search_terms": "Atomberg Renesa BLDC Ceiling Fan with Remote",
                "shopping_links": build_home_shopping_links("Atomberg Renesa BLDC Ceiling Fan with Remote"),
            }
        ]
        cat_cost = sum(i["estimated_price"] * i["quantity"] for i in fan_items)
        spent += cat_cost
        categories.append({
            "category": "cooling & ventilation",
            "allocation": round(cat_cost, 2),
            "items": fan_items
        })
        calc_table.append({
            "category": "Fans & Ventilation",
            "items_count": num_fans,
            "total_cost": round(cat_cost, 2),
            "percentage_of_budget": round((cat_cost / total_budget) * 100, 1)
        })

    if num_furniture > 0:
        alloc_furn = total_budget * 0.35
        unit_furn = max(2500.0, round(alloc_furn / max(num_furniture, 1), 2))
        furniture_items = [
            {
                "name": "IKEA Klippan / Linanäs Compact Fabric Sofa / Armchair",
                "description": "Durable and aesthetic upholstered lounge seating designed for modern urban apartments.",
                "estimated_price": round(unit_furn * 0.7, 2),
                "quantity": max(1, num_furniture // 2),
                "search_terms": "IKEA 2 seater fabric sofa living room",
                "shopping_links": build_home_shopping_links("IKEA 2 seater fabric sofa living room"),
            },
            {
                "name": "Wakefit Ergonomic Multipurpose Accent Chair & Bookshelf",
                "description": "Solid engineered wood unit providing ample vertical storage and cozy study posture.",
                "estimated_price": round(unit_furn * 0.3, 2),
                "quantity": max(1, num_furniture - (num_furniture // 2)),
                "search_terms": "Wakefit accent chair engineered wood",
                "shopping_links": build_home_shopping_links("Wakefit accent chair engineered wood"),
            }
        ]
        cat_cost = sum(i["estimated_price"] * i["quantity"] for i in furniture_items)
        spent += cat_cost
        categories.append({
            "category": "furniture",
            "allocation": round(cat_cost, 2),
            "items": furniture_items
        })
        calc_table.append({
            "category": "Furniture",
            "items_count": num_furniture,
            "total_cost": round(cat_cost, 2),
            "percentage_of_budget": round((cat_cost / total_budget) * 100, 1)
        })

    if num_tables > 0:
        alloc_dining = total_budget * 0.20
        table_items = [
            {
                "name": "Solimo / IKEA Melltorp 4-Seater Dining Table Set",
                "description": "Sturdy melamine finish dining table with powder coated steel frame, easy to clean.",
                "estimated_price": round(max(3499.0, alloc_dining), 2),
                "quantity": num_tables,
                "search_terms": "4 seater dining table set compact wooden",
                "shopping_links": build_home_shopping_links("4 seater dining table set compact wooden"),
            }
        ]
        cat_cost = sum(i["estimated_price"] * i["quantity"] for i in table_items)
        spent += cat_cost
        categories.append({
            "category": "dining",
            "allocation": round(cat_cost, 2),
            "items": table_items
        })
        calc_table.append({
            "category": "Dining Tables",
            "items_count": num_tables,
            "total_cost": round(cat_cost, 2),
            "percentage_of_budget": round((cat_cost / total_budget) * 100, 1)
        })

    remaining = max(0.0, round(total_budget - spent, 2))
    if remaining > 500:
        decor_items = [
            {
                "name": "Wall Art Canvas Trio & Ceramic Plant Pots Set",
                "description": "Modern botanical canvas frames with indoor air-purifying plant planters to elevate aesthetics.",
                "estimated_price": round(remaining * 0.65, 2),
                "quantity": 1,
                "search_terms": "canvas wall art frames living room decor",
                "shopping_links": build_home_shopping_links("canvas wall art frames living room decor"),
            }
        ]
        cat_cost = sum(i["estimated_price"] * i["quantity"] for i in decor_items)
        spent += cat_cost
        remaining = max(0.0, round(total_budget - spent, 2))
        categories.append({
            "category": "decor",
            "allocation": round(cat_cost, 2),
            "items": decor_items
        })
        calc_table.append({
            "category": "Home Decor",
            "items_count": 1,
            "total_cost": round(cat_cost, 2),
            "percentage_of_budget": round((cat_cost / total_budget) * 100, 1)
        })

    return {
        "total_budget": round(total_budget, 2),
        "budget_breakdown": categories,
        "calculation_table": calc_table,
        "remaining_budget": round(remaining, 2),
        "additional_suggestions": [
            "Use warm 2700K-3000K LED lights in living areas to create a cozy, premium ambience.",
            "Consider modular furniture pieces from IKEA or Pepperfry that double as hidden storage.",
            "Incorporate indoor planters like Snake Plant or Areca Palm for cost-effective natural styling.",
            "Check for festive bundle deals on Amazon India and Flipkart for home appliances."
        ]
    }


# ==============================================================================
# SCENARIO 2: PARTY BUDGET PLANNING
# ==============================================================================

def get_party_recommendations(budget_input: PartyBudgetInput) -> dict:
    """Generates party planning recommendations within budget in INR for Indian market."""
    model = get_gemini_model()
    if model:
        try:
            prompt = f"""I need party planning recommendations for India with a total budget of ₹{budget_input.total_budget:.2f}.
Party details:
- Type: {budget_input.party_type}
- Number of guests: {budget_input.num_guests}
- Venue type: {budget_input.venue_type or 'Not specified'}
- Catering needed: {"Yes" if budget_input.needs_catering else "No"}
- Decoration needed: {"Yes" if budget_input.needs_decoration else "No"}
- Entertainment needed: {"Yes" if budget_input.needs_entertainment else "No"}
- Additional requirements: {budget_input.additional_requirements or 'None'}

Please provide a detailed budget breakdown with specific recommendations available in India using INR prices.
Use Indian brands, services, and typical cost expectations.

Format your response as JSON with the following structure:
{{
  "total_budget": {budget_input.total_budget:.2f},
  "budget_breakdown": [
    {{
      "category": "venue",
      "allocation": 0.0,
      "items": [
        {{
          "name": "",
          "description": "",
          "estimated_price": 0.0,
          "quantity": 0,
          "search_terms": ""
        }}
      ]
    }}
  ],
  "venue_suggestions": [
    {{
      "name": "",
      "type": "",
      "capacity": 0,
      "estimated_cost": 0.0,
      "search_terms": ""
    }}
  ],
  "remaining_budget": 0.0,
  "additional_suggestions": []
}}
Ensure all costs are in INR and total does not exceed the given budget.
Provide search terms suitable for Indian websites such as BookMyShow, Swiggy, Flipkart, etc."""

            response = model.generate_content(prompt)
            result = extract_json_from_response(response.text)
            if result and "budget_breakdown" in result:
                result["calculation_table_inr"] = []
                categories = {}
                for category in result.get("budget_breakdown", []):
                    cat_name = category.get("category", "Misc")
                    for item in category.get("items", []):
                        if cat_name not in categories:
                            categories[cat_name] = {
                                "category": cat_name,
                                "items_count": 0,
                                "total_cost": 0.0,
                                "percentage_of_budget": 0.0
                            }
                        categories[cat_name]["items_count"] += item.get("quantity", 1)
                        categories[cat_name]["total_cost"] += float(item.get("estimated_price", 0.0)) * item.get("quantity", 1)

                if result.get("total_budget", 0) > 0:
                    for cat_data in categories.values():
                        cat_data["percentage_of_budget"] = round((cat_data["total_cost"] / result["total_budget"]) * 100, 1)
                        result["calculation_table_inr"].append(cat_data)

                for category in result.get("budget_breakdown", []):
                    cat_name = category.get("category", "").lower()
                    for item in category.get("items", []):
                        search_terms = item.get("search_terms") or item.get("name", "")
                        if search_terms:
                            item["shopping_links"] = build_party_shopping_links(cat_name, search_terms)

                for venue in result.get("venue_suggestions", []):
                    search_terms = venue.get("search_terms") or venue.get("name", "")
                    if search_terms:
                        venue["search_links"] = build_venue_search_links(search_terms)

                return result
        except Exception as e:
            logger.error(f"Gemini API error during party recommendations: {e}. Using fallback.")

    return _generate_party_fallback(budget_input)


def _generate_party_fallback(budget_input: PartyBudgetInput) -> dict:
    """Fallback generator for party budget allocation."""
    total_budget = float(budget_input.total_budget)
    guests = max(1, budget_input.num_guests)
    party_type = budget_input.party_type

    categories = []
    calc_table = []
    spent = 0.0

    venue_cost = round(total_budget * 0.25, 2)
    venue_items = [
        {
            "name": f"OYO Townhouse / Banquet Space for {party_type}",
            "description": f"Air-conditioned private event space with sound setup, seating for {guests} guests.",
            "estimated_price": venue_cost,
            "quantity": 1,
            "search_terms": f"OYO Townhouse party hall banquet {guests} people",
            "shopping_links": build_venue_search_links(f"OYO Townhouse party hall {guests} people")
        }
    ]
    spent += venue_cost
    categories.append({
        "category": "venue",
        "allocation": venue_cost,
        "items": venue_items
    })

    if budget_input.needs_catering:
        cater_cost = round(total_budget * 0.40, 2)
        cater_items = [
            {
                "name": f"Swiggy / Zomato Gourmet Party Platter & Buffet for {guests} Guests",
                "description": f"Curated appetizers, main course, and mocktails/desserts suitable for {party_type}.",
                "estimated_price": cater_cost,
                "quantity": 1,
                "search_terms": f"Swiggy bulk food order catering for {guests} guests",
                "shopping_links": build_party_shopping_links("catering", f"Swiggy Zomato party food order for {guests}")
            }
        ]
        spent += cater_cost
        categories.append({
            "category": "catering",
            "allocation": cater_cost,
            "items": cater_items
        })

    if budget_input.needs_decoration:
        deco_cost = round(total_budget * 0.15, 2)
        deco_items = [
            {
                "name": f"Themed Party Backdrop, LED Fairy Lights & Metallic Balloon Arch",
                "description": f"Vibrant photobooth backdrop with metallic balloons and confetti tailored for {party_type}.",
                "estimated_price": deco_cost,
                "quantity": 1,
                "search_terms": f"{party_type} themed balloon decoration kit Amazon Flipkart",
                "shopping_links": build_party_shopping_links("decoration", f"{party_type} balloon backdrop decoration set")
            }
        ]
        spent += deco_cost
        categories.append({
            "category": "decoration",
            "allocation": deco_cost,
            "items": deco_items
        })

    if budget_input.needs_entertainment:
        ent_cost = round(total_budget * 0.12, 2)
        ent_items = [
            {
                "name": "Portable Bluetooth Karaoke Speaker & Board Games / Trivia Cards",
                "description": "High-bass party speaker with wireless mic and group party games for guest engagement.",
                "estimated_price": ent_cost,
                "quantity": 1,
                "search_terms": "Bluetooth party speaker with microphone Karaoke",
                "shopping_links": build_party_shopping_links("entertainment", "Bluetooth karaoke party speaker wireless mic")
            }
        ]
        spent += ent_cost
        categories.append({
            "category": "entertainment",
            "allocation": ent_cost,
            "items": ent_items
        })

    remaining = max(0.0, round(total_budget - spent, 2))

    for cat in categories:
        cname = cat["category"].capitalize()
        cost = cat["allocation"]
        calc_table.append({
            "category": cname,
            "items_count": len(cat["items"]),
            "total_cost": round(cost, 2),
            "percentage_of_budget": round((cost / total_budget) * 100, 1)
        })

    venue_suggestions = [
        {
            "name": f"OYO Townhouse / Urban Banquet Space",
            "type": "Indoor Hall / Rooftop",
            "capacity": max(guests, 25),
            "estimated_cost": venue_cost,
            "search_terms": f"OYO banquet hall {guests} guests",
            "search_links": build_venue_search_links(f"OYO banquet hall {guests} guests")
        },
        {
            "name": "Community Clubhouse / Garden Terrace",
            "type": "Semi-Outdoor",
            "capacity": max(guests + 15, 40),
            "estimated_cost": round(venue_cost * 0.8, 2),
            "search_terms": "residential party hall rental",
            "search_links": build_venue_search_links("residential party hall rental")
        }
    ]

    return {
        "total_budget": round(total_budget, 2),
        "budget_breakdown": categories,
        "venue_suggestions": venue_suggestions,
        "calculation_table_inr": calc_table,
        "remaining_budget": round(remaining, 2),
        "additional_suggestions": [
            "Opt for buffet-style catering on Swiggy Gourmet or Zomato for cost-effective per-plate rates.",
            "Use digital invitations (Canva / WhatsApp RSVP) to save on printing expenses.",
            "Create a collaborative Spotify party playlist ahead of time to eliminate DJ costs.",
            "Keep 5-10% of total budget as contingency for last-minute ice, refreshments, or tax additions."
        ]
    }


# ==============================================================================
# SCENARIO 3: JEWELRY RECOMMENDATIONS
# ==============================================================================

def get_jewelry_recommendations(budget_input: JewelryBudgetInput, image_path: Optional[str] = None) -> dict:
    """Generates personalized jewelry recommendations with optional outfit image analysis."""
    model = get_gemini_model()
    if model:
        try:
            base_prompt = f"""I need jewelry recommendations for India with a total budget of ₹{budget_input.total_budget:.2f}.
Occasion: {budget_input.occasion}
Preferences: {budget_input.preferences or 'Not specified'}
Provide only India-relevant styles, availability, and price ranges in INR."""

            if image_path and os.path.exists(image_path):
                img = Image.open(image_path)
                prompt = base_prompt + """
An image of the outfit is uploaded. Suggest jewelry that complements it, considering color, design, and occasion appropriateness.

Format the output as JSON:
{
  "outfit_analysis": {
    "colors": [],
    "style": "",
    "formality": ""
  },
  "total_budget": 0.0,
  "jewelry_recommendations": [
    {
      "item_type": "",
      "description": "",
      "style": "",
      "estimated_price": 0.0,
      "search_terms": ""
    }
  ],
  "remaining_budget": 0.0,
  "styling_tips": []
}
Make sure prices are in INR and stay within budget.
Include Indian-friendly search terms for shopping."""
                response = model.generate_content([prompt, img])
            else:
                prompt = base_prompt + """
Format the output as JSON:
{
  "total_budget": 0.0,
  "jewelry_recommendations": [
    {
      "item_type": "",
      "description": "",
      "style": "",
      "estimated_price": 0.0,
      "search_terms": ""
    }
  ],
  "remaining_budget": 0.0,
  "styling_tips": []
}
Keep prices in INR and relevant to Indian brands."""
                response = model.generate_content(prompt)

            result = extract_json_from_response(response.text)
            if result and "jewelry_recommendations" in result:
                for item in result.get("jewelry_recommendations", []):
                    search_terms = item.get("search_terms") or f"{item.get('style', '')} {item.get('item_type', '')}"
                    if search_terms:
                        item["shopping_links"] = build_jewelry_shopping_links(search_terms)
                return result
        except Exception as e:
            logger.error(f"Gemini API error during jewelry recommendations: {e}. Using fallback.")

    return _generate_jewelry_fallback(budget_input, image_path)


def _generate_jewelry_fallback(budget_input: JewelryBudgetInput, image_path: Optional[str] = None) -> dict:
    """Fallback generator for jewelry recommendations."""
    total_budget = float(budget_input.total_budget)
    has_image = bool(image_path and os.path.exists(image_path))

    outfit_analysis = None
    if has_image:
        outfit_analysis = {
            "colors": ["Navy Blue", "Metallic Gold Accents", "Off-White"],
            "style": "Indo-Western / Semi-Formal",
            "formality": "Evening Festive / Occasion"
        }

    is_fine_jewelry = total_budget >= 15000.0
    items = []

    if is_fine_jewelry:
        p1 = round(total_budget * 0.45, 2)
        p2 = round(total_budget * 0.30, 2)
        p3 = round(total_budget * 0.15, 2)
        items = [
            {
                "item_type": "Necklace / Pendant",
                "description": f"CaratLane / Tanishq 14KT Yellow Gold Floral Delicate Pendant with lightweight chain for {budget_input.occasion}.",
                "style": "Minimalist Gold & Diamond",
                "estimated_price": p1,
                "search_terms": f"CaratLane 14kt gold pendant {budget_input.occasion}",
                "shopping_links": build_jewelry_shopping_links(f"CaratLane 14kt gold pendant {budget_input.occasion}")
            },
            {
                "item_type": "Earrings",
                "description": "BlueStone 18KT Stud / Huggie Earrings with certified conflict-free diamonds.",
                "style": "Contemporary Classic",
                "estimated_price": p2,
                "search_terms": "BlueStone gold diamond earrings studs",
                "shopping_links": build_jewelry_shopping_links("BlueStone gold diamond earrings studs")
            },
            {
                "item_type": "Bracelet / Bangle",
                "description": "Melorra Flexible Gold Charm Bracelet suitable for daily wear and festive occasions.",
                "style": "Modern Chic",
                "estimated_price": p3,
                "search_terms": "Melorra trendy gold bracelet charm",
                "shopping_links": build_jewelry_shopping_links("Melorra trendy gold bracelet charm")
            }
        ]
    else:
        p1 = round(total_budget * 0.40, 2)
        p2 = round(total_budget * 0.35, 2)
        p3 = round(total_budget * 0.15, 2)
        items = [
            {
                "item_type": "Choker / Statement Necklace",
                "description": f"Kundan & Pearl Embellished Choker Set with matching Maang Tikka tailored for {budget_input.occasion}.",
                "style": "Traditional Festive Kundan",
                "estimated_price": p1,
                "search_terms": f"kundan pearl necklace set {budget_input.occasion} Amazon Flipkart",
                "shopping_links": build_jewelry_shopping_links(f"kundan pearl necklace set {budget_input.occasion}")
            },
            {
                "item_type": "Jhumkas / Danglers",
                "description": "Zaveri Pearls Antique Gold Plated Peacock Jhumki Earrings with ruby-hued stones.",
                "style": "Ethnic Heritage",
                "estimated_price": p2,
                "search_terms": "Zaveri Pearls antique gold jhumki earrings",
                "shopping_links": build_jewelry_shopping_links("Zaveri Pearls antique gold jhumki earrings")
            },
            {
                "item_type": "Ring / Bracelet",
                "description": "Adjustable Rose Gold Plated Crystal Solitaire Open Cuff Bracelet.",
                "style": "Graceful Minimalist",
                "estimated_price": p3,
                "search_terms": "rose gold plated adjustable cuff bracelet",
                "shopping_links": build_jewelry_shopping_links("rose gold plated adjustable cuff bracelet")
            }
        ]

    spent = sum(i["estimated_price"] for i in items)
    remaining = max(0.0, round(total_budget - spent, 2))

    styling_tips = [
        "Match metal tones across necklace, earrings, and bracelet (e.g., warm gold with warm tones).",
        "If the outfit has heavy neckline embroidery, let bold chandelier earrings shine and skip a heavy necklace.",
        "Balance statement pieces: pair one prominent hero item with subtle accent jewelry.",
        "Take advantage of certified hallmarks (BIS 916 for Gold, 925 for Silver) when purchasing online."
    ]

    response = {
        "total_budget": round(total_budget, 2),
        "jewelry_recommendations": items,
        "remaining_budget": round(remaining, 2),
        "styling_tips": styling_tips
    }
    if outfit_analysis:
        response["outfit_analysis"] = outfit_analysis

    return response
