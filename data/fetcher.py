#!/usr/bin/env python

from data.loader import TWSE
from time import sleep, localtime, strftime
import json
import MySQLdb


loader = TWSE()
stock = "tse_1101.tw"

db = MySQLdb.connect(host="localhost", user="ness", passwd="ness", db="ness")
cursor = db.cursor()

try:
	data = loader.get('tse_1101.tw')["msgArray"][0]
	sql = "INSERT INTO stock VALUES ('{a}', '{b}', '{c}', '{d}', '{f}', '{g}', '{h}', '{i}', '{ip}', '{it}', '{l}', '{mt}', '{o}', '{p}', '{ps}', '{pz}', '{s}', '{t}', '{ts}', '{tv}', '{v}', '{v}', '{w}', '{y}', '{z}');".format(**data)
	cursor.execute(sql)
	db.commit()
	print(strftime("%H:%M:%S",localtime()))
except:
	pass

db.close()
