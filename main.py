from read_json import read_json
from Network import Network
from pathlib import Path
import numpy as np

#grid = read_json(Path(__file__).parent / "example_grid.json")
grid = read_json(Path(__file__).parent / "case_study_sw_Norway_8bus.json")

network = Network(grid)

network.Y = grid.admittance_matrix(network.CA)
network.impedence_matrix()
for i in range(10):
	network.BS = grid.GS_to_BS()
	network.voltage()
	network.BV = grid.correct_voltage(network.BV, network.CA)
	network.power()
	grid.BS_to_GS(network.BS)
	grid.GS_lim()
	grid.step_GS()
	print(np.round(np.angle(network.BV),2))