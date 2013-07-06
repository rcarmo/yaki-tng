import os, sys, logging

log = logging.getLogger()

import functools
from bottle import request, response
from bs4 import BeautifulSoup

from .utils import render_markup
from .store import Store
from .plugins import Registry

def render():
    """Render markup inside a wiki store result"""

    def decorator(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            
            r = Registry()
            page = callback(*args, **kwargs)
            page['data'] = BeautifulSoup(render_markup(page['data'],page['content-type']))
            r.apply_all(kwargs['page'], page['data'], request=request, response=response, indexing=False)

            # TODO: normalize links, run plugins, etc.
            
            return page
        return wrapper
    return decorator
