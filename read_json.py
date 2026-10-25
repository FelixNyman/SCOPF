import json
import numpy as np
from Grid import Grid

def read_json(file_path):
	"""Build a grid from a .json file path."""

	# load the grid from the file_path
	with open(file_path, "r", encoding = "utf-8") as fh:
		file = json.load(fh)
	grid      = Grid()
	P_base   = file["base"]["s_base_mva"]




	# ______BUS HANDELING_______
	
	# add all buses with there id's
	for bus in file["bus"]:
		if bus["in_service"]:
			grid.BIds.append(bus["id"])
			if bus["type"] == 'SLACK':
				grid.B_sla = grid.b
			grid.b += 1
			# ADD MORE CODE HERE

	# convert the list to numpy array
	grid.BIds = np.array(grid.BIds) # [n, 1, 1]
	# define the size of the variable arrays
	grid.BLS   = np.zeros(grid.b, dtype=complex)    # [n, 1, 1]

	# determnie the stady load case
	for load in file["load"]:
		if load ["in_service"]:
			ix_I  = grid.BIds_to_BIdx(load["bus"])
			if ix_I != -1:
				grid.BLS[ix_I] -= (load["p_mw"] + 1j*load["q_mvar"]) * load["scaling"] / P_base
	for shunt in file["shunt"]:
		if load ["in_service"]:
			# count only if the connected buses actually exists
			ix_I  = grid.BIds_to_BIdx(shunt["bus"])
			if ix_I > -1:
				grid.BLS[ix_I] += (load["p_mw"] + 1j*load["q_mvar"]) / P_base

	#______________________________________





	# _______GENERATOR HANDELING___________
	
	# cont the number of generators connected to exsisting buses
	for gen in file["generator"]:
		if grid.BIds_to_BIdx(gen["bus"]) != -1:
			grid.g += 1

	# allocate memory
	grid.GTM   = np.zeros([grid.b, grid.g])                   # [n, 1, g]
	grid.GRTM  = np.zeros([grid.b, grid.g], dtype= complex)   # [n, 1, g]
	grid.GCC   = np.zeros([3, grid.g])                        # [3, 1, g]
	grid.GS_max = np.zeros(grid.g, dtype=complex)             # [1, 1, g]
	grid.GS_min = np.zeros(grid.g, dtype=complex)             # [1, 1, g]
	grid.GS    = np.zeros(grid.g, dtype=complex)              # [1, 1, g]

	g = 0
	for gen in file["generator"]:
		ix = grid.BIds_to_BIdx(gen["bus"])
		if ix != -1:
			# ad the properties of a connected generator
			grid.GTM[ix, g] = 1
			grid.GS_max[g]  = (gen["max_p_mw"] + 1j*gen["max_q_mvar"]) / P_base
			grid.GS_min[g]  = (gen["min_p_mw"] + 1j*gen["min_q_mvar"]) / P_base
			grid.GS[g]      = gen["p_mw"] / P_base
			g += 1

	# guess some resonalbe cost functions
	grid.GCC[0, :]  = grid.GS_max.real                         # all have cost to run based on there size
	grid.GCC[1, :]  = 0.5 + 0.5 * np.random.rand(grid.g)      # all costs are linear between 0.5 and 1 [$ / per unit]
	grid.GCC[2, :]  = -0.01 * np.random.rand(grid.g)           # all are slight quadratic concave

	# _____________________________________




	# ______COMPONENT HANDELING____________

	# first count the number of components
	for line in file["line"]:
		ix_I  = grid.BIds_to_BIdx(line["from_bus"])
		ix_II = grid.BIds_to_BIdx(line["to_bus"])
		# count only if the connected buses actually exists
		if ix_I > -1 and ix_II > -1 and ix_I != ix_II:
			grid.c += 1
	for trafo in file["transformer"]:
		ix_I  = grid.BIds_to_BIdx(trafo["hv_bus"])
		ix_II = grid.BIds_to_BIdx(trafo["lv_bus"])
		# count only if the connected buses actually exists
		if ix_I > -1 and ix_II > -1 and ix_I != ix_II:
			grid.c += 1

	# allocate memory
	grid.CTM     = np.zeros([grid.b, grid.c], dtype=complex)
	grid.CSY     = np.zeros(grid.c, dtype=complex)
	grid.CCY     = np.zeros(grid.c, dtype=complex)
	grid.CTR     = np.ones(grid.c, dtype=complex)
	grid.CDV_lim = np.ones(grid.c)

	c = 0
	for line in file["line"]:
		ix_I  = grid.BIds_to_BIdx(line["from_bus"])
		ix_II = grid.BIds_to_BIdx(line["to_bus"])
		if ix_I > -1 and ix_II > -1 and ix_I != ix_II:
			grid.CTM[ix_I, c]  =  1
			grid.CTM[ix_II, c] = -1

			# get V_base at start bus
			for bus in file["bus"]:
				if bus["id"] == line["from_bus"]:
					V_base = bus["vn_kv"] # [kV]
			
			# get line series and charging admittance
			Y_base = P_base / (V_base ** 2) # [MVA / (kV)^2 = 1/ohm]
			Z_series      = line["length_km"] * (line["r_ohm_per_km"] + 1j*line["x_ohm_per_km"]) / line["parallel"] # [km * ohm / km = ohm]
			Z_charging    = 1 / (1j*100*np.pi * line["length_km"] * line["c_nf_per_km"] * 1e-9 * line["parallel"])
			grid.CSY[c] = 1 / (Z_series * Y_base) # [1 / ( ohm / ohm ) = per unit]
			grid.CCY[c] = 1 / (Z_charging * Y_base) # [1 / ( ohm / ohm ) = per unit]

			# get max line delta voltage
			I_base = P_base / V_base # [MVA / kV = kA]
			I_max  = line["max_i_ka"] #/ np.sqrt(3) # [kA per conductor -> one line equvilent kA] 
			grid.CDV_lim[c] = np.abs((I_max / I_base) / grid.CSY[c]) # [(kA / kA)/ per unit = per unit ]
			c += 1

	for trafo in file["transformer"]:
		ix_I  = grid.BIds_to_BIdx(trafo["hv_bus"])
		ix_II = grid.BIds_to_BIdx(trafo["lv_bus"])
		if ix_I > -1 and ix_II > -1 and ix_I != ix_II:
			grid.CTM[ix_I, c]  =  1
			grid.CTM[ix_II, c] = -1

			# get V_base at high voltage bus
			for bus in file["bus"]:
				if bus["id"] == trafo["hv_bus"]:
					V_base = bus["vn_kv"] # [kV]

			vk_ratio = (trafo["vkr_percent"] + 1j * np.sqrt(trafo["vk_percent"]**2 - trafo["vkr_percent"]**2)) / 100

			grid.CSY[c] = trafo["parallel"] * trafo["sn_mva"] / P_base / vk_ratio 

			grid.CDV_lim[c] = np.sqrt(np.abs(trafo["sn_mva"] / P_base / grid.CSY[c]))

			grid.CTR[c] = (1 + trafo["tap_pos"]*trafo["tap_step_percent"]*0.01) * np.exp(1j*np.deg2rad(trafo["tap_step_degree"]))

			c += 1
	# ________________________________
	
	return grid