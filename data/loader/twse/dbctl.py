#!/usr/bin/env python

from configparser import ConfigParser
from models import Stock, Base
from sqlalchemy import create_engine

# Load configuration
config = ConfigParser()
config.read('config.ini')

# Create DB engine
engine = create_engine(config['static_data']['connection'])
