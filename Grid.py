import numpy as np
from constrain import constrain_real_power
import time
from plot import Plot
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
		self.b = 0      # [1, 1, 1]  bus count

		# constants:
		self.BLS = 0    # [n, 1, 1]  bus load power
		self.BV_max = 0 # [n, 1, 1]  bus max voltage
		self.BV_min = 0 # [n, 1, 1]  bus min voltage
		self.BIds = []  # [n, 1, 1]  bus id's, diffent from indecies
		#self.B_sla = 0  # [1, 1, 1]  bus, internal index slack-bus


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


	def GS_to_BS(self):
		"""Maps generator power to bus power. Also defines revese map for non injectve map."""
		R = self.GTM * self.GS.real[None, :]
		R = R / np.where(R != 0 , np.sum(R, 1)[:, None], 1)
		I = self.GTM * (self.GS.imag[None, :] + 0.1) # +0.1 avoids discriminating a generator at zero reactive power when remaping
		I = I / np.where(I != 0 , np.sum(I, 1)[:, None], 1)
		self.GRTM = R + 1j*I
		return np.sum(self.GTM * self.GS[None, :], 1) + self.BLS
	
	def BS_to_GS(self, BS):
		"""Maps bus power to generator power. May be ambigous for multible generators on the same bus,
		then proportions are maintaned individually for real and reactive power."""
		BGS = BS - self.BLS
		self.GS = np.sum(self.GRTM.real * BGS.real[:, None] + 1j*self.GRTM.imag * BGS.imag[:, None], 0)
		
	def admittance_matrix(self, A):
		"""Contracts elimatal admittance matricies with component activation vector to obtain admittance matrix"""
		chargeless = np.sum((self.CTM[:, None, :] * np.conjugate(self.CTM[None, :, :])) * self.CSY[None, None, :] * A[None, None, :], 2)
		return chargeless + np.diag(np.sum(np.where(self.CTM != 0, 1/2, 0) * self.CCY[None, :] * A[None, :], 1))


	def update_tap_ratios(self, a):
		"""Changes how the matrix is built. You still need to rebuld the matrix with
		your component activation vector."""
		self.CTM = np.where(self.CTM.real > 0, 1 / a, self.CTM)

	def BIds_to_BIdx(self, id):
		"""Return the internal index whos bus has the wanted id, else return -1.""" 
		return np.sum(np.where(self.BIds == id, range(1, self.b + 1), 0)) - 1

	def step_GS(self):
		"""Performes a gradient decent step while maintaning the sum of generation and respecting there real power limits."""
		new, old, one_norm = self.GS.real, 0, np.sum(self.GS.real)

		# unconstrained, analytic gradient decent of cost funtion
		new -= 0.001*(self.GCC[1, :] + 2*self.GCC[2, :] * self.GS.real)

		# contradicting constrains requier iteration to stabelize
		while np.max(np.abs(new - old)) > 0.001:
			old = new
			new = new * one_norm / np.sum(new) # projection onto g-1 space
			new = constrain_real_power(new, self.GS_min.real, self.GS_max.real) # box constrain in g space

		self.GS += -self.GS.real + new

	def cost(self):
		"""Returns the of costs of a generation state."""
		return np.sum(self.GCC[0, :] + self.GCC[1, :] * self.GS.real + self.GCC[2, :] * self.GS.real**2, 0)

	def GS_lim(self):
		"""contstrains aparent generator power within rectangular phasor space limits"""
		self.GS += np.where(self.GS.real > self.GS_max.real, -self.GS.real + self.GS_max.real, 0)
		self.GS += np.where(self.GS.real < self.GS_min.real, -self.GS.real + self.GS_min.real, 0)
		
		self.GS += np.where(self.GS.imag > self.GS_max.imag, -self.GS.imag + self.GS_max.imag, 0)*1j
		self.GS += np.where(self.GS.imag < self.GS_min.imag, -self.GS.imag + self.GS_min.imag, 0)*1j

	
	def correct_voltage(self, V, A):
		"""Ensure bus voltage phasors respect ratings of connecting components, and drift towards 1 per unit voltaeg magnitude."""
		# constrain voltage magnitude to lie within radial limits
		V = np.where(np.abs(V) > self.BV_max, V * np.abs(self.BV_max) / np.abs(V), V)
		V = np.where(np.abs(V) < self.BV_min, V * np.abs(self.BV_min) / np.abs(V), V)

		# contradicting constrains requier iteration to stabelize
		V_old = 0
		while np.max(np.abs(V - V_old)) > 0.001:
			V_old = V
			# get component delta voltage
			CDV = np.sum(self.CTM * V[:, None], 0)
			# get difference phasor between component delta voltage and its limit
			CDDV = CDV / np.abs(CDV) * (self.CDV_lim - np.abs(CDV)) / 2 # unit vector times distance differance
			# only consider violated limits
			CDDV = np.where(np.abs(CDV) > self.CDV_lim, CDDV, 0)
			# remove differance phasor from buses for active components
			V += np.sum(self.CTM * CDDV[None, :] * A[None, :] , 1)

		# rotate all phasors so average angle is zero
		V *= np.exp(-1j*np.average(np.angle(V)))

		# favour the voltage magnitude to be one
		w = 0.001
		V *= (w*np.abs(V) + 1) / (w + 1) / np.abs(V)

		return V