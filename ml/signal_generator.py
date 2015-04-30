import numpy as np

class Signal():

	cfg = {
		'base' : 30,
		'spikers' : [
			{ 'high':100, 'tresh' : 0.81, 'width': 6, 'every_nth' : 50, 'active' : True }, #, 'type' : 'random' }
			{ 'high':90, 'tresh' : 0.70, 'width': 5, 'every_nth' : 70, 'active' : True } #, 'type' : 'random' }
		],
		'waves' : [
			{ 'amp': 20, 'freq': 30, 'active' : False },
			{ 'amp': 10, 'freq': 100, 'active' : False },
			{ 'amp': 30, 'freq': 200, 'active' : True }
		],
		'trends' : [
			{ 'intercept': 5, 'slope': 0.01, 'active' : False }
		],
		'noise' : [
			{ 'high':7, 'low':-7, 'active' : False },
			{ 'high':3, 'low':-3, 'active' : False }
		]
	}

	def __init__(self,low=0,high=100,cfg=None):
		self.limit_low = low
		self.limit_high = high
		self.trim = True
		#hold generators
		self.cfg = Signal.cfg if cfg == None else cfg

	@staticmethod
	def trend(tick,intercept,slope):
		return intercept + slope*tick

	@staticmethod
	def sine(tick,amp,freq):
		return amp * np.sin( 2 * np.pi * 1/freq * tick) #!fixme

	@staticmethod
	def noise(low,high):	return np.random.uniform(low,high)

	@staticmethod
	def spikeit(tick,high,tresh,width):
		if tick <= width : return np.random.uniform(high*tresh, high)
		return 0

	@staticmethod
	def spike(tick,spiker):
		w = np.random.randint(2,spiker['width']) if spiker.has_key('type') and spiker['type'] == 'random' else spiker['width']
		nth = spiker['every_nth']
		mth = int( tick / nth ) * nth
		spike_tick = 0
		if mth <= tick <= mth + w : spike_tick = 0 if mth == 0 else tick % mth
		if spike_tick : return Signal.spikeit(spike_tick,spiker['high'],spiker['tresh'], w)
		return 0

	def signal(self):
		tick = 0
		while True : #!fixme check for key existence
			value = self.cfg['base']
			for c in self.cfg['trends'] :
				if c['active'] : value += Signal.trend(tick, c['intercept'], c['slope'])
			for c in self.cfg['spikers'] :
				if c['active'] : value += Signal.spike(tick, c)
			for c in self.cfg['noise'] :
				if c['active'] : value += Signal.noise(c['low'], c['high'])
			for c in self.cfg['waves'] :
				if c['active'] : value += Signal.sine(tick, c['amp'], c['freq'])

			if self.trim :
				value = self.limit_high if value > self.limit_high else value
				value = self.limit_low if value < self.limit_low else value

			yield value
			tick += 1

	def signal_ticks(self,tcount=10):
		sig = self.signal()
		return [ sig.next() for i in xrange(0,tcount) ]


if __name__ == '__main__' : 
	pass

