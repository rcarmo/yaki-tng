#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API calls for users

Created by: Rui Carmo
"""

import os, sys, logging, json

log = logging.getLogger()

from bottle import route, get, put, post, delete, request, response, abort
import api

from decorators import timed, jsonp, cache_results, cache_control

# local context
prefix = api.prefix + '/pages'

# Collection URI - List
@get(prefix)
@timed
@cache_results(30)
@cache_control(300)
@jsonp
def list_pages():
    pass