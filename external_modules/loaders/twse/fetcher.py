#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json

from configparser import ConfigParser
from datetime import datetime, timedelta
from influxdb import InfluxDBClient
from sqlalchemy.orm import sessionmaker
from threading import Condition, Thread
from time import sleep, strftime

# Custom module
from dbctl import get_mariadb_engine, get_influx_client
from functions import epochtime
from models import Stock, tag
from twse import TWSE

logger = logging.getLogger(__name__)
try:
	import coloredlogs
	formatter = '%(asctime)s - %(levelname)-5s - %(message)s'
	coloredlogs.install(level='DEBUG', fmt=formatter)
except:
	formatter = logging.Formatter('%(asctime)s - %(levelname)-5s - %(message)s' ,datefmt="%Y/%m/%d %H:%M:%S")
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	ch.setFormatter(formatter)
	logger.setLevel(logging.DEBUG)
	logger.addHandler(ch)

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
mariadb_engine = None
influxclient = None

class StockFetcher:
	def __init__(self, timezone=0):
		# Query database to get stock list
		session = sessionmaker(bind=mariadb_engine)()
		self.stocks = session.query(Stock.symbol, Stock.name).filter(Stock.tag == tag)
		session.close()

	def get_stocks(self, querytime=epochtime(), intraday=False):
		"""
		This function is used to get last price of stocks from Internet with data loader.
		"""
		if self.stocks:
			loader = TWSE()
			data = []
			threads = []
			condition = Condition()

			# Get the data we needed.
			for symbol, name in self.stocks:
				t = Thread(target=self.get_stock, args=(symbol, loader, querytime, data, intraday, condition))
				t.start()
				threads.append(t)

			logger.debug("Waiting for all job")
			for t in threads:
				t.join()

			if data:
				# Store dynamic data to influxdb
				influxclient.create_database('ness')
				influxclient.write_points(data)

			return True

	def get_stock(self, symbol, loader, querytime, data, intraday, condition):
		"""
		This function will use the loader created from "get_stocks" to query data from TWSE
		"""
		stock_id = "tse_{}".format(symbol)

		# Lock loader
		condition.acquire()

		# Get stock
		try:
			stock = loader.get(stock_id, querytime)["msgArray"][0]
			logger.debug("Query stock {} with time {}".format(stock_id, querytime))
		except:
			logger.warning("Failed to query stock {} at time {}".format(stock_id, querytime))
			stock = {}

		# Unlock loader
		condition.notifyAll()
		condition.release()
			
		if stock:
			if intraday == True and "z" not in stock.keys():
				logger.debug("The intraday data of stock {} didn't have price".format(stock_id))
			else:
				data_pack = self.generate_influxdb_data(stock, intraday)
				if data_pack["fields"]:
					data.append(data_pack)

	def generate_influxdb_data(self, stock, intraday=False):
		"""
		This function is used to generate data object which will be stored to InfluxDB.
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
	open_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
	closed_time = datetime.now().replace(hour=13, minute=30, second=0, microsecond=0)

	while True:
		current_time = datetime.now()
		if current_time < open_time:
			pass
		elif current_time > closed_time:
			print("Market closed")
			break
		else:
			fetcher.get_stocks(intraday=True)
			next_time = current_time + timedelta(0, interval)
			while datetime.now() < next_time:
				pass
	fetcher.get_stocks()

def oneshot():
	fetcher = StockFetcher()
	fetcher.get_stocks()

if __name__ == "__main__":
	import sys
	from optparse import OptionParser

	parser = OptionParser()
	parser.add_option("-c", "--config", dest="config", default="config.ini")
	parser.add_option("-d", "--daily", dest="daily", action="store_true")
	parser.add_option("-s", "--oneshot", dest="oneshot", action="store_true")
	(options, args) = parser.parse_args()

	try:
		config = ConfigParser()
		config.read(options.config)
		timezone = int(config['global']['timezone'])
		mariadb_engine = get_mariadb_engine(config['mariadb']['connection'])
		influxclient = get_influx_client(
			config['influxdb']['host'],
			config['influxdb']['port'],
			config['influxdb']['user'],
			config['influxdb']['password'],
			config['influxdb']['database'])
	except:
		pass

	if options.daily == True:
		print("start daily job")
		daily(60)
	elif options.oneshot == True:
		print("start oneshot job")
		oneshot()
	else:
		parser.print_help()
		sys.exit(1)

	sys.exit(0)

# vim: ts=4 sw=4 noexpandtab
