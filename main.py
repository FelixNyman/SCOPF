from read_json import read_json
from pathlib import Path
import numpy as np

#network = read_json(Path(__file__).parent / "example_grid.json")
grid = read_json(Path(__file__).parent / "case_study_sw_Norway_8bus.json")


V = 1 + -0.5 * np.random.rand(grid.b) -0.5j + 1j*np.random.rand(grid.b)
print(V)
V = grid.correct_voltage(V)
print(V)

# Idea coppy solution as inital guess fro partial derivateion. in OPF


