#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Indexer daemon

Created by: Rui Carmo
"""

try:
    from gevent import monkey; monkey.patch_all()
except:
    print "Could not load gevent, proceeding."

import os, sys, logging, logging.config

# Make sure our bundled libraries take precedence
for f in ['lib','controllers']:
    sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),f))

import bottle
from config import settings

log = logging.getLogger()

if __name__ == "__main__":

    if settings.indexer.reloader:
        if 'BOTTLE_CHILD' not in os.environ:
            log.debug('Using reloader, spawning first child.')
        else:
            log.debug('Child spawned.')

    if not settings.indexer.reloader or ('BOTTLE_CHILD' in os.environ):
        log.info("Setting up application.")
        from routes import solr
        log.info("Serving requests.")

    bottle.run(
        port     = settings.indexer.http.port,
        host     = settings.indexer.http.bind_address,
        debug    = settings.debug,
        reloader = settings.reloader
    )
