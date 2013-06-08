#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2012, Rui Carmo
Description: Utility functions and classes 
License: MIT (see LICENSE.md for details)
"""

import os, sys, time, logging
from bs4 import BeautifulSoup

log = logging.getLogger()

class Restyler():
  def __init__(self, buffer):
    self.styles = {}
    soup = BeautifulSoup(buffer)
    self.grabStyles(soup)

  def grab(self, soup):
    styled = soup.findAll(attrs={'style':re.compile('.+')})
    for tag in styled:
      self.styles[tag.name] = tag['style']

  def apply(self, soup):
    for tag in self.styles.keys():
      items = soup.findAll(tag)
      for i in items:
        i['style'] = self.styles[tag]
    return soup