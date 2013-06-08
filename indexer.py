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

import utils, bottle, config

# read configuration file
config.indexer = utils.get_config(os.path.join(utils.path_for('etc',__file__),'indexer.json'))

# Set up logging
logging.config.dictConfig(dict(config.indexer.logging))

log = logging.getLogger()

if __name__ == "__main__":

    if config.indexer.reloader:
        if 'BOTTLE_CHILD' not in os.environ:
            log.debug('Using reloader, spawning first child.')
        else:
            log.debug('Child spawned.')

    if not config.indexer.reloader or ('BOTTLE_CHILD' in os.environ):
        log.info("Setting up application.")
        from routes import solr
        log.info("Serving requests.")

    bottle.run(
        port     = config.indexer.http.port,
        host     = config.indexer.http.bind_address,
        debug    = config.indexer.debug,
        reloader = config.indexer.reloader,
        server   = config.indexer.server
    )
