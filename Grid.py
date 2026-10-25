import numpy as np
from constrain import constrain_real_power, axis_sum
# Consider a network with n buses. 
# All variables starting with a capital letter are of size
# n or n x n and represent properties of the buses
#
# Consider the network to have m lines

class Grid:
	"""
	Bus       specific variables start with  B  and have a dim with zise  b.
	Generator specific variables start with  G  and have a dim with zise  g.
	Line      specific variables start with  L  and have a dim with zise  l.
	"""
	def __init__(self):
		# ______B SIZE__________
		self.b = 0     # [1, 1, 1]  bus count

		# constants:
		self.BLS = 0   # [n, 1, 1]  bus load power
		self.BIds = [] # [n, 1, 1]  bus id's, diffent from indecies
		self.B_sla = 0 # [1, 1, 1]  bus, internal index slack-bus


		#_______G SIZE__________
		self.g = 0     # [1, 1, 1]  generator count

		# constant: 
		self.GTM = 0    # [n, 1, g]  generator topology map
		self.GRTM = 0   # [n, 1, g]  generator reverse topology map
		self.GS_max = 0 # [1, 1, g]  generator max power limit 
		self.GS_min = 0 # [1, 1, g]  generator min power limit
		self.GCC = 0    # [3, 1, g]  generator cost coefficients 2:nd order

		# floats
		self.GS = 0     # [1, 1, g]  generator power
		
		#_______C SIZE___________
		self.c = 0      # [1, 1, 1]  component count

		# constants: 
		self.CTM = 0    # [n, 1, c]  component topology map
		self.CSY = 0    # [1, 1, c]  component series admittance
		self.CCY = 0    # [1, 1, c]  component charging admittance
		self.CTR = 0    # [1, 1, c]  component tap ratio
		self.CDV_lim = 0# [1, 1, c]  component delta voltage limit


	def matrix(self, A):
		"""Contracts elimatal admittance matricies with component activation vector to obtain admittance matrix"""
		chargeless = np.sum((self.CTM[:, None, :] * np.conjugate(self.CTM[None, :, :])) * self.CSY[None, None, :] * A[None, None, :], 2)
		return chargeless + np.diag(np.sum(np.where(self.CTM != 0, 1/2, 0) * self.CCY[None, :] *A[None, None, :], 1))


	def update_tap_ratios(self, a):
		"""Changes how the matrix is built. You still need to rebuld the matrix with
		your component activation vector."""
		self.CTM = np.where(self.CTM.real > 0, 1 / a, self.CTM)

	def BIds_to_BIdx(self, id):
		"""Return the internal index whos bus has the wanted id, else return -1.""" 
		return np.sum(np.where(self.BIds == id, range(1, self.b + 1), 0)) - 1

	def step_GS(self):
		"""Performes a gradient decent step while maintaning the sum of generation and respecting there real power limits."""
		# assume real powers have already been constrained
		delta = 10
		# create a matrix of vectors with alterations to the real power of individual generators
		Delta = self.GS.real[:, None] + delta * np.diag(np.ones(self.g))
		#Delta = self.GS.real[:, None] + delta * (2*np.random.rand(self.g**2).reshape([self.g, self.g]) - 1)
		# correct powers to be within limits
		Delta = constrain_real_power(Delta, self.GS_min.real[:, None], self.GS_max.real[:, None])
		# ensure total real power is maintaned through normalization 
		Delta = axis_sum(Delta, np.sum(self.GS.real), 0)
		# numerically approximate the cost cahnge of the different alterations
		nabla = ( self.cost(Delta) - self.cost(self.GS.real[:, None]))

		best_state = np.sum(np.where(nabla == np.min(nabla), range(self.g), -1))

		if nabla[best_state] < 0:
			self.GS += -self.GS.real + Delta[:, best_state].real


	def cost(self, val):
		"""Returns vector of costs from matrix of generator states."""
		return np.sum(self.GCC[0, :, None] + self.GCC[1, :, None] * val + self.GCC[2, :, None] * val**2, 0)

	def constrain_power(self):
		"""contstrains aparent generator power within rectangular limits"""
		self.GS += np.where(self.GS.real > self.GS_max.real, -self.GS.real + self.GS_max.real, 0)
		self.GS += np.where(self.GS.real < self.GS_min.real, -self.GS.real + self.GS_min.real, 0)
		
		self.GS += np.where(self.GS.imag > self.GS_max.imag, -self.GS.imag + self.GS_max.imag, 0)*1j
		self.GS += np.where(self.GS.imag < self.GS_min.imag, -self.GS.imag + self.GS_min.imag, 0)*1j

	
	# constrain voltage magnitude to lie within radial limits
	def constrain_voltage(self):
		self.V = np.where(np.abs(self.V) < np.real(self.V_m), self.V * np.real(self.V_m) / np.abs(self.V), self.V)
		self.V = np.where(np.abs(self.V) > np.real(self.V_p), self.V * np.real(self.V_p) / np.abs(self.V), self.V)
		