from __future__ import annotations
from typing import Tuple, List
import networkx as nx
from .data_loader import AbyssData
from .scoring import score_cell

Coord = Tuple[int, int]
# Allowed moves: down, up, right, left (no diagonals)
DIRS: list[Coord] = [(1,0), (-1,0), (0,1), (0,-1)]


def _neighbours(coord: Coord, max_row: int, max_col: int):
    r, c = coord
    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < max_row and 0 <= nc < max_col:
            yield (nr, nc)


def _route_cost(coord: Coord, data: AbyssData, mode="safe_route"):
    """
    Cost of stepping INTO a neighbour cell.
    Mode controls behavior:
      - safe_route = avoid danger
      - fast_route = ignore danger, choose shortest path
    """
    row, col = coord
    if data.get_cell(row, col) is None:
        return float("inf")

    # Use correct scoring mode
    risk_cost = score_cell(data, row, col, mode=mode)

    # Every step costs at least 1
    return 1.0 + risk_cost


def build_graph(data: AbyssData, mode="safe_route") -> nx.DiGraph:
    """
    Build the navigation graph with weights depending on route mode.
    """
    G = nx.DiGraph()
    max_row = int(data.cells["row"].max()) + 1
    max_col = int(data.cells["col"].max()) + 1

    # Add nodes
    for coord in data.cell_index.keys():
        G.add_node(coord)

    # Add weighted edges
    for coord in data.cell_index.keys():
        for nb in _neighbours(coord, max_row, max_col):
            if data.get_cell(*nb) is None:
                continue
            cost = _route_cost(nb, data, mode)
            G.add_edge(coord, nb, weight=cost)

    return G


def find_route(start: Coord, end: Coord, data: AbyssData, mode="safe_route") -> tuple[List[Coord] | None, float]:
    """
    Compute the path using Dijkstra with mode-specific weights.
    """
    G = build_graph(data, mode=mode)

    if start not in G or end not in G:
        return None, float("inf")

    try:
        path = nx.shortest_path(G, source=start, target=end, weight="weight")
        total_cost = nx.path_weight(G, path, weight="weight")
        return path, total_cost
    except nx.NetworkXNoPath:
        return None, float("inf")
