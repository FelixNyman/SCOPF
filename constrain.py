import numpy as np
def constrain_real_power(val, min, max):
	"""contstrains values within rectangular limits in complex plane"""
	val += np.where(val.real > max.real, -val.real + max.real, 0)
	val += np.where(val.real < min.real, -val.real + min.real, 0)
	
	#val += np.where(val.imag > max.imag, -val.imag + max.imag, 0)*1j
	#val += np.where(val.imag < min.imag, -val.imag + min.imag, 0)*1j
	return val

def axis_sum(val, sum, axis):
	"""Ensures that np.sum(val, axis) retuns only elemts with value 'sum'."""
	return val / np.sum(val, axis) * sum