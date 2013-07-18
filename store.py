#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main application script

Created by: Rui Carmo
"""

from gevent import monkey; monkey.patch_socket()
from gevent.server import StreamServer

import os, sys, json, logging, logging.config

# Make sure our bundled libraries take precedence
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'lib'))

import utils
from redis.server import RedisServer

# read configuration file
config = utils.get_config(os.path.join(utils.path_for('etc'),'store.json'))

# set up logging
logging.config.dictConfig(dict(config.logging))
log = logging.getLogger()

if __name__ == "__main__":
    s = RedisServer(config)
    try:
        if config.engine == "gevent":
            s.halt = False
            server = StreamServer((config.net.bind_address, config.net.port), s.gevent_handler)
            server.serve_forever()
        else:
            s.run()
    except KeyboardInterrupt:
        s.stop()

