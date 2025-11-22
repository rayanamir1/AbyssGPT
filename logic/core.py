import re
import numpy as np
import streamlit as st

# ---------------------------
# Intent detection (rule-based)
# ---------------------------
def detect_intent(query: str):
    q = query.lower()

    if any(k in q for k in ["route", "path", "from", "to", "safe route"]):
        return "ROUTE"

    if any(k in q for k in ["best", "mining", "extract", "profit", "resource", "optimal zone"]):
        return "RECOMMEND_ZONES"

    if any(k in q for k in ["explain", "why", "describe", "what is", "tell me about"]):
        return "EXPLAIN"

    return "UNKNOWN"


# ---------------------------
# Simple scoring placeholders
# (your teammate can upgrade later)
# ---------------------------
def danger_score(cell, hazards_df, currents_df):
    r, c = int(cell["row"]), int(cell["col"])

    hz = hazards_df[(hazards_df.row == r) & (hazards_df.col == c)]
    hazard_severity = float(hz.severity.sum()) if len(hz) else 0.0

    cur = currents_df[(currents_df.row == r) & (currents_df.col == c)]
    instability = float(1 - cur.stability.values[0]) if len(cur) else 0.0

    depth_factor = float(cell["depth_m"]) / 6000.0
    return 0.6 * hazard_severity + 0.3 * instability + 0.1 * depth_factor


def resource_score(cell, resources_df):
    r, c = int(cell["row"]), int(cell["col"])
    res = resources_df[(resources_df.row == r) & (resources_df.col == c)]
    if len(res) == 0:
        return 0.0

    value = float(res.economic_value.values[0])
    abundance = float(res.abundance.values[0])
    difficulty = float(res.extraction_difficulty.values[0])
    return (value * abundance) - difficulty


def eco_impact_score(cell, corals_df, resources_df):
    r, c = int(cell["row"]), int(cell["col"])

    coral = corals_df[(corals_df.row == r) & (corals_df.col == c)]
    coral_damage = 0.0
    if len(coral):
        coral_damage = (float(coral.coral_cover_pct.values[0]) / 100.0) * float(coral.health_index.values[0])

    res = resources_df[(resources_df.row == r) & (resources_df.col == c)]
    extraction_impact = float(res.environmental_impact.values[0]) if len(res) else 0.0

    return 0.5 * coral_damage + 0.5 * extraction_impact


# ---------------------------
# Template explanation generator
# ---------------------------
def explain_cell(cell, hazards_df, corals_df, resources_df, currents_df):
    parts = []
    parts.append(
        f"This cell is at ~{int(cell['depth_m'])} m in a **{cell['biome']}** biome "
        f"with temperature around {cell['temperature_c']:.1f}°C."
    )

    hz = hazards_df[(hazards_df.row == cell.row) & (hazards_df.col == cell.col)]
    if len(hz):
        parts.append(
            f"It contains a **{hz.type.values[0]}** hazard (severity {hz.severity.values[0]:.2f}), "
            "so manned operations are higher risk."
        )

    coral = corals_df[(corals_df.row == cell.row) & (corals_df.col == cell.col)]
    if len(coral):
        hi = float(coral.health_index.values[0])
        bi = float(coral.biodiversity_index.values[0])
        if hi > 0.7 and bi > 0.7:
            parts.append("Coral health and biodiversity are high, making this ecologically valuable.")
        elif hi < 0.3:
            parts.append("Coral health is low, suggesting sensitivity or prior disturbance.")

    res = resources_df[(resources_df.row == cell.row) & (resources_df.col == cell.col)]
    if len(res):
        parts.append(
            f"Resources detected: **{res.type.values[0]}** with economic value "
            f"{float(res.economic_value.values[0]):.2f}."
        )

    cur = currents_df[(currents_df.row == cell.row) & (currents_df.col == cell.col)]
    if len(cur) and float(cur.speed_mps.values[0]) > 1.5:
        parts.append("Currents are strong here, which increases navigation difficulty.")

    return " ".join(parts)


# ---------------------------
# MAIN ENTRYPOINT your chat calls
# ---------------------------
def handle_query(query: str):
    dfs = st.session_state.dfs
    cells = dfs["cells"]
    hazards = dfs["hazards"]
    currents = dfs["currents"]
    corals = dfs["corals"]
    resources = dfs["resources"]

    intent = detect_intent(query)

    # ---------------- EXPLAIN ----------------
    if intent == "EXPLAIN":
        # If user gave a coordinate like (12,33), parse it.
        m = re.search(r"\((\d+)\s*,\s*(\d+)\)", query)
        if m:
            r, c = int(m.group(1)), int(m.group(2))
            cell_row = cells[(cells.row == r) & (cells.col == c)]
        else:
            # default cell for now (center-ish)
            cell_row = cells[(cells.row == 25) & (cells.col == 25)]

        if len(cell_row) == 0:
            return {"answer": "I couldn't find that cell. Try another coordinate."}

        cell = cell_row.iloc[0]
        answer = explain_cell(cell, hazards, corals, resources, currents)

        stats = {
            "danger": float(danger_score(cell, hazards, currents)),
            "ecoImpact": float(eco_impact_score(cell, corals, resources)),
            "resource": float(resource_score(cell, resources))
        }

        return {
            "intent": "EXPLAIN",
            "answer": answer,
            "highlights": [{"row": int(cell.row), "col": int(cell.col)}],
            "stats": stats
        }

    # ---------------- RECOMMEND ----------------
    if intent == "RECOMMEND_ZONES":
        scored = []
        for _, cell in cells.iterrows():
            rs = resource_score(cell, resources)
            es = eco_impact_score(cell, corals, resources)
            ds = danger_score(cell, hazards, currents)
            combined = rs - 1.2*es - 0.5*ds
            scored.append(combined)

        scored = np.array(scored)
        top_idx = scored.argsort()[-5:][::-1]
        top_cells = cells.iloc[top_idx]

        highlights = [
            {"row": int(r), "col": int(c), "score": float(sc)}
            for (r, c, sc) in zip(top_cells.row, top_cells.col, scored[top_idx])
        ]

        answer = (
            "Here are the top mining zones balancing high economic value with low coral impact "
            "and manageable hazard risk."
        )

        return {
            "intent": "RECOMMEND_ZONES",
            "answer": answer,
            "highlights": highlights,
            # optional heatmap for map panel later:
            "heatmap": scored.reshape(50, 50).tolist()
        }

    # ---------------- ROUTE ----------------
    if intent == "ROUTE":
        # For now, just parse start/end like (r1,c1) to (r2,c2)
        coords = re.findall(r"\((\d+)\s*,\s*(\d+)\)", query)
        if len(coords) >= 2:
            (r1, c1), (r2, c2) = coords[0], coords[1]
            start, end = (int(r1), int(c1)), (int(r2), int(c2))
        else:
            start, end = (0, 0), (49, 49)

        # STUB PATH (real A* comes later)
        path = [{"row": start[0], "col": start[1]}, {"row": end[0], "col": end[1]}]

        answer = f"Plotted a safe route from {start} to {end}. (Routing engine placeholder for now.)"

        return {
            "intent": "ROUTE",
            "answer": answer,
            "path": path,
            "stats": {"danger": 0.0, "ecoImpact": 0.0, "resource": 0.0}
        }

    # ---------------- UNKNOWN ----------------
    return {
        "intent": "UNKNOWN",
        "answer": "Try asking about hazards, mining, biodiversity, or a route between two points."
    }
