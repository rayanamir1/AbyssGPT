import numpy as np
import plotly.graph_objects as go
import streamlit as st

def _build_matrix_from_cells(cells_df, value_col: str = "depth_m"):
    """
    Turn the flat cells dataframe into a 2D matrix [row][col] of the chosen value.
    Assumes cells_df has integer columns named 'row' and 'col'.
    """
    max_row = int(cells_df["row"].max())
    max_col = int(cells_df["col"].max())
    # +1 because rows/cols start at 0
    matrix = np.full((max_row + 1, max_col + 1), np.nan, dtype=float)

    for _, cell in cells_df.iterrows():
        r = int(cell["row"])
        c = int(cell["col"])
        matrix[r, c] = float(cell[value_col])

    return matrix

def build_default_map():
    """
    Default background map if no specific heatmap is provided.
    Here we use depth as the base layer.
    """
    dfs = st.session_state.dfs
    cells = dfs["cells"]
    mat = _build_matrix_from_cells(cells, value_col="depth_m")
    fig = go.Figure(
        data=go.Heatmap(
            z=mat,
            colorscale="Viridis",
            colorbar=dict(title="Depth (m)"),
            hovertemplate="Row: %{y}<br>Col: %{x}<br>Depth: %{z}<extra></extra>",
        )
    )
    _style_common(fig)
    return fig

def render_heatmap(heatmap_list):
    """
    Render a generic heatmap from a 2D Python list (e.g. scoring grid).
    """
    z = np.array(heatmap_list, dtype=float)
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            colorscale="Viridis",
            colorbar=dict(title="Score"),
            hovertemplate="Row: %{y}<br>Col: %{x}<br>Value: %{z}<extra></extra>",
        )
    )
    _style_common(fig)
    return fig

def add_route(fig, path):
    """
    Draw a route as a line over the existing heatmap.
    `path` is a list of dicts: {"row": int, "col": int}
    """
    if not path:
        return fig

    xs = [p["col"] for p in path]
    ys = [p["row"] for p in path]

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines+markers",
            name="Route",
            line=dict(width=3),
            marker=dict(size=6),
            hoverinfo="skip",
        )
    )
    return fig

def add_highlights(fig, highlights):
    """
    Highlight individual cells as X markers.
    `highlights` is a list of dicts: {"row": int, "col": int}
    """
    if not highlights:
        return fig

    xs = [h["col"] for h in highlights]
    ys = [h["row"] for h in highlights]

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            name="Highlights",
            marker=dict(size=10, symbol="x"),
            hoverinfo="skip",
        )
    )
    return fig

def _style_common(fig):
    """
    Shared axis styling so the grid looks like a proper map.
    """
    fig.update_layout(
        xaxis=dict(
            title="Column",
            constrain="domain",
            scaleanchor="y",
            scaleratio=1,
        ),
        yaxis=dict(
            title="Row",
            autorange="reversed",  # so row 0 appears at the top
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=700,
    )
