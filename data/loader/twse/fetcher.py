#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

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

	def get_closed_info(self, querytime=epochtime()):
		"""
		This function is used to get stocks after market is closed.
		"""
		fields = {
			"open": "o",
			"yesterday": "y",
			"volume": "v",
			"high": "h",
			"low": "l",
			"best_sell_price": "a",
			"best_sell_number": "f",
			"best_buy_price": "b",
			"best_buy_number": "g"
		}
		return self.get_stocks(querytime, "twse_stock_closed", fields)

	def get_intraday_info(self, querytime=epochtime()):
		"""
		This function is used to get intraday information of stocks
		"""
		fields = {
			"price": "z",
			#"temporal_volume": "tv",
			#"best_sell_price": "a",
			#"best_sell_number": "f",
			#"best_buy_price": "b",
			#"best_buy_number": "g"
		}
		return self.get_stocks(querytime, "twse_stock_intraday", fields)

	def get_stocks(self, querytime, measurement, fields):
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
					stock = loader.get(stock_id, querytime)["msgArray"][0]
					data_pack = self.generate_influxdb_data(stock, measurement, fields)
					if data_pack["fields"]:
						data.append(data_pack)
				except:
					logger.error("Failed to query stock {}".format(stock_id))

			if data:
				# Store dynamic data to influxdb
				influxclient.create_database('ness')
				influxclient.write_points(data)

			return True

	def generate_influxdb_data(self, stock, measurement, fields):
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
			data = {"measurement": measurement}
			utctime = datetime.fromtimestamp(int((int(stock["tlong"]) - 1000) / 1000)) - timedelta(hours=timezone)
			data["time"] = utctime.strftime("%Y-%m-%dT%H:%M:%SZ")
			data["tags"] = {
				"channel": stock["ch"],
				"name": stock["n"]
			}
			data["fields"] = {}
			for name, index in fields.items():
				try:
					data["fields"][name] = stock[index]
				except:
					logger.error("Stock didn't have {}".format(name))

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
			fetcher.get_intraday_info()
			next_time = current_time + timedelta(0, interval)
			while datetime.now() < next_time:
				sleep(1)
	fetcher.get_closed_info()

if __name__ == "__main__":
	daily()

# vim: ts=4 sw=4 noexpandtab
