#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from configparser import ConfigParser
from sqlalchemy.orm import sessionmaker
from time import sleep, localtime, strftime

# Custom module
from dbctl import engine
from functions import epochtime
from models import Stock, tag
from twse import TWSE

logger = logging.getLogger(__name__)

class StockFetcher:
	def __init__(self, stocks=None):
		if stocks:
			assert isinstance(stocks, dict)
			self.stocks = stocks
		else:
			# Query database to get stock list
			session = sessionmaker(bind=engine)()
			self.stocks = session.query(Stock.symbol, Stock.name).filter(Stock.tag == tag)
			session.close()

	def get_stocks(self):
		"""
		This function will call data loader to fetch stock data from Internet.
		"""
		if self.stocks:
			# Fetch data
			results = []
			loader = TWSE()
			querytime = epochtime()

			for symbol, name in self.stocks:
				stock = "tse_{}".format(symbol)
				try:
					logger.debug("Query stock {} with time {}".format(stock, querytime))
					results.append(loader.get(stock, querytime)["msgArray"][0])
				except Exception:
					logger.error("Failed to query {} data".format(stock))

			return results
	

if __name__ == "__main__":
	import json
	fetcher = StockFetcher()
	print(json.dumps(fetcher.get_stocks(), indent=4))

# vim: ts=4 sw=4 noexpandtab
