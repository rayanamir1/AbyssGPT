import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Any

# Path to the data folder: project_root/data
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_csv(name: str) -> pd.DataFrame:
    """
    Load a CSV from the data directory by filename.
    """
    path = DATA_DIR / name
    return pd.read_csv(path)


def load_all_data() -> dict:
    """
    Load all Abyssal World CSVs into a dict of DataFrames.
    Keys:
        cells, currents, hazards, corals, resources, life, poi, food_web, metadata
    """
    data = {}
    data["cells"] = load_csv("cells.csv")
    data["currents"] = load_csv("currents.csv")
    data["hazards"] = load_csv("hazards.csv")
    data["corals"] = load_csv("corals.csv")
    data["resources"] = load_csv("resources.csv")
    data["life"] = load_csv("life.csv")
    data["poi"] = load_csv("poi.csv")
    data["food_web"] = load_csv("food_web.csv")

    # Load metadata.json safely INSIDE the function
    metadata_path = DATA_DIR / "metadata.json"
    if metadata_path.exists():
        try:
            import json
            with open(metadata_path, "r") as f:
                data["metadata"] = json.load(f)
        except Exception:
            data["metadata"] = None
    else:
        data["metadata"] = None

    return data


def build_cell_index(cells_df: pd.DataFrame) -> Dict[Tuple[int, int], Dict[str, Any]]:
    """
    Build a lookup dict keyed by (row, col) -> dict of cell attributes.
    Makes it easy to quickly get info about any cell.
    """
    # Need to make sure row and col are int
    cells_df = cells_df.copy()
    cells_df["row"] = cells_df["row"].astype(int)
    cells_df["col"] = cells_df["col"].astype(int)

    index = {}
    for _, row in cells_df.iterrows():
        key = (int(row["row"]), int(row["col"]))
        # convert row to a normal dict of scalar values
        index[key] = row.to_dict()
    return index


class AbyssData:
    """
    Simple container for all dataset tables + convenience lookups.
    """

    def __init__(self):
        self.tables = load_all_data()

        self.cells = self.tables["cells"]
        self.currents = self.tables["currents"]
        self.hazards = self.tables["hazards"]
        self.corals = self.tables["corals"]
        self.resources = self.tables["resources"]
        self.life = self.tables["life"]
        self.poi = self.tables["poi"]
        self.food_web = self.tables["food_web"]
        self.metadata = self.tables["metadata"]

        # Lookup the core cell
        self.cell_index = build_cell_index(self.cells)

        # Need to prebuild hazard, coral, resource lookups keyed by (row, col)
        self.hazard_index = self._build_simple_index(self.hazards)
        self.coral_index = self._build_simple_index(self.corals)
        self.resource_index = self._build_simple_index(self.resources)
        self.life_index = self._build_simple_index(self.life)
        self.poi_index = self._build_simple_index(self.poi)

        # Currents index
        self.hazard_index = self._build_simple_index(self.hazards)
        self.coral_index = self._build_simple_index(self.corals)
        self.resource_index = self._build_simple_index(self.resources)
        self.life_index = self._build_simple_index(self.life)
        self.poi_index = self._build_simple_index(self.poi)

        self.currents_index = self._build_simple_index(self.currents)



    @staticmethod
    def _build_simple_index(df: pd.DataFrame) -> Dict[Tuple[int, int], list]:
        """
        Build index: (row, col) -> list of dicts for that cell.
        Some tables have multiple rows per cell (e.g., life, poi).
        """
        index: Dict[Tuple[int, int], list] = {}
        if "row" not in df.columns or "col" not in df.columns:
            return index

        for _, r in df.iterrows():
            key = (int(r["row"]), int(r["col"]))
            index.setdefault(key, []).append(r.to_dict())
        return index

    def get_cell(self, row: int, col: int) -> Dict[str, Any] | None:
        return self.cell_index.get((row, col))

    def get_hazards(self, row: int, col: int):
        return self.hazard_index.get((row, col), [])

    def get_corals(self, row: int, col: int):
        return self.coral_index.get((row, col), [])

    def get_resources(self, row: int, col: int):
        return self.resource_index.get((row, col), [])

    def get_life(self, row: int, col: int):
        return self.life_index.get((row, col), [])

    def get_poi(self, row: int, col: int):
        return self.poi_index.get((row, col), [])
    
    def get_currents(self, row: int, col: int):
        return self.currents_index.get((row, col), [])

if __name__ == "__main__":
    data = AbyssData()
    print(data.cells.head())
    print(data.get_cell(0, 0))