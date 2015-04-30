#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import Dumper

#constants
USED = 0 #how many times a pattern was used
ERR = 1 #when used to predict the diff(data,pred)^2 i.e. the error
ARRIVED = 2 #when the pattern was first added to the history
META_NCOLS = 4
CUP = META_NCOLS - 1 #how many times was the entry cleaned up



class TSP():

	def __init__(self,buffer_len=10,history_len=10,prediction_method='top',steps=5):
		self.buffer_len = buffer_len
		self.history_len = history_len
		self.tick = 0 #number of ticks passed

		#used to search for zero row
		self.zero = np.zeros(buffer_len)
		self.zap_m() #desicion matrix
		#holds meta info : used, err
		self.meta = np.zeros((history_len, META_NCOLS))
		self.zero_meta = np.zeros(META_NCOLS - 1) #used for cleaning meta-entries
		self.buffer = np.zeros(buffer_len)

		self.prediction_method = 'predict_' + prediction_method

		self.data = []
		self.predicted = [0]
		self.last_pred_idx = 1
		self.metrics = {}
		#hold multi step predictions as list of np-arrays
		self.mult_pred = [ np.zeros(steps) ] #!fixme

	def zap_m(self): self.m = np.zeros((self.history_len, self.buffer_len))

	@staticmethod
	def autocorr(x, t=1):
		return np.corrcoef(np.array([x[0:len(x)-t], x[t:len(x)]]))

	@staticmethod #!fixme pass by ref
	def fifo_insert(buff,value):
		buff = np.roll(buff,1)
		buff[0] = value

	#based on how much a pattern is used and error calculate a score, less is better
	@staticmethod
	def weight(x,y): #! keep in mind that atan2() expect the coords in reverse order
		return np.arctan2(y,x) #the angle between how many times the pattern was used and the cummulative error

	def find_empty_entry(self): #pick the first one
		return np.where(np.all(self.m == self.zero, axis=1))[0][0]

	def worse_entry_idx(self):
		avg_used = int( np.max(self.meta[:,USED]) ) + 1 #!!fixme or half-the-long-lasting
		#first look for dormant entries, which lived longer than avg lifespan of an entry
		#!!!  zero_idxs = np.where( (self.meta[:,USED] == 0) & (self.meta[:,ERR] == 0) & (self.tick - self.meta[:,ARRIVED] > half_avg_life) )[0]
		zero_idxs = np.where( (self.meta[:,USED] == 0) & (self.tick - self.meta[:,ARRIVED] > avg_used) )[0]
		if len(zero_idxs) > 0:
			#pick the idx of the earliest arrival i.e. the oldest from the zero-used
			idx = zero_idxs[ np.argmin(self.meta[zero_idxs,ARRIVED]) ]
			print "zc> %s" % idx
			return idx


		#otherwise find the less used with highest error rate
		usage  = self.meta[:,USED] / np.sum(self.meta[:,USED]) #high-usage => lower weight-score
		errors = self.meta[:,ERR]  / np.sum(np.sqrt(self.meta[:,ERR])) #high-err => higher weight-score

		#^^^^ !fixme :switch from scaling to z-score

		#biggest score is worse. IF (0,0) i.e. skip it
		idx = np.argmax( TSP.weight(x=usage,y=errors) ) #!!!order important
		print "wc> %s" % idx
		return idx


	def freeup_entry(self):
		#meta = t.meta[ np.nonzero[t.meta[:,0]], : ] #view only non-zero-used entries
		#pick the worse entry, biggest-angle
		idx = self.worse_entry_idx()

		self.m[idx,:] = self.zero #!fixme
		self.meta[idx,0:ARRIVED+1] = self.zero_meta
		self.meta[idx,CUP] += 1

		return idx

	def add_tick(self,value):
		self.tick += 1
#		TSP.fifo_insert(self.buffer, value)

		#handle query buffer
		self.buffer = np.roll(self.buffer,1)
		self.buffer[0] = value

		#!fixme...free up when full
		try:
			ee = self.find_empty_entry()
		except:
			ee = self.freeup_entry()
		print "ee>%s" % ee
		self.m[ee] = self.buffer

		self.meta[ee,ARRIVED] = self.tick

	def batch_ticks(self,queue):
		for val in queue : self.add_tick(val)

	@staticmethod
	def cosine_similarity(vector,matrix):
		#np.arccos(np.dot(a,b)/(np.linalg.norm(a,axis=1) * np.linalg.norm(b,axis=1)))
		sim = ( np.sum(vector*matrix,axis=1) / ( np.sqrt(np.sum(matrix**2,axis=1)) * np.sqrt(np.sum(vector**2)) ) )[::-1]
		return sim

	@staticmethod #calculate Euclidian distance
	def euclidean_distance(vector, matrix):
		dist = np.sqrt(np.sum((vector - matrix)**2,axis=1))
		#dist = np.linalg.norm(vector - matrix, axis=1)
		return dist

	def best_match_idx(self,query):
		q = query[:self.buffer_len-1]
		#!fixme .. skip full zero rows
		#return the indecies of sequences ordered by distance
		inverse_error_weights = 1 + (self.meta[:,ERR] / np.sum(np.sqrt(self.meta[:,ERR])) )
		idx = np.argsort( TSP.euclidean_distance(q, self.m[:,1:]) )# * inverse_error_weights)
		return idx

	def predict_top(self,query):
		idx = self.best_match_idx(query)[0]
		print "best,last>%s : %s" % (idx,self.last_pred_idx)
		self.last_pred_idx = idx
		self.meta[idx,USED] += 1
		return self.m[idx,0]

	def predict_avg(self,query,n=3):
		idx = self.best_match_idx(query)[:n]
		print "best,last>%s : %s" % (idx,self.last_pred_idx)
		self.last_pred_idx = idx
		self.meta[idx,USED] += 1
		return np.average(self.m[idx,0])

	def predict_nsteps(self, query, steps=5):
		rolling_query = query
		preds = np.zeros(steps)
		for s in xrange(0,steps-1):
			#preds[s] = self.m[ self.best_match_idx(query)[0], 0 ] #predict-top
			preds[s] = self.predict_top(rolling_query)
			rolling_query = np.insert(rolling_query,0,preds[s])
		self.mult_pred.append(preds)
		return preds[0]

	def calc_error(self):
		if not len(self.data) : return
		ix = len(self.data) - 1
		err = (self.data[ix] - self.predicted[ix])**2 #!?
		print "lp-idx,err>%s;%s" % (self.last_pred_idx, err)
		self.meta[ self.last_pred_idx, ERR ] += err

	def predict(self,method=None):
		#calc the error from the last prediction
		self.calc_error()

		if method == None : method = self.prediction_method
		pmethod = getattr(self, method)
		rv = pmethod(self.buffer)
		self.predicted.append(rv)
		return rv

	def train(self,value):
		self.add_tick(value)
		self.data.append(value)

	def learn(self,value,method=None):
		print '------------------'
		print 'train-------------'
		self.train(value)
		print 'predict-----------'
		rv = self.predict(method)
		return rv

	def batch_learn(self,queue):
		for val in queue : self.learn(val)


	def summary(self,burn=50):
		p = np.array(self.predicted)
		d = np.array(self.data)
		score = float( np.sum(np.sqrt((d[burn:] - p[burn:-1])**2)) / (len(p)-burn) )
		avg_used = float( np.average(self.meta[:,USED]) )
		#Cummulative per entry error
		CEE = float( np.average(np.sqrt(self.meta[:,ERR])) )
		avg_life = float( np.average(self.tick - self.meta[:,ARRIVED]) )
		self.metrics = {
			'score' : score,
			'data' : { 'mean' : float(d.mean()), 'stddev' : float(d.std()) },
			'predicted' : { 'mean' : float(p.mean()), 'stddev' : float(p.std()) },
			'avg_used' : avg_used,
			'CEE' : CEE,
			'avg_life' : avg_life
		}
		print Dumper.dump(self.metrics)


	def plot(self,which='data',burn=0,begin=0,end=None,color='green'):
		ds = getattr(self,which)
		end = end if end else len(ds)
		plt.plot(xrange(begin,end), ds, color=color)
		plt.tight_layout()

	def plot_nsteps(self,burn=50,begin=0,end=None,color='red'):
		for pos in xrange(burn,len(self.mult_pred)) :
			data = self.mult_pred[pos]
			values = data[np.nonzero(data)] #!fixme
			plt.scatter(xrange(pos, pos+len(values)) , values, color=color, alpha=0.3, s=2)
			plt.tight_layout()

