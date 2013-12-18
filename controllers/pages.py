#!/usr/bin/env python
# encoding: utf-8
"""
Pages.py

Created by Rui Carmo on 2007-02-19.
Published under the MIT license.
"""

import os, sys, logging

log = logging.getLogger()

from yaki import Store
from config import settings
from miniredis.client import RedisClient

class Controller(object:
    def __init__(settings=settings):
    	self.redis = RedisClient(settings.redis.bind_address, settings.redis.port)
    	self.store = Store(settings.content.path)