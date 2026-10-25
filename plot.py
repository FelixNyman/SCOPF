import numpy as np
import matplotlib.pyplot as plt
import time

class Plot:
	def __init__(self):
		plt.ion()
		nan, self.figure = plt.subplots()
		self.limit = 1.5
		self.hertz = 5
		self.color_wheel = ['b','g','r','c','m','y','k','w']

	def refresh(self):
		plt.pause(self.hertz ** (-1))
		self.figure.clear()
		if self.limit != 0:
			self.figure.set_xlim([-self.limit, self.limit])
			self.figure.set_ylim([-self.limit, self.limit])
			self.figure.set_aspect('equal')

	def update_values(self, x, style):
		for i in range(0, len(x)):
			self.figure.plot(np.real(x[i]), np.imag(x[i]), style)
		plt.draw()

	def draw_bounds(self, low, up, style):
		for i in range(0, len(low)):
			self.figure.plot([np.real(low[i]), np.real(up[i]), np.real(up[i]), np.real(low[i]), np.real(low[i])],
			                 [np.imag(low[i]), np.imag(low[i]), np.imag(up[i]), np.imag(up[i]), np.imag(low[i])], self.color_wheel[i]+style)
		plt.draw()