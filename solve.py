import numpy as np
import time
from plot import Plot


def solve(self):	
	# plot the solver while it runs
	if self.show:
		window = Plot()
		window.hertz = 5
		window.limit = 4

	# iterate untill the bus voltages are recoverd between iterations
	TOLORANCE = 0.001
	V_old = np.zeros(len(self.V), dtype = complex)
	while np.max(np.abs(self.V - V_old)) > TOLORANCE:
		V_old = self.V

		# plot the frame
		if self.show:
			window.refresh()
			window.draw_bounds(self.S_m, self.S_p,'--')
			window.update_values(self.S,'o')
			window.update_values(self.V,'*')

		# compute and constrain a new power guess 
		self.S = self.V * np.conjugate(self.Y @ self.V)
		self.constrain_power()

		# compute and constrain a new voltage guess 
		self.V = self.Z @ np.conjugate(self.S / self.V)
		self.constrain_voltage()

	# show the solution for a while
	if self.show:
		time.sleep(10)