#!/usr/bin/env python3

import json
import dateutil

def ratio(a, b):
	assert isinstance(a, float)
	assert isinstance(b, float)

	if b < a:
		(a, b) = (b, a)

	ratio = float(a)/float(b)
	return ratio 

def trading_pair(primary, secondary, data):
	assert isinstance(primary, str)
	assert isinstance(secondary, str)
	assert isinstance(data, list)
	stocks = {primary: [], secondary: []}
	pairs = []

	for stock in data:
		# Filter data
		try:
			channel = stock.pop('channel')
			stocks[channel].append(stock)
		except KeyError:
			# Ignore incorrect data
			pass

		if len(stocks[primary]) >= 1 and len(stocks[secondary]) >= 1:
			# Create pair
			p = stocks[primary].pop(0)
			s = stocks[secondary].pop(0)

			date = [p['time'], s['time']]
			date.sort()
			pair = {
				"value": float(p["price"])/float(s["price"]),
				"time": date[1]
			}
			pairs.append(pair)
	
	return pairs
	

if __name__ == "__main__":
	import sys

	stocks = []
	with open(sys.argv[3], 'r') as f:
		stocks = json.loads(f.read())

	print(json.dumps(trading_pair(sys.argv[1], sys.argv[2], stocks)))
	


# vim: ts=4 sw=4
