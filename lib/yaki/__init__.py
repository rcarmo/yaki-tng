#!/usr/bin/env python
# encoding: utf-8
"""
Main Yaki module

Created by Rui Carmo on 2013-06-10.
Published under the MIT license.
"""

import os, sys, logging, gettext, msgfmt

log = logging.getLogger()

from .store import Store
from .core import Singleton
from .plugins import plugin, Registry
from .utils import render_markup

# TODO: implement these

from .mocks import Index

# Initialize localizations

try: 
	english = gettext.translation('yaki', os.path.join(os.path.dirname(__file__), 'locale'), languages=['en'])
	english.install()
	log.debug(_('Localizations Installed'))

except IOError as err:
		try:
			for r,d,f in os.walk(os.path.join(os.path.dirname(__file__), 'locale')):
				for files in f:
					if files.endswith(".po"):
						msgfmt.make(os.path.join(r,files), None)
						log.info('One time only building of localizations complete')
			english = gettext.translation('yaki', os.path.join(os.path.dirname(__file__), 'locale'), languages=['en'])
			english.install()
			log.debug(_('Localizations Installed'))
		except:
			raise err
