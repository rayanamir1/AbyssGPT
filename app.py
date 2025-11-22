import streamlit as st
st.set_page_config(layout="wide")   # MUST be first Streamlit command

import pandas as pd

# --- import chat renderer ---
from ui.chat import render_chat

# Backend core handler
from logic.core import handle_query

# Map utilities
from ui.map import render_heatmap, add_route, build_default_map, add_highlights


# ---------------------------
# Data loading (cached)
# ---------------------------
@st.cache_data
def load_data():
    cells = pd.read_csv("data/cells.csv")
    hazards = pd.read_csv("data/hazards.csv")
    currents = pd.read_csv("data/currents.csv")
    corals = pd.read_csv("data/corals.csv")
    resources = pd.read_csv("data/resources.csv")
    life = pd.read_csv("data/life.csv")
    poi = pd.read_csv("data/poi.csv")

    cells_lookup = cells.set_index(["row", "col"]).to_dict(orient="index")
    return cells, hazards, currents, corals, resources, life, poi, cells_lookup


cells, hazards, currents, corals, resources, life, poi, cells_lookup = load_data()

# Store datasets for backend use
if "dfs" not in st.session_state:
    st.session_state.dfs = {
        "cells": cells,
        "hazards": hazards,
        "currents": currents,
        "corals": corals,
        "resources": resources,
        "life": life,
        "poi": poi,
        "cells_lookup": cells_lookup
    }


# ---------------------------
# Page layout
# ---------------------------
st.title("🌊 AbyssGPT — Deep Sea Intelligence Assistant")

col1, col2 = st.columns([3, 2])

# LEFT PANEL — MAP
with col1:
    st.subheader("Map")

    payload = st.session_state.get("last_payload")

    if payload is None:
        st.info("Ask AbyssGPT a question to visualize data here.")
        fig = build_default_map()
    else:
        st.caption(f"Intent: {payload.get('intent', 'UNKNOWN')}")

        # 1) Base heatmap
        if payload.get("heatmap"):
            fig = render_heatmap(payload["heatmap"])
        else:
            fig = build_default_map()

        # 2) Route overlay
        if payload.get("path"):
            fig = add_route(fig, payload["path"])

        # 3) Highlight cells
        if payload.get("highlights"):
            fig = add_highlights(fig, payload["highlights"])

    # 4) Render figure (click-to-explain removed for stability)
    st.plotly_chart(fig, use_container_width=True)

# RIGHT PANEL — CHAT
with col2:
    render_chat(height=400)
    with st.expander("Route cost legend"):
        st.markdown(
            "- Cost blends **distance** with weighted risk layers.\n"
            "- **Danger**: hazards, depth/pressure, unstable or fast currents.\n"
            "- **Eco impact**: coral health/biodiversity and extraction impact of resources.\n"
            "- Lower cost: safer and lower impact route."
        )
    with st.expander("Score definitions"):
        st.markdown(
            "- **Danger score**: risk from depth/pressure, hazards, and current speed/stability.\n"
            "- **Resource score**: economic attractiveness from abundance, value, and purity.\n"
            "- **Eco impact score**: ecological sensitivity from coral health/biodiversity and extraction impact/difficulty.\n"
            "- **Combined score**: weighted merge of danger, eco, and resource per intent (e.g., mining, conservation, routing).\n"
            "- **Score cell**: master wrapper that fetches cell context and returns the combined score for that (row, col)."
        )
