#!/usr/bin/env python
# encoding: utf-8
"""
FontPreview.py

Created by Rui Carmo on 2011-04-27
Published under the MIT license.
"""

import yaki.Engine, yaki.Store, yaki.Locale
from yaki.Utils import *
from BeautifulSoup import *
import os, re, urlparse

template = """
<div class="quicklook_holder"%(align)s><a title="%(title)s" href="%(large)s" class="quicklook"><img alt="%(alt)s" src="%(small)s" class="thumb"></a></div>
"""

class FontPreviewWikiPlugin(yaki.Plugins.WikiPlugin):
  def __init__(self, registry, webapp):
    self.webapp = webapp
    registry.register('markup', self, 'plugin','font')
    self.ac = webapp.getContext() 
    self.i18n = yaki.Locale.i18n[self.ac.locale]


  def run(self, serial, tag, tagname, pagename, soup, request, response):  
    params = {'serial':serial,'align':''}
      
    try:
      image = os.path.basename(tag['src'])
    except KeyError:
      print "Error in tag parameters for %s in %s" % (str(tag), pagename)
      return True

    try:
      params['align'] = tag['align']
    except KeyError:
      pass
    
    try:
      params['title'] = tag['title']
    except KeyError:
      params['title'] = ''
      pass
    
    if params['align'] != '':
      params['align'] = ' align="%s"' % params['align']
    
    if self.ac.store.isAttachment(pagename, image):
      c = self.webapp.getContext()
      params['large'] = c.fontpreview + pagename + "/" + image
      params['small'] = c.thumb + pagename + "/" + image
    else:
      print "Missing attachment %s in %s" % (image, pagename)
      return True

    params['alt'] = self.i18n['quicklook_click_to_zoom']
    tag.replaceWith(template % params)
    # No further processing is required
    return False
     
    
    
