#!/usr/bin/env python
# encoding: utf-8
"""
Main Yaki module

Created by Rui Carmo on 2013-06-10.
Published under the MIT license.
"""

import os, sys, logging, gettext

log = logging.getLogger()

from .store import Store
from .plugins import plugin, Registry
from .core import render_markup

# TODO: implement these

from .mocks import Index

# Initialize translations

english = gettext.translation('yaki', os.path.join(os.path.dirname(__file__), 'locale'), languages=['en'])
english.install()
log.info(_('translation_applied'))
