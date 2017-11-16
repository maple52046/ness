#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import requests
import time

from io import StringIO, open
from lxml import etree

def get_0050(html_file=''):
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
        #pattern = re.compile('/twstock/profile/*.htm')
        for hyperlink in html.xpath("//a[contains(@href, '/twstock/profile/')]"):
            url = hyperlink.get("href")
            stock_id = re.sub("[^0-9]", "", url)
            stock_name = hyperlink.text.strip()
            
            if stock_id != "0050":
                stocks.setdefault(stock_id, stock_name)
            
            
    return stocks
    
    

class TWSE:
    """
    TWSE is a data loader used to get stock data from Taiwan Stock Exchange Corporation.
    """
    def __init__(self, baseurl="http://mis.twse.com.tw/stock"):
        self.baseurl = baseurl
        self.headers = {'Accept-Language': 'zh-TW'}
        self.session = None

        
    def create_session(self):
        """
        Connect to TWSE and get cookies with new session.
        """
        # Get cookie
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        url = '{}/index.jsp'.format(self.baseurl)
        self.session.get(url).cookies
             
           
    def get(self, stock):
        """
        This function will create session to connect to TWSE, and pull stock data with current time.
        To use this function, you need to pass stock ID (e.g. "tse_1101.tw") in arguments, 
        and the function will return data with JSON format. 
        """
        if not self.session:
            self.create_session()
        
        epochtime = int(time.time() * 1000 + 1000)
        url = "{}/api/getStockInfo.jsp?ex_ch={}&_={}".format(
            self.baseurl, stock, epochtime
        )

        return self.session.get(url).json()
    
if __name__ == "__main__":
    
    obj = TWSE()
    print(json.dumps(obj.get('tse_1101.tw'), indent=4))
    #get_0050('0050.html')
    