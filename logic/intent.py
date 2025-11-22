"""
Intent class for AbyssGPT

This module takes a user query (string) and decidesthe following:

- What the user wants exactly (intent)
- What mode scoring/pathfinding should use
- Any coordinates mentioned
"""

import re
from typing import Optional, Tuple, Dict

def extract_coordinated(text: str) -> Optional[Tuple[int, int]]:
    pattern = r"\(?\s*(\d{1,2})\s*,\s*(\d{1,2})\s*\)?"
    match = re.search(pattern, text)
    if match:
        r = int(match.group(1))
        c = int(match.group(2))
        return r, c
    return None

# Intent classification
def classify_intent(query: str) -> Dict:
    """
    Returns:
    {
        "intent": str,
        "mode": str,
        "coords": (row, col) or none
    }
    """
    
    # 1. Route Planning (safe route / fast route)
    if any(x in q for x in ["route", "path", "navigate", "travel"]):
        if "safe" in q or "safest" in q:
            return {"intent": "safe_route", "mode": "safe_route", "coords": coords}

        if "fast" in q or "shortest" in q:
            # still uses pathfinding, but with a different cost function
            return {"intent": "fast_route", "mode": "balanced", "coords": coords}

        # fallback for genaric route
        return {"intent": "safe_route", "mode": "safe_route", "coords": coords}

    # 2. Mining / resource extraction
    if any(x in q for x in ["mine", "mining", "resource", "valuable", "rich"]):
        return {"intent": "mining", "mode": "mining", "coords": coords}

    # 3. Conservation / protected zones
    if any(x in q for x in ["conserve", "protect", "sensitive", "eco", "environment"]):
        return {"intent": "conservation", "mode": "conservation", "coords": coords}

    # 4. Hazard analysis
    if any(x in q for x in ["hazard", "danger", "risky", "volcano", "vent"]):
        return {"intent": "hazard_analysis", "mode": "safe_route", "coords": coords}

    # 5. Biodiversity / life analysis
    if any(x in q for x in ["life", "species", "biodiversity", "fish", "ecosystem"]):
        return {"intent": "life_analysis", "mode": "balanced", "coords": coords}

    # 6. POI lookup
    if any(x in q for x in ["poi", "point of interest", "landmark", "station", "base"]):
        return {"intent": "poi_lookup", "mode": "balanced", "coords": coords}

    # 7. Explanation of a region
    if any(x in q for x in ["explain", "describe", "what is here", "what's here"]):
        return {"intent": "explain_region", "mode": "balanced", "coords": coords}

    # 8. Data summaries (global level)
    if any(x in q for x in ["summary", "summarize", "overview"]):
        return {"intent": "summary", "mode": "balanced", "coords": None}

    # 9. Coordinate-only questions
    if coords is not None:
        # If user types: "what's at (10,12)"
        return {"intent": "coordinate_info", "mode": "balanced", "coords": coords}

    # 10. Fallback
    return {"intent": "unknown", "mode": "balanced", "coords": coords}
