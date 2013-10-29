#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: et:ts=4:sw=4:
"""
Main application script

Created by: Rui Carmo
License: MIT (see LICENSE.md for details)
"""

import os, sys, json, logging, logging.config

# Make sure our bundled libraries take precedence
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'lib'))

import utils, bottle
import miniredis.client, miniredis.server
from config import settings

log = logging.getLogger()

if __name__ == "__main__":

    if settings.reloader:
        if "BOTTLE_CHILD" not in os.environ:
            log.debug("Using reloader, spawning first child.")
        else:
            log.debug("Child spawned.")

    # Launch our bundled Redis server
    if settings.miniredis and "BOTTLE_CHILD" not in os.environ:
        try:
            client = miniredis.client.RedisClient()
            log.debug("Connected to Redis")
        except Exception, e:
            log.debug("Spawning Redis")
            miniredis.server.fork(settings.redis)

    # Bind routes
    if not settings.reloader or ("BOTTLE_CHILD" in os.environ):
        log.info("Setting up application.")
        import api, routes, controllers
        log.info("Serving requests.")

    bottle.run(
        port     = settings.http.port, 
        host     = settings.http.bind_address, 
        debug    = settings.debug,
        reloader = settings.reloader
    )
