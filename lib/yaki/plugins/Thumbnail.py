#!/usr/bin/env python
# encoding: utf-8
"""
Thumbnail.py

Created by Rui Carmo on 2010-12-27.
Published under the MIT license.
"""

import yaki.Engine, yaki.Store, yaki.Locale
from yaki.Utils import *
from BeautifulSoup import *
import os, re, urlparse

template = """<div class="quicklook_holder drop-shadow lifted"%(align)s%(style)s><a %(title)s href="%(large)s" class="quicklook"><img id="thumb%(serial)s" alt="%(large)s" src="%(src)s" class="thumb"></a></div>"""

class ThumbnailWikiPlugin(yaki.Plugins.WikiPlugin):
  def __init__(self, registry, webapp):
    self.webapp = webapp
    registry.register('markup', self, 'img','type')
    self.ac = webapp.getContext() 
    self.i18n = yaki.Locale.i18n[self.ac.locale]


  def run(self, serial, tag, tagname, pagename, soup, request, response):  
    params = {'serial':serial,'align':''}
    try:
      if tag['type'] != 'thumbnail':
        return True
    except:
      return True
      
    try:
      image = os.path.basename(tag['src'])
    except KeyError:
      print "Error in tag parameters for %s in %s" % (str(tag), pagename)
      return True

    for p in ['align','title','style']:
        try:
            params[p] = ' %s="%s"' % (p,tag[p])
        except KeyError:
            params[p] = ''
            pass
    
    if self.ac.store.isAttachment(pagename, image):
      c = self.webapp.getContext()
      params['large'] = c.media + pagename + "/" + image
      params['src'] = c.thumb + pagename + "/" + image
    else:
      print "Missing attachment %s in %s" % (image, pagename)
      return True

    params['alt'] = self.i18n['quicklook_click_to_zoom']
    tag.replaceWith(template % params)
    # No further processing is required
    return False
     
    
    
