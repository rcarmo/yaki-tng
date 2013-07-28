#!/usr/bin/env python
# encoding: utf-8
"""
Reformat custom schemas as references to exernal Wikis/sites

Created by Rui Carmo on 2007-01-11.
Published under the MIT license.
"""

import os, sys, logging

log = logging.getLogger()

import urlparse, re, time
from bs4 import BeautifulSoup
from yaki import Index, Store, plugin, render_markup
from utils.core import Singleton
from utils.timekit import time_since
import HTMLParser

@plugin
class InterWiki:
    __metaclass__ = Singleton

    category = 'markup'
    tags     = ['a']
    wiki_map = 'meta/InterWikiMap'
    schemas  = {}
    mtime    = 0


    def __init__(self):
        log.debug(self)


    def load(self):
        # load InterWikiMap
        s = Store()
        try:
            page = s.get_page(self.wiki_map)
        except:
            log.warn("InterWikiMap: no %s definitions" % self.wiki_map)
            return

        # prepare to parse only <pre> tags (so that we can have multiple maps organized by sections)
        soup = BeautifulSoup(render_markup(page['data'],page['content-type']))
        h = HTMLParser.HTMLParser()

        all_sections = u''.join(map(lambda t: str(t.string), soup.find_all('pre'))).strip()
        # now that we have the full map, let's build the schema hash
        for line in all_sections.split('\n'):
            try:
                (schema, url) = line.strip().split(' ',1)
                self.schemas[schema.lower()] = h.unescape(url) #url.replace("&amp;","&")
            except ValueError:
                log.warn("skipping line '%s'" % line)
                pass
        self.mtime = time.time()
    

    def run(self, serial, tag, tagname, pagename, soup, request, response):
        s = Store()
        if (self.mtime < s.mtime(self.wiki_map)):
            self.load()

        try:
            uri = tag['href']
        except KeyError:
            return True
        try:      
            (schema, link) = uri.split(':',1)
        except ValueError:
            return False

        schema = schema.lower()
        tag['rel'] = uri

        if schema in self.schemas.keys():
            if '%s' in self.schemas[schema]:
                try:
                    uri = self.schemas[schema] % link
                except:
                    print "Error in processing Interwiki link (%s,%s,%s)" % (schema, link, self.schemas[schema])
                    uri = self.schemas[schema] + link
            else:
                uri = self.schemas[schema] + link
            tag['href'] = uri
            (schema,netloc,path,parameters,query,fragment) = urlparse.urlparse(uri)
            tag['title'] = "link to %s on %s" % (link, netloc)
            tag['class'] = "interwiki"
            # this tag does not need to be re-processed
            return False
