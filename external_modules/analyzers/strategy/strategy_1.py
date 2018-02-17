#!/usr/bin/env python3

import sys
sys.path.insert(0, './external_modules/analyzers/algorithm')

from pair import trading_pair
from band import bollinger_band

def strategy_1(primary, secondary, stocks):
	"""
	This strategy integrate trading pair and bollinger band.
	"""
	
	pair = trading_pair(primary, secondary, stocks)
	return bollinger_band(pair)

if __name__ == "__main__":

	import json

	stocks = []
	# In current version, we load data from a json file.
	with open(sys.argv[3], 'r') as f:
		stocks = json.loads(f.read())

	# Output result with json format
	print(json.dumps(strategy_1(sys.argv[1], sys.argv[2], stocks)))
