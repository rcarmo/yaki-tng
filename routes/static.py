#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, os.path, sys, logging
from bottle import app, route, redirect, static_file, view

from utils import path_for
from config import settings
from decorators import timed, cache_control

log = logging.getLogger()


@route('/')
def index():
    redirect(os.path.join(settings.wiki.base, settings.wiki.home))

@route('/static/<filepath:path>')
@timed
@cache_control(settings.cache.cache_control)
def static(filepath):
    """Handles all the remanining static files"""
    return static_file(filepath, root=path_for(os.path.join('themes',settings.theme,'static')))

