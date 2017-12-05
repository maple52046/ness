#!/usr/bin/env python

from configparser import ConfigParser
from influxdb import InfluxDBClient
from models import Stock, Base
from sqlalchemy import create_engine

# Load configuration
config = ConfigParser()
config.read('config.ini')

# Create DB engine
engine = create_engine(config['mariadb']['connection'])

# InfluxDB client
influx = config["influxdb"]
influxclient = InfluxDBClient(influx["host"],  influx["port"], influx["user"], influx["password"], influx["database"])
