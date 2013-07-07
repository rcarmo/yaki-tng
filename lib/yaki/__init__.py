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
from .core import Singleton
from .plugins import plugin, Registry

# TODO: implement these

from .mocks import Index

# Initialize localizations

english = gettext.translation('yaki', os.path.join(os.path.dirname(__file__), 'locale'), languages=['en'])
english.install()
log.debug(_('Localizations Installed'))