import numpy as np

class BDF:

	def __init__(self):
		self.dist = np.zeros(10)
		self.dist[0] = 0.1
		#self.dist = np.array([0.1] * 10)

	def normalize(self):
		self.dist /= np.sum(self.dist)

	#sense, LH
	def update(self, map_, z, correct_prob) :
		scale = correct_prob / ( 1 - correct_prob)
		for i, val in enumerate(map_):
			if val == z : self.dist[i] *= scale
		self.normalize()

	def predict(self,offset,kernel):
		N = len(self.dist)
		kN = len(kernel)
		width = int((kN - 1)/2)

		result = np.zeros(N)
		for i in range(N):
			for k in range(kN):
				ix = (i + (width - k) - offset) % N
				result[i] += self.dist[ix] * kernel[k]
		self.dist[:] = result[:]