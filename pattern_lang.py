import sys
from lepl import *

#Flatten list of list of list .... LoL
def flatten(lst):
	for el in lst :
		try: #if elem is list, process is recursively
			for e in flatten(el): yield e
		except TypeError : #if is not list return it
			yield el

class PatternLang:

	def __init__(self):
		self.grammar = []
		self.build_grammar()

	def node(self,val):
		return val

	def calc(self,lst):
		if len(lst) >= 3:
			if lst[1] == '*' : return [ lst[0] ] * lst[2]
			if lst[1] == ':' :
				#extract only the numbers
				args = filter(lambda n: isinstance(n,int), lst)
				return range( *args )
		return lst

	def process(self,lst):
		for i in range(len(lst)): #go over the list
			if isinstance(lst[i],list): #if list process it
				lst[i] = self.process(lst[i]) #recursivly
		#it is operation, do it
		return self.calc(lst)

	def build_grammar(self):
		#definition of tokens
		num = Integer() >> int
		comma = Literal(',')
		spaces = Space()[:]
		dcol = Literal(':')
		mult = Literal('*')
		left_bracket = Literal('(')
		right_bracket = Literal(')')

		with Separator(~spaces):
			repeat = num & mult & num > self.node
			#greeder first
			ranges = num & dcol & ( (num & dcol & num) | num ) > self.node
			ops = repeat | ranges | num #operations
			op_list = ops[1:,~comma] #more than one ops separated by comma
			group = Delayed() #there will something encased in brackets
			group_repeat = group & mult & num > self.node #like a repeat but for block
			group_list = (group_repeat | group | op_list | ops)[1:,~comma] #block-list
			group += ~left_bracket & group_list & ~right_bracket > self.node #finally define the block
			atom = group_repeat | group | ops #group or standalone op
			self.grammar = atom[1:,~comma] > self.node

	def parse(self,txt):
		return self.grammar.parse(txt)

	def generate(self,pattern):
		return list( flatten( self.process( self.parse(pattern) ) ))


def test():
	arg = ''
	if len(sys.argv) > 1 : arg = sys.argv[1] 
	pat = arg if arg else '3*4,(2*4,1:5)*2,(5*2,3*3)'
	print pat
	p = PatternLang()
	lst = p.parse(pat)[0]
	print lst
	res = p.process(lst)
	print res
	print list(flatten(res))


if __name__ == '__main__' : test()
