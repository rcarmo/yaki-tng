import os, sys, logging

log = logging.getLogger()

import functools

from yaki.utils import render_markup

def render():
    """Render markup inside a wiki store result"""

    def decorator(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            page = callback(*args, **kwargs)
            page['data'] = render_markup(page['data'],page['headers']['content-type'])

            # TODO: normalize links, run plugins, etc.
            
            return page
        return wrapper
    return decorator
