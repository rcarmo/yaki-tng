#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, logging
from bottle import app, route, redirect, static_file, view

from utils import path_for
from config import settings

log = logging.getLogger()


@route('/')
def index():
    redirect(os.path.join(settings.wiki.base, settings.wiki.home))

@route('/static/<filepath:path>')
def static(filepath):
    """Handles all the remanining static files"""
    return static_file(filepath, root=path_for('static'))

