import pandas as pd

# Load each csv file
hazards = pd.read_csv("data/hazards.csv")
cells = pd.read_csv("data/cells.csv")
corals = pd.read_csv("data/corals.csv")
currents = pd.read_csv("data/currents.csv")
food_web = pd.read_csv("data/food_web.csv")
life = pd.read_csv("data/life.csv")
poi = pd.read_csv("data/poi.csv")
resources = pd.read_csv("data/resources.csv")

