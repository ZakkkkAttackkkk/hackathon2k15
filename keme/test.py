class Complex:
	def __init__(self,real,imag):
		self.real = real
		self.imag = imag
	def __add__(self,other):
		return Complex(self.real+other.real,self.imag+other.imag);
	def __sub__(self,other):
		return Complex(self.real-other.real,self.imag-other.imag);
	def __repr__(self):
		return "{}+{}j".format(self.real,self.imag);
	def conjugate(self):
		self.imag=-self.imag

class Complex_(Complex):
	def __init__(self):
		self.real=0;self.imag=0
