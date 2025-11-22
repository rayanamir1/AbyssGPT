# 🌊 AbyssGPT  
### Deep-Sea Intelligence Assistant for Mapping, Risk Analysis & Resource Planning

AbyssGPT is an interactive marine-intelligence system that analyzes deep-sea data layers such as hazards, biodiversity, corals, resources, currents, and seafloor topography.  
It supports natural-language queries, generates risk assessments, highlights resource-rich mining zones, and visualizes results on a dynamic map.

Built with **Python, Streamlit, NumPy, Plotly**, and a full custom backend logic engine.

---

## Features

### Natural-Language Query Engine**
Ask AbyssGPT things like:
- “Explain (10, 15)”
- “Find safe route from (2,3) to (10,15)”
- “Where are the best mining zones with low coral impact?”
- “Show biodiversity at (4,9)”
- “POI at (3,7)”

Our custom intent-classifier (no LLM dependency) routes each query to:
- Hazard analysis  
- Biodiversity / species lookup  
- Mining score analysis  
- Conservation heatmaps  
- Route-finding  
- Region explanations  

---

## Data Layers Used**
Stored in `/data/*.csv`:

| Layer        | Includes |
|--------------|----------|
| `cells.csv`  | Depth, temperature, biome |
| `currents.csv` | Speed, stability |
| `hazards.csv` | Vents, trenches, volcanism, severity |
| `corals.csv` | Health, cover %, biodiversity index |
| `resources.csv` | Abundance, value, impact |
| `life.csv` | Species, density, threat level |
| `poi.csv` | Landmarks & seafloor features |

Every query fetches data from these layers and builds a structured explanation.

---

## Map Visualization**
Uses Plotly to show:
- Depth map (default)
- Heatmaps for mining or conservation queries
- Route overlays
- Highlighted coordinates

---

## Backend Logic Overview**

### Scoring Engine (`logic/scoring.py`)
- **Danger Score** — depth, hazards, currents  
- **Resource Score** — abundance, value, purity  
- **Ecological Impact Score** — corals, life, environmental impact  
- **Combined Score** — weighted based on query:
  - Mining  
  - Conservation  
  - Safe-route navigation  
  - Balanced  

### Pathfinding (`logic/pathfinding.py`)
Uses a Dijkstra-style graph search to compute least-risk routes.

### Explanation Generator (`logic/explain.py`)
Turns raw numeric data into human-readable descriptions.

---

## Chat Interface**

Built using Streamlit native chat components:
- Clean chat bubbles
- Demo query shortcuts
- Stable input cycle with no duplicate messages
- Structured responses (answer + data source + important stats)

---

## Project Structure

AbyssGPT/
│── app.py # Main Streamlit app
│── ui/
│ ├── chat.py # Chat interface
│ └── map.py # Plotly visualization
│── logic/
│ ├── core.py # Query router + intent logic
│ ├── explain.py # Natural language output
│ ├── pathfinding.py # Navigation engine
│ ├── scoring.py # Risk & resource model
│ ├── data_loader.py # CSV loading & indexing
│ └── intent.py # Natural-language intent parser
│── data/ # All marine datasets
│── README.md
│── requirements.txt

---

## ▶️ **How to Run**

### 1. Install dependencies:
```bash
pip install -r requirements.txt

streamlit run app.py

http://localhost:8501

```

## Example Prompts 

- Explain (10, 15)
- What are the hazards at (4,9)
- Give biodiversity at (18, 11)
- poi at (2,0)
- Safe route from (1,1) to (15,20)
- Show best mining zones
- Conservation hotspots

---

## Team and Roles
- Dilraj Deogan — Backend logic, scoring engine, data loader, core architecture, QA
- Rayan Amir - Backend logic, pathfinding engine, core architecture
- Dhruv Ghai - Frontend, Chatbot UI, explain and core backend logic
- Arsh Mobeen - Frontend, mapping system, and core backend logic

---

## Tech Stack
- Python
- Streamlit
- Numpy
- Pandas
- Plotly
- NetworkX

---

## Future Improvements

- Integrate real LLM (DeepSeek, GPT, Claude, etc.)
- Add uncertainty modeling
- Expand dataset with geological layers
- Multi-hop reasoning across cells
- Predictive modeling for climate + ocean drift

--- 

