from bitarray import bitarray
import mmh3
import numpy as np
import math

def mm(cnt,prob) : return - (cnt * math.log(prob)) / (math.log(2)**2)
def kk(cnt,mbits) : return (mbits/cnt) * math.log(2)

class Blooms:

	def __init__(self, nfilters, nbits, hash_count):
		self.nbits = nbits
		self.nfilters = nfilters
		self.hash_count = hash_count
		self.bits = bitarray(nfilters * nbits)
		self.bits.setall(0)

	def add(self, nth_filter, string):
		for seed in xrange(self.hash_count):
			result = mmh3.hash(string, seed) % self.nbits
			#calc offset of nth filter then set the bits
			self.bits[(nth_filter * self.nbits) + result] = 1

	def add_bin(self,nth_filter, bitary):
		self.add(nth_filter, bitary.tobytes())

	def lookup(self, string):
		for seed in xrange(self.hash_count):
			result = mmh3.hash(string, seed) % self.nbits
			if self.bits[(nth_filter * self.nbits) + result] == 0:
				return 0
		return 1

	def bin_lookup(self, bitary):
		return self.lookup(bitary.tobytes())

	def to_np(self):
		ary = np.zeros((self.nfilters,self.nbits))
		for f in xrange(self.nfilters):
			pos = f * self.nbits
			ary[f] = np.array(self.bits[ pos : pos+self.nbits ].tolist(), dtype='uint8')
		return ary

