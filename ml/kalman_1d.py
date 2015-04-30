import numpy as np
import matplotlib.pyplot as plt
from signal_generator import Signal

class Kalman1D(object):

# when we have only data i.e. no ctrl(u) we have to set some Q-ctrl-variance
# i.e. predict return the same value

	def __init__(self,x0,P,R,Q):
		self.x = x0 #estimited value, state
		self.P = P #variance of the est state
		self.R = R #measurement error/variance
		self.Q = Q #movement/control error/variance
		self.estimated = []
		self.predicted = [0]
		self.data = []

	#z - data/measurament
	# "mean averaged" and variation shrinked
	def train(self,z):
		self.data.append(z)
		#mean eq
		self.x = (z * self.P + self.x * self.R) / (self.P + self.R)
		#variation eq
		self.P = 1. / (1. / self.P + 1. / self.R )
		self.estimated.append(self.P)

	#movement shift and variance degradation
	def predict(self, u = 0.0):
		self.x += u #shift the mean
		self.P += self.Q #spread variation
		self.predicted.append(self.x)

	def learn(self,data):
		self.train(data)
		self.predict()

	def plot_kalman(self):
		x = range(1,len(self.data)+1)
		plt.plot(x,self.data,label='data',color='green')
		plt.plot(x,self.predicted[:-1],label='predicted',color='red')
		plt.plot(x,self.estimated, label='est',color='blue',linewidth=2)
		plt.tight_layout()


def test_kalman(ticks=1000,x0=0,P=0.5,R=1,Q=0.5):

	sg = Signal(cfg=Signal.cfg)
	k = Kalman1D(x0,P, R, Q)

	sig = sg.signal()

	for t in xrange(0,ticks):
		data = sig.next()
		k.learn(data)

	return k

