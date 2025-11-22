from __future__ import annotations
from typing import Tuple, List
import networkx as nx
from .data_loader import AbyssData
from .scoring import (score_cell)

Coord = Tuple[int, int]
# Allowed moves; down, up, right, left (no diagonals)
DIRS: list[Coord] = [(1,0), (-1,0), (0,1), (0,-1)]

def _neighbours(coord: Coord, max_row: int, max_col: int):
    """
    Given a cell (Row, Column), yield valid neighbours in cell
    """
    r, c = coord
    for dr, dc in DIRS: # delta row, delta column
        nr, nc = r + dr, c + dc # neighbour row, neioghbour column
        if 0 <= nr < max_row and 0 <= nc < max_col: # stay in grid bounds
            yield(nr,nc)

def _build_cell_features(row: int, col: int, data: AbyssData) -> dict | None:
    """
    Build a single cell dictionary for this (row, column).
    scoring.py can read everything from this one place
    """
    base = data.get_cell(row,col)
    if base is None:
        return None
    
    # Start with core information from cells.csv
    cell = dict(base)   # So we dont have to modify the original row

    # Hazards
    hazards = data.get_hazards(row, col)
    if hazards:
        worst = max(hazards, key=lambda h: h.get("severity", 0.0))
        cell["hazard_type"] = worst.get("type")
        cell["hazard_severity"] = worst.get("severity", 0.0)
    else:   # No hazard rows
        cell.setdefault("hazard_type", None)
        cell.setdefault("hazard_severity", 0.0)
    
    # Corals
    corals = data.get_corals(row, col)
    if corals:
        c = corals[0]   # Use first coral record
        cell["coral_cover_pct"] = c.get("coral_cover_pct", 0.0)
        cell["coral_health_index"] = c.get("health_index", 0.0)
        cell["biodiversity_index"] = c.get("biodiversity_index", 0.0)
    else:   # No coral data
        cell.setdefault("coral_cover_pct", 0.0)
        cell.setdefault("coral_health_index", 0.0)
        cell.setdefault("biodiversity_index", 0.0)
   
    # Resources
    resources = data.get_resources(row, col)
    if resources:
        r = resources[0]    # Use first resource row
        cell["resource_abundance"] = r.get("abundance", 0.0)
        cell["economic_value"] = r.get("economic_value", 0.0)
        cell["extraction_difficulty"] = r.get("extraction_difficulty", 0.0)
        cell["environmental_impact"] = r.get("environmental_impact", 0.0)
    else:   # No resources data
        cell.setdefault("resource_abundance", 0.0)
        cell.setdefault("economic_value", 0.0)
        cell.setdefault("extraction_difficulty", 0.0)
        cell.setdefault("environmental_impact", 0.0)

    # Currents
    currents = data.get_currents(row, col)
    if currents:
        cur = currents[0]
        cell["current_speed_mps"] = cur.get("speed_mps", 0.0)
        cell["current_stability"] = cur.get("stability", 1.0)
    else:
        cell.setdefault("current_speed_mps", 0.0)
        cell.setdefault("current_stability", 1.0)

    return cell

def _route_cost(coord: Coord, data: AbyssData) -> float:
    """
    Cost of moving into this coordinate
    Bigger number = worse || try to avoid high-cost cells

    """

    row, col = coord
    if data.get_cell(row, col) is None:
        return float("inf")
    
    risk_cost = score_cell(data, row, col, mode="safe_route")   # Risk cost from scoring.py
    base_step_cost = 1.0    # Every move costs atleast 1

    return base_step_cost + risk_cost

def build_graph(data: AbyssData) -> nx.DiGraph:
    """
    Find best route from start to end
    Edge node = (row, col)
    Edges go from cell to each of their neighbours
    Edge weight for stepping into the grid
    """
    G = nx.DiGraph()    # Empty graph
    max_row = int(data.cells["row"].max()) + 1  # Use these to stay in grid bounds
    max_col = int(data.cells["col"].max()) + 1  

    # Add nodes for each known cell
    for coord in data.cell_index.keys():
        G.add_node(coord)
    
    # Add edges with weights to neighbours
    for coord in data.cell_index.keys():
        for nb in _neighbours(coord, max_row, max_col):
            if data.get_cell(*nb) is None:
                continue    # Skip the non existent cells
            
            cost = _route_cost(nb, data)
            G.add_edge(coord, nb, weight=cost)
    return G

def find_route(start: Coord, end: Coord, data: AbyssData,) -> tuple[List[Coord] | None, float]:
    """
    Find safest route from start to end
    NetworkX shortest_path with our risk based edge weights
    returns a list of coordinates, or None if no path exists
    and total cost for the path
    """
    G = build_graph(data)   # Build graph
    if start not in G or end not in G:
        return None, float("inf")   # if not in G, none ofr path, infinity for cost
    
    try:   # Uses Dijkstras algorithm
        path: List[Coord] = nx.shortest_path(G, source = start, target = end, weight="weight")
        total_cost: float = nx.path_weight(G, path, weight="weight")
        return path, total_cost
    except nx.NetworkXNoPath:
        return None, float("inf")