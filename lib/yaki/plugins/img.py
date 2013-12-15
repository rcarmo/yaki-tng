#!/usr/bin/env python
# encoding: utf-8
"""
media.py

Created by Rui Carmo on 2007-01-11.
Published under the MIT license.
"""

import os, os.path, sys, logging, cgi, urlparse
from config import settings
from yaki import Index, Store, plugin
from utils.core import Singleton

log = logging.getLogger()

@plugin
class ImageWikiPlugin:
    __metaclass__ = Singleton

    category  = 'markup'
    tags      = ['img']


    def __init__(self):
        log.debug(self)


    def run(self, serial, tag, tagname, pagename, soup, request, response):
        try:
            uri = tag['src']
            schema, _, path, _, _, _ = urlparse.urlparse(uri)
        except Exception, e:
            log.debug(e)
            return True

        if schema: # TODO: deal with cid: schema
            return True
            
        s = Store()
        if s.is_attachment(pagename, path):
            tag['src'] = unicode(cgi.escape(os.path.join(settings.wiki.media, pagename, path)))
            return False # no further processing required
        return True
