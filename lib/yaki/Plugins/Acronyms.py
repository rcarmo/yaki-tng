#!/usr/bin/env python
# encoding: utf-8
"""
acronyms.py

Created by Rui Carmo on 2007-01-11.
Published under the MIT license.
"""

import os, sys, logging

log = logging.getLogger('plugins')

import urlparse, re
from bs4 import *

meta_page = 'meta/Acronyms'

class AcronymPlugin(yaki.plugins.Plugin):

    def __init__(self, registry, settings):
        registry.register('markup', self, 'span', 'caps')
        c = webapp.getContext()
        self.acronyms = {}
        # load Acronyms
        try:
            page = c.store.get_revision(meta_page)
        except:
            log.warn("no %s definitions" % meta_page)
            return

        # prepare to parse only <pre> tags in it (so that we can have multiple tables organized by sections)
        plaintext = SoupStrainer('pre', text=re.compile('.+'))
        map = ''.join([text for text in BeautifulSoup(page.render(), parseOnlyThese=plaintext)])
        # now that we have the full map, let's build the schema hash
        lines = map.split('\n')
        for line in lines:
            try:
                (acronym, expansion) = line.split(' ',1)
                self.acronyms[acronym.lower()] = expansion
            except ValueError: # skip lines with more than two fields
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
