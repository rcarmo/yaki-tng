#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: et:ts=4:sw=4

import os, os.path, sys, logging

log = logging.getLogger()

import functools, urlparse
from bottle import request, response
from bs4 import BeautifulSoup

from yaki import render_markup, Registry
from utils.stringkit import munge_string

plugins = Registry()

def render(overrides = {}):
    """Render markup inside a wiki store result"""

    def decorator(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            
            page = callback(*args, **kwargs)
            log.warn(page['content-type'])
            if page['content-type'] in overrides:
                page['content-type'] = overrides[page['content-type']]
            log.warn(page['content-type'])

            page['data'] = BeautifulSoup(render_markup(page['data'],page['content-type']))
            plugins.apply_all(kwargs['page'], page['data'], request=request, response=response, indexing=False)

            # TODO: normalize links, run specific plugins, etc.

            # Normalize legacy keywords
            keywords = []
            for k in [u'keywords', u'tags']:
                if k in page['headers'].keys():
                    keywords.extend(page['headers'][k].split(','))
            page['headers']['keywords'] = ','.join(list(set([k.strip() for k in keywords])))

            # Inject any per-page CSS
            if u'css' not in page['headers'].keys():
                page['headers']['css'] = None

            # clean up requested URI
            page['headers']['url'] = urlparse.urlunparse(( request.urlparts.scheme, request.urlparts.netloc, os.path.abspath(request.urlparts.path), None, None, None ))
            page['headers']['permalink'] = page['headers']['url'] + "#%s" % munge_string(page['headers']['title'])
            return page
        return wrapper
    return decorator
