#!/usr/bin/env python
# encoding: utf-8
"""
Replace aliases in links

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
class Aliases:
    __metaclass__ = Singleton

    category  = 'markup'
    tags      = ['a']
    meta_page = 'meta/Aliases'
    aliases   = {}
    mtime     = 0


    def __init__(self):
        log.debug(self)


    def load(self):
        # load Aliases
        s = Store()
        try:
            page = s.get_page(self.meta_page)
        except:
            log.warn("Aliases: no %s definitions" % self.meta_page)
            return

        # prepare to parse only <pre> tags (so that we can have multiple maps organized by sections)
        soup = BeautifulSoup(render_markup(page['data'],page['content-type']))
        h = HTMLParser.HTMLParser()

        all_sections = u''.join(map(lambda t: str(t.string), soup.find_all('pre'))).strip()
        # now that we have the full map, let's build the schema hash
        for line in all_sections.split('\n'):
            try:
                (link, replacement) = line.strip().split(' ',1)
                self.aliases[link] = replacement
                self.aliases[link.replace('_',' ')] = replacement
            except ValueError:
                log.warn("skipping line '%s'" % line)
                pass
        self.mtime = time.time()
    

    def run(self, serial, tag, tagname, pagename, soup, request, response):
        s = Store()
        if (self.mtime < s.mtime(self.meta_page)):
            self.load()

        try:
            link = tag['href']
        except KeyError:
            return True

        while True: # expand multiple aliases if required
            stack = [] # avoid loops
            try:
                alias = self.aliases[tag['href']]
                if alias not in stack:
                    stack.append(alias)
                    tag['href'] = alias
                else: # avoid loops
                    break
            except:
                break
        # this tag may need to be re-processed by another plugin
        return True
