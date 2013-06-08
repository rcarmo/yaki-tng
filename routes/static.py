#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, logging
from bottle import app, route, redirect, static_file, view

log = logging.getLogger()

@route('/')
def index():
    redirect("/space/HomePage")
    """Index page"""
    return static_file('index.html', root='static')

@route('<filepath:path>')
def static(filepath):
    """Handles all the remanining static files"""
    return static_file(filepath, root='static')

