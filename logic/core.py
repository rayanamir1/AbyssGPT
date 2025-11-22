# logic/core.py

import re
from logic.intent import classify_intent
from logic.data_loader import AbyssData
from logic.explain import explain_cell
from logic.pathfinding import find_route


# Load datasets once (fast + prevents constant reloading)
data = AbyssData()


def handle_query(query: str):
    """
    Main backend router.
    Takes a user query in natural language,
    extracts intent + coordinates,
    executes the correct module,
    and returns a unified payload for Streamlit.
    """

    intent = classify_intent(query)
    itype = intent["intent"]
    coords = intent["coords"]

    # 1. Exlanation and Coordinate Lookups
    if itype in ["coordinate_info", "explain_region"]:
        if coords is None:
            return {
                "intent": "EXPLAIN",
                "answer": "Please specify coordinates like (row, col)."
            }

        r, c = coords
        return explain_cell(data, r, c)

    # 2. Route-Finding (Safe / balanced)
    if itype in ["safe_route", "fast_route"]:

        # Extract coordinates: expecting two of them
        matches = re.findall(r"\(?\s*(\d+)\s*,\s*(\d+)\s*\)?", query)
        if len(matches) < 2:
            return {
                "intent": "ROUTE",
                "answer": "Specify start AND end coordinates, e.g., (2,3) to (10,15)."
            }

        start = (int(matches[0][0]), int(matches[0][1]))
        end   = (int(matches[1][0]), int(matches[1][1]))

        path, cost = find_route(start, end, data)

        if path is None:
            return {
                "intent": "ROUTE",
                "answer": "No viable route was found between these coordinates."
            }

        return {
            "intent": "ROUTE",
            "answer": f"Found a route from {start} to {end} with total risk cost {cost:.2f}.",
            "path": [{"row": r, "col": c} for (r, c) in path],
            "highlights": [],
            "stats": {"cost": cost}
        }
    
    # 3. Mining and Resource Analysis
    if itype == "mining":
        scored = []
        coords = []

        # score each cell
        for (r, c), cell in data.cell_index.items():
            danger = danger_score(cell, data.get_hazards(r,c), data.get_currents(r,c))
            eco = eco_impact_score(data.get_corals(r,c), data.get_life(r,c), data.get_resources(r,c))
            resource = resource_score(data.get_resources(r,c))
            combined = combined_score(danger, eco, resource, mode="mining")
            
            scored.append(combined)
            coords.append((r,c))

        # Build heatmap 50x50
        import numpy as np
        heatmap = np.zeros((50,50))
        for idx, (r,c) in enumerate(coords):
            heatmap[r][c] = scored[idx]

        # Top 5 mining zones
        top_idx = np.argsort(scored)[-5:]
        highlights = [{"row": coords[i][0], "col": coords[i][1]} for i in top_idx]

        return {
            "intent": "MINING",
            "answer": "Here are the top recommended mining zones balancing profit and ecological impact.",
            "heatmap": heatmap.tolist(),
            "highlights": highlights,
        }


    # 4. Conservation Anlysis
    if itype == "conservation":
        from logic.scoring import (
            danger_score,
            eco_impact_score,
            resource_score,
            combined_score
        )
        import numpy as np

        scored = []
        coords_list = []

        # Iterate through every cell in the grid
        for (r, c), cell in data.cell_index.items():

            danger = danger_score(cell, data.get_hazards(r, c), data.get_currents(r, c))
            eco = eco_impact_score(
                data.get_corals(r, c),
                data.get_life(r, c),
                data.get_resources(r, c)
            )
            resource = resource_score(data.get_resources(r, c))

            # Conservation mode → fragile = high score
            combined = combined_score(danger, eco, resource, mode="conservation")

            scored.append(combined)
            coords_list.append((r, c))

        # Build heatmap
        heatmap = np.zeros((50, 50))
        for idx, (r, c) in enumerate(coords_list):
            heatmap[r][c] = scored[idx]

        # Highlight 5 most fragile ecological zones
        top_idx = np.argsort(scored)[-5:]
        highlights = [{"row": coords_list[i][0], "col": coords_list[i][1]} for i in top_idx]

        return {
            "intent": "CONSERVATION",
            "answer": "These regions are highly sensitive ecological zones.",
            "heatmap": heatmap.tolist(),
            "highlights": highlights
        }


    # 5. Biodiversity and Hazard (using explain engine)
    if itype in ["life_analysis", "hazard_analysis", "poi_lookup"]:
        if coords is None:
            return {"answer": "Please include coordinates for analysis."}
        r, c = coords
        return explain_cell(data, r, c)

    # 6. Fallback
    return {
        "intent": "UNKNOWN",
        "answer": (
            "I couldn’t understand your request. "
            "Try asking about routes, hazards, resources, biodiversity, or coordinates."
        )
    }
