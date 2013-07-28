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


def do_pings(siteinfo):
  try:
    for target in siteinfo['ping']:
      if target == 'technorati':
        print "Pinging Technorati..."
        server = xmlrpclib.Server('http://rpc.technorati.com/rpc/ping')
        print server.weblogUpdates.ping(siteinfo['sitetitle'], siteinfo['ping'][target])
  except:
    pass


def makeUnique(seq, transform=None):  
  # order preserving 
  if transform is None: 
    def transform(x): return x 
  seen = {} 
  result = [] 
  for item in seq: 
    marker = transform(item) 
    if marker not in seen:
      seen[marker] = 1
      result.append(item)
  return result
  

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
        

def walk(top, topdown=True, onerror=None, followlinks=False, ziparchive=None, zipdepth=0):
    """Reimplementation of os.walk to traverse ZIP files as well"""
    try:
        if (os.path.splitext(top)[1]).lower() == '.zip':
            if ziparchive:
                # skip nested ZIPs.
                yield top, [], []
            else:
                ziparchive = zipfile.ZipFile(top)
            names = list(set(map(lambda x: [p+'/' for p in x.split('/') if p != ""][zipdepth],ziparchive.namelist())))
        else:
            names = os.listdir(top)
    except error, err:
        if onerror is not None:
            onerror(err)
        return

    dirs, nondirs = [], []
    if ziparchive:
        for name in names:
            if name == '__MACOSX/':
                continue
            if name[-1::] == '/':
                dirs.append(name)
            else:
                nondirs.append(name)
    else:        
        for name in names:
            if os.path.isdir(os.path.join(top, name)):
                dirs.append(name)
            else:
                nondirs.append(name)
    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        new_path = os.path.join(top, name)
        if ziparchive:
            for x in walk(new_path, topdown, onerror, followlinks):
                yield x
        else:
            if followlinks or not islink(new_path):
                for x in walk(new_path, topdown, onerror, followlinks):
                    yield x
    if not topdown:
        yield top, dirs, nondirs

if __name__ == "__main__":
  import Locale
  print plainTime(Locale.i18n["en_US"],parseDate("2010-04-18 08:09:00"), True)
