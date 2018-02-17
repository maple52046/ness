#!/usr/bin/env python3

from math import pow, sqrt

mean = lambda array: sum(array)/len(array)
def std(array, xbar):
	s = float(0);
	for x in array:
		s += pow((x - xbar), 2)

	s /= (len(array) - 1)
	return sqrt(s)
	
class Bollinger(list):
	"""
	Bollinger object is inherit Python list. To create this object, 
	you need to pass a initial array with 20 elements, then you can use "value" method 
	to get the value of Bollinger band (a Python dictionary).

	The length of this object will be fixed when the object is created,
	when you append a value into this object,
	it will drop the first element and re-calculate new value.
	"""
	def __init__(self, prices):
		assert isinstance(prices, list)
		list.__init__(self, prices)

	def append(self, price):
		self.pop(0)
		list.append(self, price)

	def value(self):
		m = mean(self)
		s = std(self, m)
		return {
			'top': (m + s*2),
			'middle': m,
			'bottom': (m - s*2)
		}

def bollinger_band(stocks):
	"""
	Pass stock array to get Bollinger Bands
	"""
	band = None
	data = []
	bands = []

	for stock in stocks:

		if len(data) < 20:
			# The data array is initial data of the bolling band
			data.append(float(stock["value"]))

		if len(data) >= 20:
			if not band:
				# Create a Bollinger band with initiate data
				band = Bollinger(data)
			else:
				band.append(stock["value"])

			bands.append({
				"time": stock["time"], 
				"bands": band.value(),
				"value": stock["value"]
			})

	return bands

if __name__ == "__main__":
	import json
	import sys

	pairs = []

	# Load data
	with open(sys.argv[1], 'r') as f:
		pairs = json.loads(f.read())

	print(json.dumps(bollinger_band(pairs)))


# vim: ts=4 sw=4 noexpandtab
