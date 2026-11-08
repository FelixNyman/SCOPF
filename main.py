#from read_json import read_json
from read_IEEE_json import read_IEEE_json
from Network import Network
from pathlib import Path
import numpy as np


grid = read_IEEE_json(Path(__file__).parent / "IEEE_9_bus.json")

grid.print_grid_constrains()

network = Network(grid)


network.Y = grid.admittance_matrix(network.CA)
network.impedence_matrix()

for i in range(0):
	print(f"new iteration {i}")
	network.BS = grid.GS_to_BS()
	network.voltage()
	network.BV = grid.correct_voltage(network.BV, network.CA)
	network.power()
	grid.BS_to_GS(network.BS)
	grid.GS_lim()