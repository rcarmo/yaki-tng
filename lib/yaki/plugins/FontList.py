#!/usr/bin/env python
# encoding: utf-8
"""
FontList.py

Created by Rui Carmo on 2011-04-27
Published under the MIT license.
"""

import yaki.Engine, yaki.Store, yaki.Locale
from yaki.Utils import *
from BeautifulSoup import *
import os, re, glob, urlparse

template = """
<div style="float:left;" class="quicklook_holder"%(align)s><a title="%(title)s" href="%(large)s" class="quicklook"><img alt="%(alt)s" title="%(alt)s" src="%(small)s" class="thumb"></a></div>
"""

class FontListWikiPlugin(yaki.Plugins.WikiPlugin):
  def __init__(self, registry, webapp):
    self.webapp = webapp
    registry.register('markup', self, 'plugin','fonts')
    self.ac = webapp.getContext() 
    self.i18n = yaki.Locale.i18n[self.ac.locale]

  def run(self, serial, tag, tagname, pagename, soup, request, response):  
    params = {'serial':serial,'align':''}
      
    try:
      pattern = os.path.basename(tag['src'])
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
    
    items = []
    attachments = self.ac.store.getAttachments(pagename, pattern)
    if not len(attachments):
      print "Missing attachments %s in %s" % (pattern, pagename)
      return True
    c = self.webapp.getContext()
    for a in attachments:
      params['large'] = c.fontpreview + pagename + "/" + a
      params['small'] = c.thumb + pagename + "/" + a
      params['alt'] = a + ' ' + self.i18n['quicklook_click_to_zoom']
      items.append(template % params)
    tag.replaceWith(''.join(items))
    # No further processing is required
    return False
     
    
    
