#!/usr/bin/env python
# encoding: utf-8
"""
IncludeFile.py

Created by Rui Carmo on 2011-03-27.
Published under the MIT license.
"""

import yaki.Engine, yaki.Store, yaki.Locale
from yaki.Utils import renderMarkup
import urlparse, re, cgi, os
from BeautifulSoup import *


class MarkupWikiPlugin(yaki.Plugins.WikiPlugin):
  def __init__(self, registry, webapp):
    registry.register('markup',self, 'plugin','markup')
    self.registry = registry
    self.ac = webapp.getContext()
    self.i18n = yaki.Locale.i18n[self.ac.locale]
  
  def run(self, serial, tag, tagname, pagename, soup, request, response):
    try:
      markup = tag['syntax']
    except KeyError:
      markup = u'text/html'
    try:
      source = tag['src']
      (schema,host,path,parameters,query,fragment) = urlparse.urlparse(source)
      if schema == 'cid' or self.ac.store.isAttachment(pagename,path):
        filename = self.ac.store.getAttachmentFilename(pagename,path)
        if os.path.exists(filename):
          raw = codecs.open(filename,'r','utf-8').read().strip()
        else:
          tag.replaceWith(self.i18n['error_include_file'])
          return False
      else:
        tag.replaceWith(self.i18n['error_reference_format'])
        return False
    except KeyError:
      raw = (u''.join(tag.findAll(text=re.compile('.+')))).strip('\r\n\t ')
      
    try:
      spoon = BeautifulSoup('<div class="include">%s</div>' % renderMarkup(raw,markup))
      self.registry.runForAllTags(pagename, spoon, request, response)
      tag.replaceWith(spoon)
    except:
      tag.replaceWith(self.i18n['error_markup_format'])
    return False
  
