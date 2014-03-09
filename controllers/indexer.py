#!/usr/bin/env python
# encoding: utf-8
"""
Indexer.py

Created by Rui Carmo on 2007-02-19.
Published under the MIT license.
"""

import os, errno, time, gc, difflib, urllib, urlparse
import logging
from collections import defaultdict

log = logging.getLogger()

import utils

from bs4 import BeautifulSoup
from whoosh import index
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED, DATETIME
from whoosh.analysis import StemmingAnalyzer, KeywordAnalyzer
from whoosh.query import Query, And, Or, Term, FuzzyTerm, Not, Regex, TermRange, DateRange, Every
from whoosh.qparser import QueryParser
from whoosh.writing import AsyncWriter
from whoosh.sorting import ScoreFacet, MultiFacet, FieldFacet


class Indexer():

    def __init__(self, config, queue):
        """Setup environment"""
        self.indexpath = config.storage.path
        self.started = time.time()
    
        try:
            os.makedirs(self.indexpath)
        except OSError, e: # it already exists
            if e.errno == errno.EEXIST:
                log.info('Index folder already exists.')
            pass

        self.schema = Schema(
            name     = ID(stored=True,unique=True),                     # page name/path
            title    = TEXT(stored=True,analyzer=StemmingAnalyzer()),   # title
            body     = TEXT(stored=True,analyzer=StemmingAnalyzer()),   # plaintext
            wiki     = KEYWORD(lowercase=True, commas=True),            # wiki links
            link     = KEYWORD(commas=True),                            # other links
            date     = DATETIME(stored=True),                           # creation date
            modified = DATETIME(stored=True),                           # modification date
            tags     = KEYWORD(stored=True,lowercase=True, commas=True) # tags
        )
        
        try:
            log.debug("Opening existing index")
            self.whoosh = index.open_dir(self.indexpath)
        except Exception, e:
            log.debug("Could not open existing index: %s" % e)   
            log.debug("Creating new index")
            self.whoosh = index.create_in(self.indexpath, self.schema)
        self.writer = AsyncWriter(self.whoosh)
        self.searcher = self.whoosh.searcher()


    def delete(self, to_delete):
        for name in to_delete:
            self.whoosh.delete_by_term('name',name)

    def add(self, doc):
        """Index a single document. We assume we'll be getting plaintext throughout."""
        
        kwargs = defaultdict(None)
        kwargs.update(doc)
        kwargs['date']     = datetime.datetime(doc['date'])
        kwargs['modified'] = datetime.datetime(doc['modified'])
        self.writer.update_document(**kwargs)

    def search(self, query, limit=40, field='body'):
        """Query the index"""
        try:
            s = self.searcher
            qp = QueryParser('title', schema=self.schema) # search title first
            q = qp.parse(query)
            r = s.search(q,limit=limit)

            qp = QueryParser('tags', schema=self.schema) # then the tags
            q = qp.parse(query)
            r.upgrade_and_extend(s.search(q,limit=limit))

            qp = QueryParser(field, schema=self.schema) # then the body
            q = qp.parse(query)
            sc = MultiFacet([ScoreFacet(),FieldFacet("modified", reverse=True)])
            r.upgrade_and_extend(s.search(q,limit=limit, sortedby = sc))
        except Exception, e:
            print "ERROR in search: %s" % query, locals()
            r = None
        return [hit for hit in r]
