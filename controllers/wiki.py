#!/usr/bin/env python
# encoding: utf-8
"""
wiki.py

Created by Rui Carmo on 2013-12-10.
Published under the MIT license.
"""

import os, sys, logging

log = logging.getLogger()

from yaki import Store
from yaki.constants import *
from redis import StrictRedis as Redis
from difflib import get_close_matches

class WikiController(object):

    def __init__(self, settings):
        """Initialize the controler and preload basic metadata"""

    	self.redis = Redis(host=settings.redis.bind_address, port=settings.redis.port)
    	self.store = Store(settings.content.path)
        self.get_all_pages()   # page modification times
        self.get_all_aliases() # page aliases


    def get_page(self, path):
        """Returns a single page"""

        if path in self.store.pages:
            return self.store.get_page(path)
        raise KeyError


    def resolve_alias(self, path):
        """Attempts to resolve an alias to a page"""

        # Check locally first, to save overhead
        if path in self.store.aliases:
            return self.store.aliases[path]

        # Check if there's been an update in Redis
        alias = self.redis.hget(META_ALIASES, path)
        if alias:
            self.store.aliases[path] = alias
            return alias
        
        return None


    def get_all_pages(self):
        """Returns a hash of all known pages and mtimes"""

        if not len(self.store.pages):
            if self.redis.exists(META_PAGES):
                self.store.pages = self.redis.hgetall(META_PAGES)
            else:
                # force filesystem scan and alias generation
                pages = self.store.get_all_pages()
                log.debug(pages)
                self.redis.hmset(META_PAGES,self.store.get_all_pages())
        return self.store.pages


    def get_all_aliases(self):
        """Returns a hash of all known page aliases"""

        if not len(self.store.aliases):
            if self.redis.exists(META_ALIASES):
                self.store.aliases = self.redis.hgetall(META_ALIASES)
            else:
                # force filesystem scan and alias generation
                self.store.get_all_pages()
                self.redis.hmset(META_ALIASES, self.store.aliases)
        return self.store.aliases


    def get_close_matches_for_page(self, path):
        """Get a list of close matches for a given page/path"""

        pages = self.get_all_pages()
        return get_close_matches(path, pages.keys())




