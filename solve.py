import numpy as np
import time
from plot import Plot


def solve(network):	
	# plot the solver while it runs
	if network.show:
		window = Plot()
		window.hertz = 5
		window.limit = 4

	# iterate untill the bus voltages are recoverd between iterations
	TOLORANCE = 0.001
	V_old = np.zeros(len(network.V), dtype = complex)
	while np.max(np.abs(network.V - V_old)) > TOLORANCE:
		V_old = network.V

		# plot the frame
		if network.show:
			window.refresh()
			window.draw_bounds(network.S_m, network.S_p,'--')
			window.update_values(network.S,'o')
			window.update_values(network.V,'*')

		# compute and constrain a new power guess 
		network.S = network.V * (network.Y @ network.V)
		network.constrain_power()

		# compute and constrain a new voltage guess 
		network.V = network.Z @ np.conjugate(network.S / network.V)
		network.constrain_voltage()

	# show the solution for a while
	if network.show:
		time.sleep(10)