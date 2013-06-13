#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Plugin registration and invocation

Created by Rui Carmo on 2006-11-12.
Published under the MIT license.
"""

import os, sys, re, logging

log = logging.getLogger()

from config import settings

from utils import path_for, locate

class PluginRegistry:
    plugins = {'markup': {}}
    serial = 0
    
    def __init__(self, settings):
        """Load wiki plugins. Assumptions are that they are inside the plugins directory 
             under the yaki tree, in userlibs, so we can use standard import..."""
        print "Loading Wiki plugins..."
        # Get plugin directory
        path = path_for(settings.plugins.path)
        sys.path.insert(0,path)
        for f in locate('*.py', path):
            (modname,ext) = rsplit(os.path.basename(path), '.', 1)
            #print modname
            try:
                _module = __import__(modname, globals(), locals(), [''])
                # Load each python file
                for x in dir(_module):
                    if 'WikiPlugin' in x:
                        _class = getattr(_module, x)
                        _class(self,webapp) # plugins will register themselves
            except ImportError:
                pass
        sys.path.pop()
        
    def register(self, category, instance, tag, name):
        #print "Plugin %s registered in category %s for tag %s" % (name,category,tag)
        if tag not in self.plugins[category].keys():
            self.plugins[category][tag] = {}
        self.plugins[category][tag][name.lower()] = instance
    
    def runForAllTags(self, pagename, soup, request=None, response=None, indexing=False):
        """Runs all markup plugins that process specific tags (except the plugin one)"""
        for tagname in self.plugins['markup'].keys():
            if tagname != 'plugin':
                order = self.plugins['markup'][tagname].keys()
                order.sort()
                for i in order:
                    plugin = self.plugins['markup'][tagname][i]
                    # Go through all tags in document
                    for tag in soup(tagname):
                        result = plugin.run(self.serial, tag, tagname, pagename, soup, request, response)
                        self.serial = self.serial + 1
                        if result == True:
                            continue

    def run(self, tag, tagname, pagename = None, soup = None, request=None, response=None, indexing=False):
        if tagname == 'plugin':
            try:
                name = tag['name'].lower() # get the attribute
            except KeyError:
                return
            if name in self.plugins['markup']['plugin']:
                plugin = self.plugins['markup']['plugin'][name]
                if not indexing:
                    result = plugin.run(self.serial, tag, tagname, pagename, soup, request, response)
                    self.serial = self.serial + 1
                else:
                    tag.replaceWith('')
                # ignore the result for plugin tags
        elif tagname in self.plugins['markup']:
            for i in self.plugins['markup'][tagname]:
                plugin = self.plugins['markup'][tagname][i]
                result = plugin.run(self.serial, tag, tagname, pagename, soup, request, response)
                self.serial = self.serial + 1
                # if plugin returns False, then the tag does not need to be processed any further
                if result == False:
                    return

class WikiPlugin:
    """Base class for all Wiki plugins"""
    def __init__(self, registry, webapp):
        # Register this (override in child classes)
        registry.register('markup',self, 'plugin', 'base')  
    def run(self, serial, tag, tagname, pagename, soup, request = None, response = None, indexing = False):
        pass
    
