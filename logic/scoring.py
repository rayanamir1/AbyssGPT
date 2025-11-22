"""
Scoring engine for AbyssGPT

This module computes:
- danger_score      ; how risky a cell is
- resource_score    ; how economically attractive a cell is
- eco_impact_score  ; how ecologically sensitive a cell is
- combined_score    ; merges scores based on intent
- score_cell        ; master scoring wrapper

Weights tuned for hackathon performance:
Balanced, stable, intuitive.
"""

from typing import Dict, Any, List

# Danger Score

def danger_score(
    cell: Dict[str, Any],
    hazards: List[Dict[str, Any]],
    currents: List[Dict[str, Any]]
) -> float:
    """
    Computes risk level of a cell.
    Higher = more dangerous.
    """
    score = 0.0

    # Depth
    depth = cell.get("depth_m", 0)
    depth_norm = min(depth / 7000, 1.0) # normalized 0–1
    score += depth_norm * 0.25 # using a weight of 25%

    # Hazards
    for hz in hazards:
        severity = hz.get("severity", 0)
        score += severity * 0.55 # hazards are the most dominant factor

    # Currents; strong and unstable currents contribute
    if currents:
        c = currents[0]
        speed = c.get("speed_mps", 0)
        stability = c.get("stability", 1.0)

        score += (speed / 5) * 0.15 # normalize the speed (max ~5 m/s)
        score += (1 - stability) * 0.25 # instability is extra risk

    return float(score)

# Resource Score
def resource_score(resources: List[Dict[str, Any]]) -> float:
    """
    Economic attractiveness of a mining zone.
    Higher = more valuable.
    """
    if not resources:
        return 0.0

    score = 0.0
    for r in resources:
        abundance = r.get("abundance", 0)
        value = r.get("economic_value", 0)
        purity = r.get("purity", 0)

        score += (
            abundance * 0.35 +
            value * 0.50 +
            purity * 0.15
        )

    return float(score)

# Ecological Impact Score
def eco_impact_score(
    corals: List[Dict[str, Any]],
    life: List[Dict[str, Any]],
    resources: List[Dict[str, Any]]
) -> float:
    """
    Ecological sensitivity of a cell.
    Higher = more ecologically fragile → worse for mining.
    """
    score = 0.0

    # Coral Sensitivity
    for c in corals:
        health = c.get("health_index", 0)
        biodiversity = c.get("biodiversity_index", 0)
        score += (health + biodiversity) * 0.4

    # Overall Species that are at risk
    for sp in life:
        density = sp.get("density", 0)
        threat = sp.get("threat_level", 0)
        score += density * threat * 0.25

    # Extraction difficulty and Invronmental Impact
    for r in resources:
        impact = r.get("environmental_impact", 0)
        difficulty = r.get("extraction_difficulty", 0)
        score += impact * 0.30 + difficulty * 0.10

    return float(score)

# The Combined Score (This is unified across intents)
def combined_score(
    danger: float,
    eco: float,
    resource: float,
    mode: str = "balanced"
) -> float:
    """
    Merge scores depending on intent:
      - mining       (maximize resources, minimize eco damage)
      - conservation (highlight high eco sensitivity)
      - safe_route   (for A* routing)
      - balanced     (general analysis)
    """

    mode = mode.lower()

    if mode == "mining":
        return (resource * 1.0) - (0.35 * danger) - (0.55 * eco)

    if mode == "conservation":
        return -(eco * 1.0) - (0.25 * danger)

    if mode == "safe_route":
        # A* uses the cost, danger is the cost and eco is the slight modifier
        return (danger * 1.0) + (0.25 * eco)

    # Default; this is balanced
    return resource - (0.25 * danger) - (0.35 * eco)

# Master Wrapper: this is the score_cell()
def score_cell(data, row: int, col: int, mode: str = "balanced") -> float:
    """
    Compute the final combined score for a cell.
    This is what pathfinding & zone recommendation will call.
    """

    cell = data.get_cell(row, col)
    if cell is None:
        return float("inf") # invalid cell

    hazards = data.get_hazards(row, col)
    corals = data.get_corals(row, col)
    resources = data.get_resources(row, col)
    life = data.get_life(row, col)

    # currents.csv is a table, this is finding a specific row
    currents = data.get_currents(row, col)

    d = danger_score(cell, hazards, currents)
    r = resource_score(resources)
    e = eco_impact_score(corals, life, resources)

    return combined_score(d, e, r, mode)

# Risk Rationale - returns not only numbers, but why a cell was dangerous
def danger_breakdown(cell, hazards, currents):
    depth = cell.get("depth_m", 0)
    hazard_count = len(hazards)
    current_speed = currents[0].get("speed_mps", 0) if currents else 0

    return {
        "depth_m": depth,
        "hazard_count": hazard_count,
        "current_speed": current_speed,
        "hazards_present": [h.get("type", "unknown") for h in hazards]
    }

# Dynamic weighting 
def adaptive_weights(cell):
    depth = cell.get("depth_m", 0)

    if depth > 4000:
        # within deep ocean; danger is more important
        return {"danger": 0.5, "eco": 0.3, "resource": 0.2}
    else:
        # near coral reefs; eco is more important
        return {"danger": 0.3, "eco": 0.5, "resource": 0.2}
    
# Modifying combined_score to optionally accept weights
def combined_score_with_weights(danger, eco, resource, weights):
    return (
        resource * weights["resource"] -
        danger * weights["danger"] -
        eco * weights["eco"]
    )

# Global Normalization layer
def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0
    return (value - min_val) / (max_val - min_val)



