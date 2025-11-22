import re
from typing import Optional, Tuple, Dict

# Extract coordinates like "(12, 5)" or "12,5"
def extract_coordinates(text: str) -> Optional[Tuple[int, int]]:
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
        "coords": (row, col) or None
    }
    """
    q = query.lower().strip()
    coords = extract_coordinates(q)

    # 1. Route Planning
    if any(x in q for x in ["route", "path", "navigate", "travel"]):
        if "safe" in q or "safest" in q:
            return {"intent": "safe_route", "mode": "safe_route", "coords": coords}

        if "fast" in q or "shortest" in q:
            return {"intent": "fast_route", "mode": "balanced", "coords": coords}

        return {"intent": "safe_route", "mode": "safe_route", "coords": coords}

    # 2. Mining
    if any(x in q for x in ["mine", "mining", "resource", "valuable", "rich"]):
        return {"intent": "mining", "mode": "mining", "coords": coords}

    # 3. Conservation
    if any(x in q for x in ["conserve", "protect", "sensitive", "eco", "environment"]):
        return {"intent": "conservation", "mode": "conservation", "coords": coords}

    # 4. Hazards
    if any(x in q for x in ["hazard", "danger", "risky", "volcano", "vent"]):
        return {"intent": "hazard_analysis", "mode": "safe_route", "coords": coords}

    # 5. Biodiversity
    if any(x in q for x in ["life", "species", "biodiversity", "fish", "ecosystem"]):
        return {"intent": "life_analysis", "mode": "balanced", "coords": coords}

    # 6. POI
    if any(x in q for x in ["poi", "point of interest", "landmark", "station", "base"]):
        return {"intent": "poi_lookup", "mode": "balanced", "coords": coords}

    # 7. Region Explanation
    if any(x in q for x in ["explain", "describe", "what is here", "what's here"]):
        return {"intent": "explain_region", "mode": "balanced", "coords": coords}

    # 8. Summary
    if any(x in q for x in ["summary", "summarize", "overview"]):
        return {"intent": "summary", "mode": "balanced", "coords": None}

    # 9. Coordinate-only question
    if coords is not None:
        return {"intent": "coordinate_info", "mode": "balanced", "coords": coords}

    # 10. Fallback
    return {"intent": "unknown", "mode": "balanced", "coords": coords}

# Test block
if __name__ == "__main__":
    tests = [
        "find safe route from (2,3)",
        "where is best mining zone?",
        "analyze hazards at 10,15",
        "explain region at (3,8)",
        "give biodiversity at (12,9)",
        "poi at 4,6",
        "protect sensitive area",
        "what's at (8,8)?"
    ]

    for t in tests:
        print(t, "->", classify_intent(t))
