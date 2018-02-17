#!/usr/bin/env python3

import json

def ratio(a, b):
	assert isinstance(a, float)
	assert isinstance(b, float)

	if b < a:
		(a, b) = (b, a)

	ratio = float(a)/float(b)
	return ratio 

def main(stock_data):
	assert isinstance(stock_data, list)
	stocks = {}
	counts = {}

	# Sumation and counting
	for stock in stock_data:
		stocks.setdefault(stock['channel'], 0.0)
		stocks[stock['channel']] += float(stock['price'])

		counts.setdefault(stock['channel'], 0)
		counts[stock['channel']] += 1
	
	primary_mean = stocks.pop(primary_stock) / float(counts.pop(primary_stock))

	pairs = []
	# Get mean and ratio
	for channel in stocks.keys():
		mean = stocks[channel] / float(counts[channel])
		pairs.append({'value': channel, 'ratio': ratio(primary_mean, mean)})
		
	return pairs
	

if __name__ == "__main__":
	import sys

	stocks = []
	with open(sys.argv[1], 'r') as f:
		stocks = json.loads(f.read())

	print(json.dumps(main(primary, stocks)))
	


# vim: ts=4 sw=4
