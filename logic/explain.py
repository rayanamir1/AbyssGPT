"""
Template-driven explanation builder for a single grid cell.
Consumes AbyssData lookups, scores the cell, and returns text + map metadata.
"""

from typing import Dict, Any, List
from logic.scoring import (
    danger_score,
    resource_score,
    eco_impact_score,
    adaptive_weights,
    combined_score_with_weights,
    danger_breakdown,
)


def explain_cell(data, row: int, col: int) -> Dict[str, Any]:
    """
    Fetch context for (row, col), compute scores, and assemble a narrative.
    Returns an intent payload the UI can render (text, highlights, stats).
    """
    cell = data.get_cell(row, col)
    if not cell:
        return {
            "intent": "EXPLAIN",
            "answer": "I couldn't find that cell. Try another coordinate.",
            "highlights": [],
            "stats": {},
        }

    # Pull all layers for this coordinate
    hazards = data.get_hazards(row, col)
    corals = data.get_corals(row, col)
    resources = data.get_resources(row, col)
    life = data.get_life(row, col)
    currents = data.get_currents(row, col)
    poi = data.get_poi(row, col)

    # Compute core scores and a combined weighted score
    danger = danger_score(cell, hazards, currents)
    resource = resource_score(resources)
    eco = eco_impact_score(corals, life, resources)
    weights = adaptive_weights(cell)
    combined = combined_score_with_weights(danger, eco, resource, weights)

    # Build narrative from template snippets
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
    }


def _describe_cell(cell: Dict[str, Any]) -> str:
    """Base physical context: depth, biome, and temperature."""
    return (
        f"This cell sits at ~{int(cell.get('depth_m', 0))} m in a {cell.get('biome', 'unknown')} biome "
        f"with temperature around {cell.get('temperature_c', 0):.1f}°C."
    )


def _describe_currents(currents: List[Dict[str, Any]]) -> str:
    """Summarize current speed and stability if present."""
    if not currents:
        return ""
    c = currents[0]
    speed = c.get("speed_mps", 0)
    stab = c.get("stability", 1.0)
    note = "stable" if stab > 0.7 else "unstable"
    if speed > 1.5:
        return f"Currents are {note} and strong (~{speed:.1f} m/s), adding nav risk."
    return f"Currents are {note} (~{speed:.1f} m/s)."


def _describe_hazards(hazards: List[Dict[str, Any]]) -> str:
    """Call out the most salient hazard, if any."""
    if not hazards:
        return "No major hazards recorded."
    hz = hazards[0]
    return f"Contains a {hz.get('type', 'hazard')} (severity {hz.get('severity', 0):.2f}), raising operational risk."


def _describe_corals(corals: List[Dict[str, Any]]) -> str:
    """Describe coral health/biodiversity as an eco-sensitivity signal."""
    if not corals:
        return ""
    c = corals[0]
    health = c.get("health_index", 0)
    biod = c.get("biodiversity_index", 0)
    cover = c.get("coral_cover_pct", 0)
    if health > 0.7 and biod > 0.7:
        return f"High coral health (H={health:.2f}, B={biod:.2f}, cover ~{cover:.0f}%), ecologically valuable."
    if health < 0.3:
        return f"Coral health is low (H={health:.2f}), indicating sensitivity or prior disturbance."
    return f"Moderate coral presence (H={health:.2f}, B={biod:.2f}, cover ~{cover:.0f}%)."


def _describe_resources(resources: List[Dict[str, Any]]) -> str:
    """Surface the headline resource family/value/impact."""
    if not resources:
        return "No notable resource deposits logged."
    r = resources[0]
    fam = r.get("family", r.get("type", "resource"))
    val = r.get("economic_value", 0)
    impact = r.get("environmental_impact", 0)
    return f"Resources: {fam} (value {val:.2f}, impact {impact:.2f}); check extraction difficulty."


def _describe_life(life: List[Dict[str, Any]]) -> str:
    """Mention a representative species if present."""
    if not life:
        return ""
    sp = life[0]
    return f"Species noted: {sp.get('species', 'unknown')} (density {sp.get('density', 0)}, threat {sp.get('threat_level', 0)})."


def _describe_poi(poi: List[Dict[str, Any]]) -> str:
    """Highlight a point of interest on this cell, if any."""
    if not poi:
        return ""
    p = poi[0]
    return f"Point of interest: {p.get('label', p.get('category', 'POI'))} — {p.get('description', '')}"
