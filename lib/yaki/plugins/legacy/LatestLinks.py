#!/usr/bin/env python
# encoding: utf-8
"""
LatestLinks.py

Created by Rui Carmo on 2011-09-04.
Published under the MIT license.
"""

import re, md5, urlparse, time, cgi, traceback
import yaki.Engine, yaki.Store, yaki.Locale
from yaki.Utils import *
from yaki.Layout import *
from BeautifulSoup import *

class LatestLinkEntriesWikiPlugin(yaki.Plugins.WikiPlugin):
  def __init__(self, registry, webapp):
    registry.register('markup',self, 'plugin','LatestLinks')
    self.webapp = webapp
    self.ac = webapp.getContext()
    self.i18n = yaki.Locale.i18n[self.ac.locale]

  def run(self, serial, tag, tagname, pagename, soup, request, response): 
    ac = self.ac
    c = request.getContext()
    # define how many entries to show
    try:
      bound = int(tag['size'])
    except:
      bound = 5

    # filter for the namespace we want
    # TODO: this should be extensible to tags sometime in the future
    try:
      mask = re.compile(tag['src'])
    except:
      mask = re.compile('^(links)\/(\d+){4}\/(\d+){2}\/(\d+){2}.*')
      
    # find entries. 
    # We use the indexer's allpages here because that's updated upon server start
    # ...and because we want to do our own sorting anyway.
    latest = [path for path in self.ac.indexer.allpages if mask.match(path)]
    latest.sort()
    latest.reverse()
    posts = []
    count = 0
    for name in latest:
      try:
        page = ac.store.getRevision(name)
      except IOError:
        print "LatestLinkBlogEntries: could not retrieve %s" % name
        continue  
      headers = page.headers
      posttitle = headers['title']
      path = ac.base + name
      if 'x-link' in headers.keys():
        link = uri = headers['x-link']
        (schema,netloc,path,parameters,query,fragment) = urlparse.urlparse(uri)
        if schema in self.i18n['uri_schemas'].keys():
          linkclass   = self.i18n['uri_schemas'][schema]['class']
          description = "external link to %s" % cgi.escape(uri)
      content = yaki.Engine.renderPage(self.ac,page)
      # now try to trim content down to the first paragraph
      # TODO: check i18n for all inline HTML
      soup = BeautifulSoup(content)
      try:
        text = soup.findAll('p')
        if len(text) > 1:
          [p.extract() for p in soup.findAll('p')[1:]]
          soup.findAll('p')[0].append((u'&nbsp;<a class="wikilink" href="%s">' % (ac.base + name)) + self.i18n['readmore'] + u'</a>')
        else:
          soup.findAll('p')[0].append(u'&nbsp;<small><a class="wikilink" title="permalink to this entry" href="%s">&#x262F;</a></small>' % (ac.base + name))
      except Exception, e:
        print "DEBUG: Error in latestlinks: %s" % e

      # now look for the image and stuff the title inside it as a span
      try:
        holder = soup.findAll('div', {'class': re.compile('quicklook_holder')})[0]
        holder.findAll('a')[0]['class'] = 'disabled-quicklook'
        holder.findAll('a')[0]['href'] = link
        holder.findAll('a')[0]['title'] = "external link to %s" % cgi.escape(uri)
        holder.findAll('img')[0]['alt'] = "thumbnail of %s" % cgi.escape(uri)
        holder.findAll('a')[0].append(ac.templates['linkblog-image-overlay'] % locals())
        posts.append('<li>' + str(soup) + '</li>')
      except:
        continue
      count = count + 1
      if count == bound:
        break
    tag.replaceWith('<ul class="latest-linkblog-entries">' + ''.join(posts) + '</ul>')
