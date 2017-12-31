#!/usr/bin/env python3

import json

def is_pair(a, b):
	assert isinstance(a, float)
	assert isinstance(b, float)

	if b < a:
		(a, b) = (b, a)

	ratio = float(a)/float(b)
	return ratio if ratio >= 0.9 else None

def main(stocks):
	assert isinstance(stocks, dict)
	stocks = list(stocks.items())
	stocks.sort()

	pairs = {}
	for i in range(len(stocks)-1):
		for j in range((i+1), len(stocks)):
			ch1, p1 = stocks[i]
			ch2, p2 = stocks[j]
			ratio_value = is_pair(float(p1), float(p2))
			if ratio_value:
				pairs.setdefault(ch1, {})
				pairs.setdefault(ch2, {})
				pairs[ch1][ch2] = ratio_value
				pairs[ch2][ch1] = ratio_value

	return pairs
	

if __name__ == "__main__":
	import sys

	stocks = json.loads(sys.argv[1])
	print(json.dumps(main(stocks)))
	


# vim: ts=4 sw=4
