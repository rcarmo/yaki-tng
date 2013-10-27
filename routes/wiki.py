#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
wiki.py
"""

import os, sys, logging

log = logging.getLogger()

from bottle import route, redirect, view
from config import settings

from utils import path_for
from yaki import Store
from yaki.decorators import render

from decorators import timed, redis_cache, cache_control

from miniredis.client import RedisClient

r = RedisClient()

@route('/')
@route('/space')
def root():
    log.debug(settings)
    redirect(settings.content.homepage)


@route('/space/<page:path>')
@timed
@redis_cache(r, 'markup')
@view('wiki')
@render()
def wiki(page):
    s = Store(path_for(settings.content.path))
    try:
        result = s.get_page(page.lower())
    except Exception, e:
        log.warn("%s rendering page %s" % (e, page))
        result = s.get_page('meta/EmptyPage')

    return result
