#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json

from configparser import ConfigParser
from datetime import datetime, timedelta
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

config = ConfigParser()
config.read('config.ini')
try:
	timezone = int(config['global']['timezone'])
except:
	timezone = 0

fields = {
	"o": "open",
	"y": "yesterday",
	"v": "volume",
	"h": "high",
	"l": "low",
	"a": "best_sell_price",
	"f": "best_sell_number",
	"b": "best_buy_price",
	"g": "best_buy_number",
	"z": "price"
}

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

	def get_stocks(self, querytime=epochtime(), intraday=False):
		"""
		This function is used to get last price of stocks from Internet with data loader.
		"""
		if self.stocks:
			loader = TWSE()
			data = []

			# Get the data we needed.
			for symbol, name in self.stocks:
				try:
					# Get stock
					stock_id = "tse_{}".format(symbol)
					logger.debug("Query stock {} with time {}".format(stock_id, querytime))
					stock= loader.get(stock_id, querytime)["msgArray"][0]
					if intraday == True and "z" not in stock.keys():
						logger.debug("The intraday data of stock {} didn't have price".format(stock_id))
					else:
						data_pack = self.generate_influxdb_data(stock, intraday)
						if data_pack["fields"]:
							data.append(data_pack)
				except KeyError:
					logger.error("Failed to query stock {} with time {}".format(stock_id, querytime))

			if data:
				# Store dynamic data to influxdb
				influxclient.create_database('ness')
				influxclient.write_points(data)

			return True

	def generate_influxdb_data(self, stock, intraday=False):
		"""
		This function is used to generate data object which will be stored to InfluxDB.
		The argument 'fields' is a Python dict which is a 'filed name' and 'stock index' mapping,
		e.g.:
			{"price": "z"}
			{"open": "o", "volume": "v"}
		"""

		assert isinstance(stock, dict)
		assert isinstance(fields, dict)

		if stock:
			# Generate data
			data = {"measurement": "twse"}
			utctime = datetime.fromtimestamp(int((int(stock["tlong"]) - 1000) / 1000)) - timedelta(hours=timezone)
			data["time"] = utctime.strftime("%Y-%m-%dT%H:%M:%SZ")
			data["tags"] = {
				"channel": stock["ch"],
				"name": stock["n"],
				"intraday": intraday
			}
			data["fields"] = {}
			for k, v in stock.items():
				if k in fields.keys():
					data["fields"][fields[k]] = v

		return data

def daily(interval=60):

	fetcher = StockFetcher()
	open_time = datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
	closed_time = datetime.now().replace(hour=13, minute=30, second=0, microsecond=0)

	while True:
		current_time = datetime.now()
		if current_time < open_time:
			sleep(1)
		elif current_time > closed_time:
			print("Market closed")
			break
		else:
			fetcher.get_stocks(intraday=True)
			next_time = current_time + timedelta(0, interval)
			while datetime.now() < next_time:
				sleep(1)
	fetcher.get_stocks()

def oneshot():
	fetcher = StockFetcher()
	fetcher.get_stocks()

if __name__ == "__main__":
	import sys
	from optparse import OptionParser

	parser = OptionParser()
	parser.add_option("-d", "--daily", dest="daily", action="store_true")
	parser.add_option("-s", "--oneshot", dest="oneshot", action="store_true")
	(options, args) = parser.parse_args()

	if options.daily == True:
		print("start daily job")
		daily()
	elif options.oneshot == True:
		print("start oneshot job")
		oneshot()
	else:
		parser.print_help()
		sys.exit(1)

	sys.exit(0)

# vim: ts=4 sw=4 noexpandtab
