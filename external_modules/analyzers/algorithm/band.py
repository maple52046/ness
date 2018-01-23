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
	def __init__(self, prices, length=20):
		list.__init__(self, prices)
		self.mean = mean(prices)
		self.std = std(prices, self.mean)
		self.length = length

	def append(self, price):
		if self.__len__() >= self.length:
			self.pop(0)
		list.append(self, price)
		self.mean = mean(self)
		self.std = std(self, self.mean)

	def value(self):
		return {'top': (self.mean + self.std*2),
			'middle': self.mean,
			'bottom': (self.mean - self.std*2)}

def bollinger_band(stocks):
	band = None
	data = []
	bands = []
	for stock in stocks:

		if len(data) < 20:
			data.append(float(stock["value"]))

		if len(data) >= 20:
			if not band:
				band = Bollinger(data)
			bands.append({"time": stock["time"], "value": band.value()})	

	return bands
		

if __name__ == "__main__":
	import json
	import sys

	pairs = []
	with open(sys.argv[1], 'r') as f:
		pairs = json.loads(f.read())

	print(json.dumps(bollinger_band(pairs)))


# vim: ts=4 sw=4 noexpandtab
