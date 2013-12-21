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

from decorators import timed, redis_cache, cache_control, cache_results

from redis import StrictRedis as Redis

r = Redis()

@route('/')
@route(settings.wiki.base)
def root():
    log.debug(settings)
    redirect(settings.content.homepage)


@route(settings.wiki.base + '/<page:path>')
@timed
@cache_results(settings.cache.worker_timeout)
@redis_cache(r, 'html', settings.cache.redis_timeout)
@cache_control(settings.cache.cache_control)
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
@cache_control(settings.cache.cache_control)
def media_asset(item):
    """Return page attachments"""

    return static_file(item, root=path_for(settings.content.path))
