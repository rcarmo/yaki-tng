#!/usr/bin/env python
# encoding: utf-8
"""
Ratings.py

Created by Rui Carmo on 2012-03-24.
Published under the MIT license.
"""

import os
import yaki.Engine, yaki.Store
from yaki.Utils import *
from BeautifulSoup import *

class MindMapViewerWikiPlugin(yaki.Plugins.WikiPlugin):
  def __init__(self, registry, webapp):
    self.ac = webapp.getContext()
    self.imgpath = os.path.join('/',self.ac.theme,'img')
    registry.register('markup',self, 'plugin','rating')

  def run(self, serial, tag, tagname, pagename, soup, request, response):  
    try:
      value = tag['value']
    except KeyError:
      return True
    tag.replaceWith('<img class="rating" width="64" height="19" src="%s/%s.png">' % (self.imgpath, value))
    return False
     
    
    
