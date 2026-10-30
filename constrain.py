import numpy as np
def constrain_real_power(val, min, max):
	"""Takes three real valued tensors of identical arbritary size"""
	val += np.where(val > max, -val + max, 0)
	val += np.where(val < min, -val + min, 0)
	return val
