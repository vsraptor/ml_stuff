#!/usr/bin/env python
from sklearn.base import BaseEstimator
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def random_signal(N=10000,freq_count=3,noise=False):
	t = np.arange(N,dtype=float)
	#pcik rand freq and conv them to freq
	Ts = np.random.rand(freq_count)*2000+10
	fs = 1./Ts
	#pick rand amplitudes
	amp = np.random.rand(freq_count)*200+100
	#pick rand phases
	ph = np.random.rand(freq_count)*2*np.pi
	#make signal
	sig = np.zeros(N)
	for i in range(len(fs)):
		sig += amp[i] * np.sin(2*np.pi*t*fs[i]+ph[i])
	if noise : #add noise
		sn = sig + np.random.randn(N)*3*sig + np.random.randn(N)*700
		return sn
	return sig

class FFT(BaseEstimator):

	@staticmethod
	def cos_sin(time,freq,camp,samp):
		return camp * np.cos( 2 * np.pi * freq * time) + samp * np.sin( 2 * np.pi * freq * time)

	#generate wave as sum of sinusoids
	@staticmethod
	def wave(time_list, frs_amps,dc_offset=0): #frs_amps : freq-amps numpy array
		frs_amps_len = len(frs_amps)
		#repeat time items frs_amps_len-times
		lst = [ FFT.cos_sin(x, *y) for x in time_list for y in frs_amps.tolist() ]
		#sum every frs_amps_len elements
		return [ sum(lst[i:i+frs_amps_len]) + dc_offset for i in np.arange(0,len(time_list)*frs_amps_len,frs_amps_len) ]


	def __init__(self,topn_freq=4):
		self.topn = topn_freq
		self.fitted = False

#	def get_params(self):
#		return { 'N':self.N, 'signal': self.signal, 'freqs': self.freqs, 'topn':self.topn, 'fitted':self.fitted,
#					'amps':self.amps, 'cos_amps':self.amps, 'sin_amps':self.sin_amps, 'frs_amps':self.frs_amps  }

	def fit(self, signal):
		#flatten/fix the signal shape
		if len(signal.shape) == 1 : self.signal = signal
		else: self.signal = signal.ravel()

		#number of samples
		self.N = len(self.signal)
		#do a DFT, returns array of cos/sin amplitudes as complex num ordered by +asc/-asc freq
		self.amps = np.fft.fft(self.signal)
		self.ix = np.arange(1,self.N/2+1) #first half a +freq, second half -freq
		#calculate power spectrum density
		self.psd = np.abs(self.amps[self.ix])**2 + np.abs(self.amps[-self.ix])**2
		#get top freqs indexes
		self.idxs = (-self.psd).argsort()[:self.topn]
		fsbin = self.ix[self.idxs]#bins with the topn max freqs
		self.all_freqs = np.fft.fftfreq(self.N)
		self.freqs = self.all_freqs[fsbin]

		#!fixme
		#self.amps[0] = self.amps[0]/2
		#self.amps[self.N/2] = self.amps[self.N/2]/2

		norm = self.amps[fsbin] / (self.N/2)
		self.cos_amps = np.real(norm) #cos
		self.sin_amps = -np.imag(norm)
		self.dc_offset = np.real(self.amps[0])/self.N

		self.frs_amps = np.hstack((np.c_[self.freqs], np.c_[self.cos_amps], np.c_[self.sin_amps]))
		self.fitted = True
		return self

	def predict(self,X,use_waves=None):

		if len(X.shape) == 1 : times = X
		else: times = X.ravel()

		if not self.fitted : raise Exception("You have to first fit() the model")
		if use_waves == None : return np.array( FFT.wave(times, self.frs_amps,dc_offset=self.dc_offset) )
		if isinstance(use_waves,slice) : return np.array( FFT.wave(times, self.frs_amps[use_waves], dc_offset=self.dc_offset) )
		return np.array( FFT.wave(times, self.frs_amps[use_waves:use_waves+1], dc_offset=self.dc_offset) )


	def plot_psd(self):
		plt.plot(self.all_freqs[self.ix],self.psd,'k-')

	def plot_orig_signal(self):
		t = np.arange(self.N,dtype=float)
		plt.plot(t,self.signal,'k-',label='Signal')

	def plot_est_signal(self,time_range=0,use_waves=None,date_range=None):
		if time_range <= 0 : time_range = self.N
		t = np.arange(time_range,dtype=float)
		dt = date_range if isinstance(date_range, np.ndarray) else t
		plt.plot(dt,self.predict(t,use_waves),label='Est. signal: %s' % use_waves , alpha=0.6)

