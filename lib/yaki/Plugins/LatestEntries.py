#!/usr/bin/env python
# encoding: utf-8
"""
LatestEntries.py

Created by Rui Carmo on 2011-09-02.
Published under the MIT license.
"""

import re, md5, urlparse, time, cgi, traceback
import yaki.Engine, yaki.Store, yaki.Locale
from yaki.Utils import *
from yaki.Layout import *
from BeautifulSoup import *

class LatestBlogEntriesWikiPlugin(yaki.Plugins.WikiPlugin):
  def __init__(self, registry, webapp):
    registry.register('markup',self, 'plugin','LatestEntries')
    self.webapp = webapp
    self.ac = webapp.getContext()
    self.i18n = yaki.Locale.i18n[self.ac.locale]

  def run(self, serial, tag, tagname, pagename, soup, request, response): 
    ac = self.ac
    c = request.getContext()
    # define how many blog entries to show
    try:
      bound = int(tag['size'])
    except:
      bound = 3

    # filter for the namespace we want
    # TODO: this should be extensible to tags sometime in the future
    try:
      mask = re.compile(tag['src'])
    except:
      mask = re.compile('^(blog)\/(\d+){4}\/(\d+){2}\/(\d+){2}.*')
      
    # this is what entries ought to look like, ideally
    canon = "0000/00/00/0000"
    
    # find entries. 
    # We use the indexer's allpages here because that's updated upon server start
    # ...and because we want to do our own sorting anyway.
    paths = [path for path in self.ac.indexer.allpages if mask.match(path)]
    # canonize paths
    entries = {}
    for i in paths:
      (prefix, path) = i.split("/",1)
      l = len(path)
      p = len(prefix)+1
      k = len(canon)
      # add an hex digest in case there are multiple entries at the same time
      if l < k:
        entries[i[p:l+p] + canon[-(k-l):] + md5.new(i).hexdigest()] = i
      else:
        entries[i[p:] + md5.new(i).hexdigest()] = i

    latest = entries.keys()
    latest.sort()
    latest.reverse()
    # skip over the latest entry
    latest = latest[1:bound+1]
    posts = []
    for i in latest:
      name = entries[i]
      try:
        page = ac.store.getRevision(name)
      except IOError:
        print "LatestBlogEntries: could not retrieve %s" % name
        continue  
      headers = page.headers
      path = ac.base + name
      linkclass = "wikilink"
      posttitle = headers['title']
      rellink = path
      permalink = headers['bookmark'] = request.getBaseURL() + rellink
      if SANITIZE_TITLE_REGEX.match(name):
        permalink = permalink + "#%s" % sanitizeTitle(posttitle)
      description = "permanent link to this entry"
      if 'x-link' in headers.keys():
        link = uri = headers['x-link']
        (schema,netloc,path,parameters,query,fragment) = urlparse.urlparse(uri)
        if schema in self.i18n['uri_schemas'].keys():
          linkclass   = self.i18n['uri_schemas'][schema]['class']
          description = "external link to %s" % cgi.escape(uri)
      content = yaki.Engine.renderPage(self.ac,page)
      try:
        soup = BeautifulSoup(content)
        # remove all funky markup                                              
        for unwanted in ['img','plugin','div','pre']:                               
            [i.extract() for i in soup.findAll(unwanted)] 
        paragraphs = filter(lambda p: p.contents, soup.findAll('p'))
	soup = paragraphs[0]
        content = soup.renderContents().decode('utf-8')
        # TODO: impose bound checks here and insert ellipsis if appropriate.
        # the "Read More" links are added in the template below.
      except Exception, e:
        print "DEBUG: failed to trim content to first paragraph for entry %s, %s" % (name, e)
        continue
      postinfo = renderInfo(self.i18n,headers)
      metadata = renderEntryMetaData(self.i18n,headers)
      # Generate c.comments
      formatComments(ac,request,name, True)
      comments = c.comments
      try:
        tags = headers['tags']
      except:
        tags = ""
      
      references = ''
      posts.append(ac.templates['latest-entries'] % locals())
    tag.replaceWith(''.join(posts))
