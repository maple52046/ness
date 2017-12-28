#!/usr/bin/env python3

from algorithm.bbands import BollingerBands

import json
import sys

	
def pair_trade_with_bollinger_bands(stocks):
	"""
	Pari Trade with Bollinger Bands (for backtest)
	"""

	# Convert data
	prices = {}
	for stock in stocks:
		prices.setdefault(stock['channel'], [])
		prices[stock['channel']].append(stock['price'])

	# Determine fration
	channels = list(prices.keys())
	if float(prices[channels[1]][0]) >= float(prices[channels[0]][0]):
		channels[0], channels[1] = channels[1], channels[0]

	# Format data
	pair_prices = []
	for i in range(len(prices[channels[0]])):
		try:
			pair_prices.append( float(prices[channels[0]][i])/float(prices[channels[1]][i]) )
		except IndexError:
			break

	# Analysis data with algorithm
	bbands = []
	if len(pair_prices) >= 20:
		alg = BollingerBands(pair_prices[0:20])
		bbands.append(alg.value())

		for i in range(21, len(pair_prices)):
			alg.append(pair_prices[i])
			bbands.append(alg.value())

	return {'{}/{}'.format(channels[0], channels[1]) : bbands}
	

if __name__ == "__main__":

	import sys

	data = pair_trade_with_bollinger_bands(json.loads(sys.argv[1]))
	print(json.dumps(data))
	#print(data)

# vim: ts=4 sw=4 noexpandtab
