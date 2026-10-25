from read_json import read_json
from pathlib import Path
import numpy as np

#grid = read_json(Path(__file__).parent / "example_grid.json")
grid = read_json(Path(__file__).parent / "case_study_sw_Norway_8bus.json")

print(grid.GS)
grid.BS_to_GS(grid.GS_to_BS())
print(grid.GS)

# Idea coppy solution as inital guess fro partial derivateion. in OPF


