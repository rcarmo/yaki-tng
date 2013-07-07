#!/usr/bin/env python
# encoding: utf-8
"""
Store.py

Content store encapsulation (currently one folder per page with an index document)

Created by Rui Carmo on 2006-11-12.
Published under the MIT license.
"""

import os, sys, logging
import stat, glob, codecs, shutil, rfc822
from .core import Singleton

BASE_TYPES={
    "txt"     : "text/plain",
    "html"    : "text/html",
    "htm"     : "text/html",
    "md"      : "text/x-markdown",
    "mkd"     : "text/x-markdown",
    "mkdn"    : "text/x-markdown",
    "markdown": "text/x-markdown",
    "textile" : "text/x-textile"
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

IGNORED_FOLDERS = ['CVS', '.hg', '.svn', '.git', '.AppleDouble']


def parse_page(buffer, mime_type='text/plain'):
    headers = {}
    markup  = ''
    if mime_type in ['text/plain', 'text/x-textile', 'text/x-markdown']:
      try:
        (header_lines,markup) = buffer.split("\n\n", 1)
        for header in header_lines.strip().split("\n"):
          (name, value) = header.strip().split(":", 1)
          headers[name.lower().strip()] = unicode(value.strip())
      except:
        raise TypeError, "Invalid page file format."
    return headers, markup, mime_type


class Store:
    """Wiki Store - abstracts file storage"""
    __metaclass__ = Singleton

    def __init__(self, path = None):
        """Constructor"""
        self.path    = path
        self.pages   = {}
        self.aliases = {}
        self.dates   = {}
        

    def get_path(self,pagename):
        """Append the store path to the pagename"""
        return os.path.join(self.path, pagename)
    

    def date(self, pagename):
        """
        Retrieve a page's stored date (or fall back to mtime)
        """
        if pagename in self.dates.keys():
            return self.dates[pagename]
        else:
            return self.mtime(pagename)


    def exists(self, pagename):
        """Verifies if a given page/path exists"""
        targetpath = self.get_path(pagename)
        return(os.path.exists(targetpath))


    def mtime(self, pagename):
        """
        Retrieve modification time for the current revision of a given page by checking the folder modification time.
        Assumes underlying OS/FS knows how to properly update mtime on a folder.
        """
        targetpath = self.get_path(pagename)
        if(os.path.exists(targetpath)):
            return os.stat(targetpath)[stat.ST_MTIME]
        return None

    
    def get_attachments(self, pagename, pattern = '*'):
        targetpath = self.get_path(pagename)
        attachments = glob.glob(os.path.join(targetpath,pattern))
        attachments = map(os.path.basename,filter(lambda x: not os.path.isdir(x), attachments))
        return attachments

                
    def is_attachment(self, pagename, attachment):
        """
        Checks if a given filename is actually attached to a page
        """
        targetpath = self.get_path(pagename)
        attachment = os.path.join(targetpath,attachment)
        try:
            if attachment and os.path.exists(attachment) and not os.path.isdir(attachment):
                return True
        except:
            print "ERROR: bad attachment in %s" % pagename
        return False


    def get_attachment_filename(self, pagename, attachment):
        """
        Returns the filename for an attachment
        """
        targetpath = self.get_path(pagename)
        targetfile = os.path.join(targetpath,attachment)
        return targetfile

    
    def get_page(self, pagename, revision = None):
        """
        Retrieve the specified revision from the store.
        
        At this point we ignore the revision argument
        (versioning will be added at a later date, if ever)
        """
        targetpath = self.get_path(pagename)
        mtime = self.mtime(pagename)
        if mtime != None:
            for base in BASE_FILENAMES:
                targetfile = os.path.join(targetpath,base)
                if os.path.exists(targetfile):
                    mtime = os.stat(targetfile)[stat.ST_MTIME]
                    break
            try:
                h = codecs.open(targetfile,'r','utf-8')
                buffer = h.read()
                h.close()
                headers, markup, mime_type = parse_page(buffer,BASE_TYPES[base.split('.',1)[1]])
    
                # If the page has no title header, use the path name
                if 'title' not in headers.keys():
                    headers['title'] = pagename
                headers['name'] = pagename
                
                # Now try to supply a sensible set of dates
                try:
                    # try parsing the date header
                    headers['date'] = parse_date(headers['date'])
                except:
                    # if there's no date header, use the file's modification time
                    # (if only to avoid throwing an exception again)
                    headers['date'] = mtime
                    pass
                # Never rely on the file modification time for last-modified
                # (otherwise SVN, Unison, etc play havoc with modification dates)
                try:
                    headers['last-modified'] = parse_date(headers['last-modified'])
                except:
                    headers['last-modified'] = headers['date']
                    pass
                return {'headers': headers, 'data': markup, 'content-type': mime_type}
            except IOError:
                print "IOError cascade!"
                raise IOError, "Couldn't find page %s." % (pagename)
        else:
             raise IOError, "Couldn't find page %s." % (pagename)
        return None
    

    def get_all_pages(self):
        """
        Enumerate all pages and their last modification time
        """
        for folder, subfolders, files in os.walk(self.path):
            # Skip common SCM subfolders
            # TODO: move this to a regexp-based ignore list
            for i in IGNORED_FOLDERS:
                if i in subfolders:
                    subfolders.remove(i)
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
    

    def update_page(self, pagename, fields, base = "index.txt"):
        """
        Updates a given page, inserting a neutral text file by default
        """
        targetpath = self.getPath(pagename)
        if(not os.path.exists(targetpath)):
            os.makedirs(targetpath)
        filename = os.path.join(targetpath,base) 
        try:
            open(filename, "wb").write((BASE_PAGE % fields).encode('utf-8'))
        except IOError:
            return None
        return True
    

    def add_attachment(self, pagename, filename, newbasename = None):
        targetpath = self.getPath(pagename)
        if(not os.path.exists(targetpath)):
            os.makedirs(targetpath)
        if newbasename:
            shutil.move(filename,os.path.join(targetpath,newbasename))
        else:
            shutil.move(filename,os.path.join(targetpath,os.path.basename(filename)))

#=================================

if __name__=="__main__":
    print "Initializing test store."
    s = Store('../space')
    print s.allPages()
    print "Getting test page."
    r = s.getRevision('SandBox')
    if None != r:
        print r.raw
    else:
        print "Empty page."
