#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import requests

from configparser import ConfigParser
from io import StringIO, open
from lxml import etree
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dbctl import engine
from models import Stock

def import_tw0050_concept(stocks):
    """
    This function will import the concepts of tw0050 (JSON format) to database (MariaDB).
    """
    assert isinstance(stocks, dict)

    # Connect to database
    session = sessionmaker(bind=engine)()

    # Get current list
    # Remove stock if that stock is not in current list
    # Add new stock if stock is not existing
    stock_objs = []
    for stock_id, stock_name in stocks.items():
        symbol = "{}.tw".format(stock_id)
        stock_objs.append(Stock(symbol, stock_name.encode('utf8'), "tw0050"))

    if stock_objs:
        session.add_all(stock_objs)
        session.commit()

    session.close()
    
def get_0050_from_cnyes(html_file=''):
    """
    This function is used to get stock list of TW0050 from www.cnyes.com.
    
    P.S. in current version, it's recommended you to pass html file in the arguments to this funciton.
    """
    
    # Get HTML raw data
    if html_file:
        with open(html_file, 'r', encoding='utf8') as f:
            raw = f.read()
    else:
        url = "https://www.cnyes.com/twstock/Etfingredient/0050.htm"
        session = requests.Session()
        raw = session.get(url,verify=False).text
    
    stocks = {}
    if raw:
        # Parse HTML
        parser = etree.HTMLParser()
        html = etree.parse(StringIO(raw), parser)
        for hyperlink in html.xpath("//a[contains(@href, '/twstock/profile/')]"):
            url = hyperlink.get("href")
            stock_id = re.sub("[^0-9]", "", url)
            stock_name = hyperlink.text.strip()
            
            if stock_id != "0050":
                stocks.setdefault(stock_id, stock_name)
            
    return stocks

if __name__ == "__main__":

    import sys
    from models import Base

    # Create database table
    Base.metadata.create_all(engine)

    # Get the concepts of 0050
    html_file = sys.argv[1] if len(sys.argv) >= 2 else input("Please input the path of 0050.html: ")
    stocks = get_0050_from_cnyes(html_file)

    # Import concept stock to database
    import_tw0050_concept(stocks)

# vim: ts=4 sw=4 expandtab
