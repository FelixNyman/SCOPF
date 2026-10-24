import numpy as np

# Consider a network with n buses. 
# All variables starting with a capital letter are of size
# n or n x n and represent properties of the buses
#
# Consider the network to have m lines

class Network:
	def __init__(self, file):
		# [n x n] admittance and inpedance matricies
		self.Y = 0
		self.Z = 0

		# plot the solver while solving
		self.show = True

		# bus ids
		self.Ids = [2,0,1]

		# floating voltage and power at the buses
		self.V = 0 #np.ones(3,dtype=complex)
		self.S = 0 #np.zeros(3,dtype=complex)

		# minus and plus limits for power and voltage magnitude
		self.S_m = [-1-1j, -0.5-0.5j, 0.5+0.5j]
		self.S_p = [+1+1j, -0.5-0.5j, 0.5+0.5j]	
		self.V_m = [1, 0.5, 0.5] 
		self.V_p = [1, 1.5, 1.5] 

		# line topology, properies and limitations in per units
		self.l_start_index = np.array([0,2])
		self.l_end_index = np.array([1,2])
		self.l_y_series = np.array([0.1j,-0.2j])
		self.l_y_charging = np.array([0.02j, 0.01j])
		self.l_voltage = []
		self.l_max_voltage = []

		# transformer topology, propertis and limitations in per units
		self.t_start_index = []
		self.t_end_index = []
		self.t_tap_ratio = []
		self.t_y_series = []

		# shunt topology and property.
		self.s_index = []
		self.s_y = []

		# construct the network from the file
		self.buses_from_file(file)
		self.lines_from_file(file)
		self.trafos_from_file(file)
		self.shunts_from_file(file)
		self.matrices()

	def buses_from_file(self, file):
		# add all buses with there id's, voltage limits and net aperant power limits
		#for bus in file:
		if False:
			# Psuedo code
			self.Ids.append(bus["id"])
			self.V_m.append(bus["v_min"])
			self.V_p.append(bus["v_max"])
			S_m, S_p = 0
			for gen in file:
				if gen["id"] == bus["id"]:
					S_m += gen["p_min"] + 1j*gen["q_min"]
					S_p += gen["p_max"] + 1j*gen["q_max"]
			for load in file:
				if load["id"] == bus["id"]:
					S_m += load["p"] + 1j*load["q"]
					S_p += load["p"] + 1j*load["q"]
			self.S_m.append(S_m)
			self.S_p.append(S_p)

		# convert the lists to numpy arrays
		self.Ids = np.array(self.Ids)
		self.S_m = np.array(self.S_m)
		self.S_p = np.array(self.S_p)
		self.V_m = np.array(self.V_m)
		self.V_p = np.array(self.V_p)

		# define the size of the variable arrays
		self.V = np.ones(len(self.Ids),dtype=complex)
		self.S = np.zeros(len(self.Ids),dtype=complex)


	def lines_from_file(self, file):
		#for line in file:
		if False:
			start_index = self.bus_index_from_id(line["from_bus"])
			end_index = self.bus_index_from_id(line["to_bus"])
			# continue only if the connected buses actually exists
			if start_index > -1 and end_index > -1:
				self.l_start_index.append(start_index)
				self.l_end_index.append(end_index)


	def trafos_from_file(self, file):
		g=0


	def shunts_from_file(self, file):
		g=0
		

	# return the internal index whos bus has the wanted id, else return -1 
	def bus_index_from_id(self, id):
		return np.sum(np.where(self.Ids == id, range(1, len(self.Ids) + 1), 0)) - 1


	# build the admittance and inpedance matricies after the file has be read and converted to per units
	def matrices(self):
		self.Y = np.zeros([len(self.Ids), len(self.Ids)], dtype=complex)
		for line in range(0, len(self.l_start_index)):
			# ad elimental admittance matrix for piline model 
			self.Y[self.l_start_index[line], self.l_start_index[line]] += self.l_y_series[line] + self.l_y_charging[line] / 2
			self.Y[self.l_start_index[line], self.l_end_index[line]] +=  -self.l_y_series[line]
			self.Y[self.l_end_index[line], self.l_start_index[line]] +=  -self.l_y_series[line]
			self.Y[self.l_end_index[line], self.l_end_index[line]] +=     self.l_y_series[line] + self.l_y_charging[line] / 2
		for trafo in range(0, len(self.t_start_index)):
			# ad elimental admittance matrix for complex tap ratio transformer
			self.Y[self.t_start_index[trafo], self.t_start_index[trafo]] += self.t_y_series[trafo] / (np.abs(self.t_tap_ratio[trafo]) ** 2)
			self.Y[self.t_start_index[trafo], self.t_end_index[trafo]] +=  -self.t_y_series[trafo] / np.conjugate(self.t_tap_ratio[trafo])
			self.Y[self.t_end_index[trafo], self.t_start_index[trafo]] +=  -self.t_y_series[trafo] / self.t_tap_ratio[trafo]
			self.Y[self.t_end_index[trafo], self.t_end_index[trafo]] +=     self.t_y_series[trafo]
		for shunt in range(0, len(self.s_index)):
			# ad admittance at shunted bus
			self.Y[self.s_index[shunt], self.s_index[shunt]] += self.s_y[shunt]
		
		# calculate the impedance matrix
		self.Z = np.linalg.inv(self.Y)


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
		