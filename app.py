import pandas as pd
import streamlit as st

# --- import chat renderer ---
from ui.chat import render_chat

# ❗ FIXED: import handle_query from core backend, NOT explain
from logic.core import handle_query

# ---------------------------
# Data loading (cache so it doesn't reload every interaction)
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
st.set_page_config(layout="wide")
st.title("🌊 AbyssGPT — Deep Sea Intelligence Assistant")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Map")

    payload = st.session_state.get("last_payload")

    if payload is None:
        st.info("Ask AbyssGPT a question to visualize data here.")
    else:
        st.write("Map payload received:")
        st.json({
            "intent": payload.get("intent"),
            "has_heatmap": payload.get("heatmap") is not None,
            "has_path": payload.get("path") is not None,
            "num_highlights": len(payload.get("highlights", []))
        })

        # Example hooks (implement these later)
        # if payload.get("heatmap"):
        #     fig = render_heatmap(payload["heatmap"])
        #     st.plotly_chart(fig, use_container_width=True)
        #
        # if payload.get("path"):
        #     fig = add_route(fig, payload["path"])
        #     st.plotly_chart(fig, use_container_width=True)

with col2:
    render_chat(height=400)