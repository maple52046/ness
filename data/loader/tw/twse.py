#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

from functions import epochtime

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
             
           
    def get(self, stock, querytime=''):
        """
        This function will create session to connect to TWSE, and pull stock data with current time.
        To use this function, you need to pass stock ID (e.g. "tse_1101.tw") in arguments, 
        and the function will return data with JSON format. 
        """
        if not self.session:
            self.create_session()
        
        if not querytime:
            querytime = epochtime()

        url = "{}/api/getStockInfo.jsp?ex_ch={}&_={}".format(
            self.baseurl, stock, querytime
        )

        return self.session.get(url).json()
    
if __name__ == "__main__":
    
    obj = TWSE()
    print(json.dumps(obj.get('tse_1101.tw'), indent=4))
    
# vim: ts=4 sw=4 expandtab
