import numpy as np
def constrain_real_power(val, min, max):
	"""contstrains values within rectangular limits in complex plane"""
	val += np.where(val > max, -val + max, 0)
	val += np.where(val < min, -val + min, 0)
	return val
