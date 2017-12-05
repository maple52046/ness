#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, VARCHAR, NVARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
tag = 'tw0050'

class Stock(Base):
    __tablename__ = 'stock_list'

    symbol = Column(VARCHAR(12), primary_key=True)
    name = Column(NVARCHAR(36))
    tag = Column(VARCHAR(12))

    def __init__(self, symbol, name='', custom_tag=tag):
        self.symbol = symbol
        self.name = name
        self.tag = custom_tag

# vim: ts=4 sw=4 expandtab
