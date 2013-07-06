#!/usr/bin/env python
# encoding: utf-8
"""
ZipStore.py

Content store encapsulation (currently one folder per page with an index document)

Created by Rui Carmo on 2010-08-21.
Published under the MIT license.
"""

import os, stat, glob, codecs, zipfile
import rfc822 # for basic parsing
from yaki.Page import Page
from yaki.Utils import *

BASE_TYPES={
  "txt": "text/plain",
  "html": "text/html",
  "htm": "text/html",
  "markdown": "text/x-markdown",
  "textile": "text/x-textile"
}
BASE_FILENAMES=["index.%s" % x for x in BASE_TYPES.keys()]
BASE_PAGE = """From: %(author)s
Date: %(date)s
Content-Type: %(markup)s
Content-Encoding: utf-8
Title: %(title)s
Keywords: %(keywords)s
Categories: %(categories)s
Tags: %(tags)s
%(_headers)s

%(content)s
"""

class Store:
  """
  Wiki Store - abstracts actual storage and versioning
  """

  def __init__(self,path="space"):
    """
    Constructor
    """
    self.path = path
    self.pages={}
    self.aliases={}
    self.dates={}
  
  def getPath(self,pagename):
    """
    Append the store path to the pagename
    """
    return os.path.join(self.path, pagename)
  
  def get(self, vpath, handle = False, folders = True):
    """ TODO: refactor this to separate get mtime from file access """
    realpath = os.path.join(self.path, vpath)
    # check standard files first
    if(os.path.exists(realpath)):
      if handle:
        return codecs.open(realpath,'r','utf-8')
      else:
        return os.stat(realpath)[stat.ST_MTIME]
    # now look for ZIP files
    base = ''
    pieces = vpath.split(os.sep)
    for i in range(len(pieces)):
      base = os.path.join(base, pieces[i])
      # FAILS WHEN INVOKED WITH A SINGLE MISSING FILENAME
      realpath = os.path.join(self.path, base)
      if not os.path.exists(realpath):
        return None
      for entry in os.listdir(realpath):
        (dummy, ext) = os.path.splitext(entry)
        if ext.lower() == '.zip':
          z = zipfile.ZipFile(os.path.join(self.path, base, entry))
          # check for folder mtimes first
          if not handle and folders and (os.path.splitext(vpath)[1] == ''):
            try:
              # probably the weirdest time trick ever
              return time.mktime(datetime.datetime(*(z.getinfo(os.sep.join(pieces[i:]) + os.sep).date_time)).timetuple())
            except:
              pass
          for name in z.namelist():
            # TODO: remove trailing os.sep
            print "get", vpath, base, name, os.path.join(base,name)
            if vpath == os.path.join(base,name):
              if getHandle:
                return codecs.EncodedFile(z.open(name),'utf-8')
              else:
                return time.mktime(datetime.datetime(*(z.getinfo(name).date_time)).timetuple())
    return None
  
  def date(self, pagename):
    """
    Retrieve a page's stored date (or fall back to mtime)
    """
    if pagename in self.dates.keys():
      return self.dates[pagename]
    else:
      return self.get(pagename)

  def mtime(self, pagename):
    """
    Retrieve modification time for the current revision of a given page by checking the folder's mtime (to account for changed attachments), or None if the folder does not exist.
    """
    realpath = os.path.join(self.path, pagename)
    # check standard files first
    if(os.path.exists(realpath)):
      return os.stat(realpath)[stat.ST_MTIME]
    # now look for ZIP files
    vpath = ''
    pieces = realpath.split(os.sep)
    realpath = realpath + "/"
    for i in range(len(pieces)):
      vpath = os.path.join(self.path, vpath, pieces[i])
      for entry in os.listdir(vpath):
        (dummy, ext) = os.path.splitext(entry)
        if ext.lower() == '.zip':
          z = zipfile.ZipFile(os.path.join(vpath, entry))
          # check inside this zip file for a matching path
          # (paths are stored with a trailing slash)
          for name in z.namelist():
            if os.path.join(vpath, name) == realpath:
              return time.mktime(datetime.datetime(*(z.getinfo(name).date_time)).timetuple())
    return None

  def getAttachments(self, pagename, pattern = '*'):
    targetpath = self.getPath(pagename) 
    attachments = glob.glob(os.path.join(targetpath,pattern))
    attachments = map(os.path.basename,filter(lambda x: not os.path.isdir(x), attachments))
    return attachments
  
  def isAttachment(self, pagename, attachment):
    """
    Checks it a given filename is actually attached to a page
    """
    targetpath = self.getPath(pagename)
    attachment = os.path.join(targetpath,attachment)
    try:
      if attachment and os.path.exists(attachment) and not os.path.isdir(attachment):
        return True
    except:
      print "ERROR: bad attachment in %s" % pagename
    return False

  def getAttachmentFilename(self, pagename, attachment):
    """
    Returns the filename for an attachment
    """
    targetpath = self.getPath(pagename)
    targetfile = os.path.join(targetpath,attachment)
    return targetfile
  
  def getRevision(self, pagename, revision = None):
    """
    Retrieve the specified revision from the store.
    
    At this point we ignore the revision argument
    (versioning will be added at a later date, if ever)
    """
    targetpath = self.getPath(pagename)
    # check that folder exists
    mtime = self.mtime(pagename)
    if mtime != None:
      # figure out which is the base document
      for base in BASE_FILENAMES:
        mtime = self.get(os.path.join(pagename,base))
        if mtime:
          break
      try:
        h = self.get(os.path.join(pagename,base),True)
        buffer = h.read()
        h.close()
        p = Page(buffer,BASE_TYPES[base.split('.',1)[1]])
  
        # If the page has no title header, use the path name
        if 'title' not in p.headers.keys():
          p.headers['title'] = pagename
        p.headers['name'] = pagename
        
        # Now try to supply a sensible set of dates
        try:
          # try parsing the date header
          p.headers['date'] = parseDate(p.headers['date'])
        except:
          # if there's no date header, use the file's modification time
          # (if only to avoid throwing an exception again)
          p.headers['date'] = mtime
          pass
        # Never rely on the file modification time for last-modified
        # (otherwise SVN, Unison, etc play havoc with modification dates)
        try:
          p.headers['last-modified'] = parseDate(p.headers['last-modified'])
        except:
          p.headers['last-modified'] = p.headers['date']
          pass
        self.dates[pagename] = p.headers['date']
        return p
      except IOError:
        raise IOError, "Couldn't find page %s." % (pagename)
    else:
       raise IOError, "Couldn't find page %s." % (pagename)
    return None
  
  def allPages(self):
    """
    Enumerate all pages and their last modification time

    Assumes root is _not_ a ZIP file
    """
    for folder, subfolders, files in os.walk(self.path):
      # Skip common SCM subfolders
      for i in ['CVS', '.hg', '.svn', '.git', '.AppleDouble']:
        if i in subfolders:
          subfolders.remove(i)
      for entry in files:
        (dummy, ext) = os.path.splitext(entry)
        if ext.lower() == '.zip':
          z = zipfile.ZipFile(os.path.join(folder,entry))
          for f in z.namelist():
            (path, name) = os.path.split(f)
            # Skip OSX resources
            if '__MACOSX' in path:
                continue
            if name in BASE_FILENAMES:
              #print f, os.path.join(folder[len(self.path)+1:], path)
              #self.pages[os.path.join(folder[len(self.path)+1:])] = time.mktime(datetime.datetime(*(z.getinfo(f).date_time)).timetuple())
              self.pages[path] = time.mktime(datetime.datetime(*(z.getinfo(f).date_time)).timetuple())
      for base in BASE_FILENAMES:
        if( base in files ):
          # Check for modification date of markup file only
          mtime = os.stat(os.path.join(folder,base))[stat.ST_MTIME]
          # Add each path (removing the self.path prefix)
          self.pages[folder[len(self.path)+1:]] = mtime
 
    for name in self.pages.keys():
      base = os.path.basename(name).lower()
      if base in self.aliases.keys():
        if len(self.aliases[base]) > len(name):
          self.aliases[base] = name
      else:
        self.aliases[base] = name        
      for replacement in ALIASING_CHARS:
        alias = name.lower().replace(' ',replacement)
        self.aliases[alias] = name
    return self.pages
  
  def updatePage(self, pagename, fields, base = "index.txt"):
    """
    Updates a given page, inserting a neutral text file by default
    """
    targetpath = self.getPath(pagename)
    if(not os.path.exists(targetpath)):
      os.makedirs(targetpath)
    filename = os.path.join(targetpath,base) 
    try:
      h = open(filename, "wb")
      h.write((BASE_PAGE % fields).encode('utf-8'))
      h.close()
    except IOError:
      return None
    return True
  
  def addAttachment(self, pagename, filename, newbasename = None):
    targetpath = self.getPath(pagename)
    if(not os.path.exists(targetpath)):
      os.makedirs(targetpath)
    if newbasename:
      os.rename(filename,os.path.join(targetpath,newbasename))
    else:
      os.rename(filename,os.path.join(targetpath,os.path.basename(filename)))

#=================================

if __name__=="__main__":
  print "Initializing test store."
  s = Store('../../../space/blog')
  print filter(lambda x, y: "2007" in x,s.allPages().iteritems()) 
