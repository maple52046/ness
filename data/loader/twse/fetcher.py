#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from configparser import ConfigParser
from influxdb import InfluxDBClient
from sqlalchemy.orm import sessionmaker
from threading import Thread
from time import sleep, localtime, strftime

# Custom module
from dbctl import engine, influxclient
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
			loader = TWSE()
			querytime = epochtime()
			data = []

			# Get the data we needed.
			for symbol, name in self.stocks:
				# Get stock
				stock_id = "tse_{}".format(symbol)
				try:
					logger.debug("Query stock {} with time {}".format(stock_id, querytime))
					stock = loader.get(stock_id, querytime)["msgArray"][0]
					data.append(self.generate_influxdb_data(stock))
				except:
					logger.error("Failed to query stock {}".format(stock_id))


			# Store dynamic data to influxdb
			influxclient.create_database('ness')
			influxclient.write_points(data)

			return True

	def generate_influxdb_data(self, stock):

		assert isinstance(stock, dict)
		if stock:
			# Generate data
			data = {"measurement": "twse_stock_last"}
			data["time"] = int((int(stock["tlong"]) - 1000) / 1000)
			data["tags"] = {"channel": stock["ch"]}
			data["fields"] = {"price": stock["z"]}

		return data

if __name__ == "__main__":
	import json
	fetcher = StockFetcher()
	fetcher.get_stocks()

# vim: ts=4 sw=4 noexpandtab
