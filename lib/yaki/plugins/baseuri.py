#!/usr/bin/env python
# encoding: utf-8
"""
Reformat links and page references

Created by Rui Carmo on 2006-09-12.
Published under the MIT license.
"""

import os, sys, logging

log = logging.getLogger()

import urlparse, re
from bs4 import BeautifulSoup
from gettext import gettext as _
from yaki import Index, Store, Singleton, plugin
from utils import time_since

@plugin
class RebaseURIs:
    __metaclass__ = Singleton

    category = 'markup'
    tags     = ['a']

    uri_schemas = {
        '*'      :{'title': u'unknown protocol linking to %(uri)s','class': u'generic'},
        'http'   :{'title': u'external link to %(uri)s','class': u'http'},
        'https'  :{'title': u'secure link to %(uri)s','class': u'https'},
        'ftp'    :{'title': u'file transfer link to %(uri)s','class': u'ftp'},
        'gopher' :{'title': u'(probably deprecated) link to %(uri)s','class': u'ftp'},
        'sftp'   :{'title': u'secure file transfer link to %(uri)s','class': u'ftp'},
        'ssh'    :{'title': u'secure shell session to %(uri)s','class': u'terminal'},
        'telnet' :{'title': u'(probably insecure) terminal session to %(uri)s','class': u'terminal'},
        'mailto' :{'title': u'e-mail to %(uri)s','class': u'mail'},
        'outlook':{'title': u'MAPI link to %(uri)s','class': u'mail'},
        'skype'  :{'title': u'call %(uri)s using Skype','class': u'call'},
        'sip'    :{'title': u'call %(uri)s using SIP','class': u'call'},
        'tel'    :{'title': u'call %(uri)s using SIP','class': u'call'},
        'callto' :{'title': u'call %(uri)s','class': u'call'},
        'cid'    :{'title': u'link to attached file %(uri)s', 'class': u'linkedfile'},
        'attach' :{'title': u'link to attached file %(uri)s', 'class': u'linkedfile'}
    }

    base  = '/space'
    media = '/media'
    
    def __init__(self):
        log.debug(self)
        pass

    def run(self, serial, tag, tagname, pagename, soup, request, response):
        i, s = Index(), Store()

        try:
            uri = tag['href']
        except KeyError:
            return True
        
        # Try to handle the uri as a schema/path pair
        (schema,netloc,path,parameters,query,fragment) = urlparse.urlparse(uri)
        known = False
        if schema == '':
            uri = i.resolve_alias(path)
            if uri != path:
                path = tag['href'] = uri
            if uri in i.all_pages:
                known = True
        
        if(schema == ''):
            if s.is_attachment(pagename, path):
                tag['href'] = unicode(self.media + pagename + "/" + path)
                tag['title'] = self.schemas['attach']['title'] % {'uri':os.path.basename(path)}
                tag['class'] = self.schemas['attach']['class']
                return False

            if(known): # this is a known Wiki link, so there is no need to run it through more plugins
                if request is False:
                    # check for a direct outbound link
                    if path in i.default_links:
                        uri = i.default_links[path]
                        (schema,netloc,path,parameters,query,fragment) = urlparse.urlparse(uri)
                        tag['href'] = uri
                        tag['title'] = self.schemas[schema]['title'] % {'uri':uri}
                        tag['class'] = self.schemas[schema]['class']
                        return False
                tag['href'] = self.base + tag['href']
                tag['class'] = "wiki"
                try: # to use indexed metadata to annotate links
                    last = i.page_info[path]['last-modified']
                    tag['title'] = _('link_update_format') % (path,time_since(last))
                except:
                    tag['title'] = _('link_defined_notindexed_format') % path
            elif((schema == netloc == path == parameters == query == '') and (fragment != '')):
                # this is an anchor, leave it alone
                tag['href'] = self.ac.base + pagename + "#" + fragment
                tag['class'] = "anchor"
                try:
                    exists = tag['title']
                except:
                    tag['title'] = _('link_anchor_format') % fragment
            else:
                if request is False:
                    # remove unknown wiki links for RSS feeds
                    tag.replace_with(tag.contents[0])
                    # format for online viewing
                try:
                    exists = tag['class']
                    return True #we're done here, but this tag may need handling elsewhere
                except:
                    tag['href'] = self.base + tag['href']
                    tag['class'] = "wikiunknown"
                    tag['title'] = _('link_undefined_format') % path
        elif(schema in self.schemas.keys()): # this is an external link, so reformat it
            tag['title'] = self.schemas[schema]['title'] % {'uri':uri}
            tag['class'] = self.schemas[schema]['class']
            #tag['target'] = '_blank'
        else: # assume this is an interwiki link (i.e., it seems to have a custom schema)
            tag['title'] =  _('link_interwiki_format') % uri
            tag['class'] = "interwiki"
            #tag['target'] = '_blank'
            # Signal that this tag needs further processing
            return True
        # We're done
        return False
