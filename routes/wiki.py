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


@route('/')
def root():
    log.debug(settings)
    redirect(settings.content.homepage)


@route('/space/<page:path>')
#@view('wiki')
def wiki(page):
    s = Store(path_for(settings.content.path))
    try:
        result = s.get_page(page.lower())
    except:
        result = s.get_page('meta/EmptyPage')

    log.debug(result)
    return result