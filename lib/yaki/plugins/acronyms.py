#!/usr/bin/env python
# encoding: utf-8
"""
acronyms.py

Created by Rui Carmo on 2007-01-11.
Published under the MIT license.
"""

import os, sys, logging

log = logging.getLogger()

import urlparse, re, time
from bs4 import BeautifulSoup, SoupStrainer
from yaki import Store, plugin
from utils.core import Singleton

meta_page = 'meta/Acronyms'


@plugin
class Acronyms:
    __metaclass__ = Singleton

    category  = 'markup'
    tags      = ['span','caps']
    meta_page = 'meta/Acronyms'
    mtime     = 0

    def __init__(self):
        log.debug(self)

    def load(self):
        s = Store()
        try:
            page = s.get_page(self.meta_page)
        except:
            log.warn("no %s definitions" % meta_page)
            return

        # prepare to parse only <pre> tags (so that we can have multiple maps organized by sections)
        soup = BeautifulSoup(render_markup(page['data'],page['content-type']))
        h = HTMLParser.HTMLParser()

        all_sections = u''.join(map(lambda t: str(t.string), soup.find_all('pre'))).strip()
        # now that we have the full map, let's build the schema hash

        for line in all_sections.split('\n'):
            try:
                (acronym, expansion) = line.split(' ',1)
                self.acronyms[acronym.lower()] = expansion
            except ValueError: # skip lines with more than two fields
                log.warn("skipping line '%s'" % line)
                pass
    
    
    def run(self, serial, tag, tagname, pagename, soup, request, response):
        try:
            acronym = ''.join(tag.find_all(text=re.compile('.+')))
        except:
            return True
        acronym = acronym.lower()
        if acronym in self.acronyms.keys():
            meaning = self.acronyms[acronym]
            tag['title'] = meaning
            # this tag does not need to be re-processed
            return False
        return True
