from read_json import read_json
from pathlib import Path
import numpy as np

#network = read_json(Path(__file__).parent / "example_grid.json")
grid = read_json(Path(__file__).parent / "case_study_sw_Norway_8bus.json")
#G_min, G, G_max = network.G_non_slack()


for i in range(100):
	grid.step_GS()
	print(grid.cost(grid.GS.real[:, None]))
	#print(grid.GS.real)
# Idea coppy solution as inital guess fro partial derivateion. in OPF


