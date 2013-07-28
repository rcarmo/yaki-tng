#!/usr/bin/env python
# encoding: utf-8
"""
Miscellaneous utility functions

Created by Rui Carmo on 2006-09-10.
Published under the MIT license.
"""

import math, time, datetime, calendar, unittest
import os, sys, re, binascii, fnmatch, xmlrpclib, cgi, htmlentitydefs, struct
import cStringIO as StringIO


def sanitize_title(title):
  return re.sub("[\W+]","-",title.lower())


def render_markup(raw, markup=u'text/html'):
    # Allow module to load regardless of textile or markdown support
    try:
        import textile
        import smartypants
        import markdown
    except ImportError:
        pass

    def _markdown(raw):
        return markdown.Markdown(extensions=['extra','toc','smartypants','codehilite','meta','sane_lists'], safe_mode=False).convert(raw)

    def _plaintext(raw):
        return u'<pre>\n%s</pre>' % raw

    def _textile(raw):
        return smartypants.smartyPants(textile.textile(unicode(raw), head_offset=0, validate=0, sanitize=1, encoding='utf-8', output='utf-8'))

    def _html(raw):
        return raw
    
    return {
        u'text/plain'         : _plaintext,
        u'text/x-web-markdown': _markdown,
        u'text/x-markdown'    : _markdown,
        u'text/markdown'      : _markdown,
        u'text/textile'       : _textile,
        u'text/x-textile'     : _textile,
        u'text/html'          : _html}[markup](raw)
        
