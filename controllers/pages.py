#!/usr/bin/env python
# encoding: utf-8
"""
Pages.py

Created by Rui Carmo on 2007-02-19.
Published under the MIT license.
"""

import os, errno, time, gc, difflib, urllib, urlparse
import logging
from collections import defaultdict

log = logging.getLogger()

from yaki import Store
from config import settings

class Controller:
    def __init__(settings=settings):
    	