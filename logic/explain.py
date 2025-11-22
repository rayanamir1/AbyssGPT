from typing import Dict, Any, List
from logic.scoring import (
    danger_score,
    resource_score,
    eco_impact_score,
    adaptive_weights,
    combined_score_with_weights,
    danger_breakdown,
)

# --- safe float helper ---
def _f(x):
    try:
        return float(x)
    except:
        return 0.0


def explain_cell(data, row: int, col: int) -> Dict[str, Any]:
    cell = data.get_cell(row, col)
    if not cell:
        return {
            "intent": "EXPLAIN",
            "answer": "I couldn't find that cell. Try another coordinate.",
            "highlights": [],
            "stats": {},
        }

    # Pull layers
    hazards = data.get_hazards(row, col)
    corals = data.get_corals(row, col)
    resources = data.get_resources(row, col)
    life = data.get_life(row, col)
    currents = data.get_currents(row, col)
    poi = data.get_poi(row, col)

    # Compute scores
    danger = danger_score(cell, hazards, currents)
    resource = resource_score(resources)
    eco = eco_impact_score(corals, life, resources)
    weights = adaptive_weights(cell)
    combined = combined_score_with_weights(danger, eco, resource, weights)

    parts = [
        _describe_cell(cell),
        _describe_currents(currents),
        _describe_hazards(hazards),
        _describe_corals(corals),
        _describe_resources(resources),
        _describe_life(life),
        _describe_poi(poi),
    ]
    answer = " ".join([p for p in parts if p])

    return {
        "intent": "EXPLAIN",
        "answer": answer,
        "highlights": [{"row": row, "col": col}],
        "stats": {
            "danger": danger,
            "ecoImpact": eco,
            "resource": resource,
            "combined": combined,
        },
        "breakdown": {
            "danger": danger_breakdown(cell, hazards, currents),
        },
        "source": "cells.csv, hazards.csv, currents.csv, corals.csv, resources.csv, life.csv, poi.csv",
        "important_info": [
            f"Danger: {danger:.2f}",
            f"Eco impact: {eco:.2f}",
            f"Resource: {resource:.2f}",
            f"Combined: {combined:.2f}"
        ],
    }


def _describe_cell(cell):
    depth = _f(cell.get("depth_m", 0))
    temp = _f(cell.get("temperature_c", 0))
    biome = cell.get("biome", "unknown")

    return (
        f"This cell sits at ~{int(depth)} m in a {biome} biome "
        f"with temperature around {temp:.1f}°C."
    )


def _describe_currents(currents):
    if not currents:
        return ""

    c = currents[0]
    speed = _f(c.get("speed_mps", 0))
    stability = _f(c.get("stability", 1.0))

    note = "stable" if stability > 0.7 else "unstable"

    if speed > 1.5:
        return f"Currents are {note} and strong (~{speed:.1f} m/s), adding nav risk."

    return f"Currents are {note} (~{speed:.1f} m/s)."


def _describe_hazards(hazards):
    if not hazards:
        return "No major hazards recorded."

    hz = hazards[0]
    t = hz.get("type", "hazard")
    severity = _f(hz.get("severity", 0))
    return f"Contains a {t} (severity {severity:.2f}), raising operational risk."


def _describe_corals(corals):
    if not corals:
        return ""

    c = corals[0]
    health = _f(c.get("health_index", 0))
    biod = _f(c.get("biodiversity_index", 0))
    cover = _f(c.get("coral_cover_pct", 0))

    if health > 0.7 and biod > 0.7:
        return f"High coral health (H={health:.2f}, B={biod:.2f}, cover ~{cover:.0f}%), ecologically valuable."
    if health < 0.3:
        return f"Coral health is low (H={health:.2f}), indicating sensitivity or prior disturbance."

    return f"Moderate coral presence (H={health:.2f}, B={biod:.2f}, cover ~{cover:.0f}%)."


def _describe_resources(resources):
    if not resources:
        return "No notable resource deposits logged."

    r = resources[0]
    fam = r.get("family", r.get("type", "resource"))
    val = _f(r.get("economic_value", 0))
    impact = _f(r.get("environmental_impact", 0))

    return f"Resources: {fam} (value {val:.2f}, impact {impact:.2f}); check extraction difficulty."


def _describe_life(life):
    if not life:
        return ""

    sp = life[0]
    density = _f(sp.get("density", 0))
    threat = _f(sp.get("threat_level", 0))

    return f"Species noted: {sp.get('species', 'unknown')} (density {density}, threat {threat})."


def _describe_poi(poi):
    if not poi:
        return ""

    p = poi[0]
    return f"Point of interest: {p.get('label', p.get('category', 'POI'))} — {p.get('description', '')}"
