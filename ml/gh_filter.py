import numpy as np
import matplotlib.pyplot as plt
from signal_generator import Signal

class GH:

	def __init__(self,initial_guess=None,est_scale=0.5,pred_scale=0.5,learn_method=None):
		self.data = []
		self.estimated = [] #keep track of estimations
		self.predicted = [] #keep track of predictions
		self.dt = 1
		self.est_scale = est_scale #g  - velocity?, deviation ! :variance-est/ var-measurement
		self.pred_scale = pred_scale #h  - cov
		self.delta_pred = [1] #initial guess
		self.learn_method = learn_method

		start = initial_guess if initial_guess else 0
		self.predicted.append(start)

	@property
	def last_pred(self): return self.predicted[-1]
	@property
	def last_est(self): return self.estimated[-1]
	@property
	def last_delta_pred(self): return self.delta_pred[-1]

	#calculate the diff between the incoming data/measurement and the last prediction/control-change
	def residual(self, data): return data - self.last_pred

	def call_method(self, action, method=None, args=None):
		if method == None : method_attr = action
		else: method_attr = action + '_' + method
		pick_method = getattr(self, method_attr)
		if args : return pick_method(args)
		return pick_method()

	#one train <=> predict cycle
	def learn(self, data, method=None):
		self.data.append(data)
		est = self.call_method( action='train', method=method, args=data)
		pred = self.call_method( action='predict', method=method)
		return est, pred

	def batch_learn(self, method='None', lst):
		for d in lst : self.learn(d,method)


#=== STEP1 : BASIC train, predict methods ========================================

	def predict_basic(self):
		self.predicted.append(self.last_est)
		return self.last_pred

	def train_basic(self,data):
		est = self.last_pred + self.est_scale * self.residual(data)
		self.estimated.append(est)
		return est

#=== STEP2 : BASIC train, predict also changes in the direction of the "incoming-data" =====

	def predict_delta(self):
		pred = self.last_est + self.last_delta_pred
		self.predicted.append(self.last_est)
		return self.last_pred

	def train_delta(self,data):
		delta = self.last_delta_pred + self.pred_scale * self.residual(data)
		self.delta_pred.append(delta)
		est = self.last_pred + self.est_scale * self.residual(data)
		self.estimated.append(est)
		return est

#=== DEFAULT train, predict methods ========================================

	def predict(self):
		pred = self.last_est + self.last_delta_pred * self.dt
		self.predicted.append(pred)
		return pred

	def train(self, data):
		delta = self.last_delta_pred + self.pred_scale * (self.residual(data) / self.dt)
		self.delta_pred.append(delta)
		est = self.last_pred + self.est_scale * self.residual(data)
		self.estimated.append(est)
		return est



def test(ticks=1000,v=0.5,a=0.5):

	sg = Signal(cfg=Signal.cfg)
	gh = GH(0,v,a)

	sig = sg.signal()

	for t in xrange(0,ticks):
		data = sig.next()
		gh.learn(data)

	return gh

def plotit(gh):
	x = range(1,len(gh.data)+1)
	plt.plot(x,gh.data,label='data',color='green')
	plt.plot(x,gh.predicted[:-1],label='predicted',color='red')
	plt.plot(x,gh.estimated, label='est',color='blue',linewidth=2)
	plt.tight_layout()
