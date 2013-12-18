#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: et, ts=4, sw=4

import os, sys, logging

log = logging.getLogger()

import functools
from bottle import request, response
from bs4 import BeautifulSoup

from yaki import render_markup, Registry

plugins = Registry()

def render():
    """Render markup inside a wiki store result"""

    def decorator(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            
            page = callback(*args, **kwargs)
            page['data'] = BeautifulSoup(render_markup(page['data'],page['content-type']))
            plugins.apply_all(kwargs['page'], page['data'], request=request, response=response, indexing=False)

            # TODO: normalize links, run specific plugins, etc.
            
            return page
        return wrapper
    return decorator
