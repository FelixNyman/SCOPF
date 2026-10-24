from read_json import read_json
from pathlib import Path
import numpy as np

#network = read_json(Path(__file__).parent / "example_grid.json")
network = read_json(Path(__file__).parent / "case_study_sw_Norway_8bus.json")
#G_min, G, G_max = network.G_non_slack()


print(network.CCY)
print(network.CSY)
print(network.GS_max)
print(network.GS0)
print(np.linalg.det(network.matrix()))
# Idea coppy solution as inital guess fro partial derivateion. in OPF


