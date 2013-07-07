# Module placeholder

import os, sys, logging, gettext

log = logging.getLogger()

from .store import Store
from .core import Singleton
from .plugins import plugin, Registry

# TODO: implement these

from .mocks import Index

# Initialize localizations

gettext.bindtextdomain('yaki', os.path.join(os.path.dirname(__file__), 'locale'))
gettext.textdomain('yaki')
