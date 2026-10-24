import numpy as np

# Consider a network with n buses. 
# All variables starting with a capital letter are of size
# n or n x n and represent properties of the buses
#
# Consider the network to have m lines

class Network:
	def __init__(self):
		# ______B SIZE__________
		self.b = 0     # [1, 1, 1]  bus count

		# constats:
		self.Y = 0     # [b, b, 1]  bus admittance matrix
		self.Z = 0     # [b, b, 1]  bus impedance matrix

		# floats:
		self.BV = 0    # [n, 1, 1]  bus voltage
		self.BS = 0    # [n, 1, 1]  bus power

		#_______G SIZE__________
		self.g = 0     # [1, 1, 1]  generator count

		# floats:
		self.GS = 0    # [1, 1, g]  generator power

		#_______C SIZE___________
		self.c = 0     # [1, 1, 1]  component count

		# floats:
		self.CA = 0    # [1, 1, c]  component activation
		self.CTR = 0   # [1, 1, c]  component tap ratio
		self.CBC = []  # [       ]  component, network contingency


	# contstrains aparent power within rectangular limits
	def constrain_power(self):
		self.S = np.where(np.real(self.S) > np.real(self.S_p), np.real(self.S_p) + 1j*np.imag(self.S), self.S)
		self.S = np.where(np.real(self.S) < np.real(self.S_m), np.real(self.S_m) + 1j*np.imag(self.S), self.S)
	
		self.S = np.where(np.imag(self.S) > np.imag(self.S_p), np.real(self.S) + 1j*np.imag(self.S_p), self.S)
		self.S = np.where(np.imag(self.S) < np.imag(self.S_m), np.real(self.S) + 1j*np.imag(self.S_m), self.S)

	
	# constrain voltage magnitude to lie within radial limits
	def constrain_voltage(self):
		self.V = np.where(np.abs(self.V) < np.real(self.V_m), self.V * np.real(self.V_m) / np.abs(self.V), self.V)
		self.V = np.where(np.abs(self.V) > np.real(self.V_p), self.V * np.real(self.V_p) / np.abs(self.V), self.V)
		