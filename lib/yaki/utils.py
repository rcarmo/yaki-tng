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
import yaki.Locale


#
# Wild Wild Web
#

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
        return markdown.Markdown(extensions=['extra','toc','smartypants'], safe_mode=False).convert(raw)

    def _plaintext(raw):
        return u'<pre>\n%s</pre>' % raw

    def _textile(raw):
        return smartypants.smartyPants(textile.textile(unicode(raw), head_offset=0, validate=0, sanitize=1, encoding='utf-8', output='utf-8'))

    def _html(raw):
        return raw
    
    return {
        u'text/plain': _plaintext,
        u'text/x-web-markdown': _markdown,
        u'text/x-markdown': _markdown,
        u'text/markdown': _markdown,
        u'text/textile': _textile,
        u'text/x-textile': _textile,
        u'text/html': _html}[markup](raw)
    

def getImageInfo(data):
    data = str(data)
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    # handle GIFs
    if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack("<HH", data[6:10])
        width = int(w)
        height = int(h)

    # See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
          and (data[12:16] == 'IHDR')):
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)

    # Maybe this is for an older PNG version.
    elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
        # Check to see if we have the right content type
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[8:16])
        width = int(w)
        height = int(h)

    # Check for a JPEG
    elif (size >= 4):                                                          
        jpeg = StringIO.StringIO(data)                                         
        b = jpeg.read(4)                                                       
        if b.startswith('\xff\xd8\xff\xe0'):                                   
            content_type = 'image/jpeg'                                        
            bs = jpeg.tell()                                                   
            b = jpeg.read(2)                                                   
            bl = (ord(b[0]) << 8) + ord(b[1])                                  
            b = jpeg.read(4)                                                   
            if b.startswith("JFIF"):                                           
                bs += bl                                                       
                while(bs < len(data)):                                         
                    jpeg.seek(bs)                                              
                    b = jpeg.read(4)                                           
                    bl = (ord(b[2]) << 8) + ord(b[3])                          
                    if bl >= 7 and b[0] == '\xff' and b[1] == '\xc0':          
                        jpeg.read(1)                                           
                        b = jpeg.read(4)                                       
                        height = (ord(b[0]) << 8) + ord(b[1])                  
                        width = (ord(b[2]) << 8) + ord(b[3])                   
                        break                                                  
                    bs = bs + bl + 2      
    return width, height, content_type                                         

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
