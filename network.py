import numpy as np

# Consider a network with n buses. 
# All variables starting with a capital letter are of size
# n or n x n and represent properties of the buses
#
# Consider the network to have m lines

class Network:
	def __init__(self, grid):
		# ______B SIZE__________
		self.b = grid.b     # [1, 1, 1]  bus count

		# constats:
		self.Y = 0     # [b, b, 1]  bus admittance matrix
		self.Z = 0     # [b, b, 1]  bus impedance matrix

		# floats:
		self.BV = np.ones(grid.b, dtype=complex)   # [n, 1, 1]  bus voltage
		self.BS = np.zeros(grid.b, dtype=complex)  # [n, 1, 1]  bus power

		#_______C SIZE___________
		self.c = grid.c                            # [1, 1, 1]  component count

		# floats:
		self.CA = np.ones(grid.c, dtype=complex)   # [1, 1, c]  component activation
		self.CTR = grid.CTR                        # [1, 1, c]  component tap ratio
		self.CC = -1                               # [1, 1, 1]  component contingency

	def impedence_matrix(self):
		"""Inverts the admittance matrix of the network."""
		self.Z = np.linalg.inv(self.Y)

	def voltage(self):
		"""Iterate bus voltage""" 
		self.BV = self.Z @ np.conjugate(self.BS / self.BV)		
	def power(self):
		"""Calculate bus power.""" 
		self.BS = self.BV * np.conjugate(self.Y @ self.BV)