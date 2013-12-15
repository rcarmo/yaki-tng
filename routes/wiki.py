#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
wiki.py
"""

import os, sys, logging

log = logging.getLogger()

from bottle import route, redirect, view, static_file
from config import settings

from utils import path_for
from yaki import Store
from yaki.decorators import render

from decorators import timed, redis_cache, cache_control

from miniredis.client import RedisClient

r = RedisClient()

@route('/')
@route(settings.wiki.base)
def root():
    log.debug(settings)
    redirect(settings.content.homepage)


@route(settings.wiki.base + '/<page:path>')
@timed
@redis_cache(r, 'markup')
@view('wiki')
@render()
def wiki(page):
    """Render a wiki page"""

    s = Store(path_for(settings.content.path))
    try:
        result = s.get_page(page.lower())
    except Exception, e:
        log.warn("%s rendering page %s" % (e, page))
        result = s.get_page('meta/EmptyPage')
    return result
    

@route(settings.wiki.media + '/<item:path>')
@timed
def media_asset(item):
    """Return page attachments -- by default, we assume the raw markup is also up for grabs, although this may change later"""

    s = Store(path_for(settings.content.path))
    return static_file(item, root=s.get_path(settings.content.path))
