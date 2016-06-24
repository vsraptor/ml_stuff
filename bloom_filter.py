from bitarray import bitarray
import mmh3
import math

def mm(cnt,prob) : return - (cnt * math.log(prob)) / (math.log(2)**2)
def kk(cnt,mbits) : return (mbits/cnt) * math.log(2)

class BloomFilter:

	def __init__(self, size, hash_count):
		self.size = size
		self.hash_count = hash_count
		self.bits = bitarray(size)
		self.bits.setall(0)

	def add(self, string):
		for seed in xrange(self.hash_count):
			result = mmh3.hash(string, seed) % self.size
			self.bits[result] = 1

	def lookup(self, string):
		for seed in xrange(self.hash_count):
			result = mmh3.hash(string, seed) % self.size
			if self.bits[result] == 0:
				return 0
		return 1

