import numpy as np

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
		self.GS0 = 0    # [1, 1, g]  generator initial power guess
		self.GS_max = 0 # [1, 1, g]  generator max power limit 
		self.GS_min = 0 # [1, 1, g]  generator min power limit
		self.G_sla = 0  # [1, 1, 1]  generator that picks up the slack

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
		