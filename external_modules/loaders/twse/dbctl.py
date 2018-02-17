#!/usr/bin/env python

from influxdb import InfluxDBClient
from sqlalchemy import create_engine

get_mariadb_engine = lambda connection: create_engine(connection)
get_influx_client = lambda host,  port, user, password, database: InfluxDBClient(host,  port, user, password, database)
