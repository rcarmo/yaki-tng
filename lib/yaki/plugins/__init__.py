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

from utils import path_for, locate

class Registry:
    plugins = {'markup': {}}
    serial = 0
    
    def __init__(self, settings):
        """Load wiki plugins. Assumptions are that they are alongside this file, under the yaki tree"""
        log.info("Loading Wiki plugins...")
        # Get plugin directory
        path = os.path.dirname(__file__)
        for f in locate('*.py', path):
            (modname,ext) = os.path.basename(f).rsplit('.', 1)
            log.debug("module: %s" % modname)
            try:
                _module = __import__(modname, globals(), locals(), [''])
                for x in dir(_module):
                    if 'Plugin' in x:
                        _class = getattr(_module, x)
                        _class(self, settings)
            except ImportError:
                pass
        
    
    def register(self, category, instance, tag, name):
        """Registration callback for plugins"""

        log.debug("Plugin %s registered in category %s for tag %s" % (name,category,tag))
        if tag not in self.plugins[category].keys():
            self.plugins[category][tag] = {}
        self.plugins[category][tag][name.lower()] = instance
    
    
    def run_for_all_tags(self, pagename, soup, request=None, response=None, indexing=False):
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
        """Run each plugin"""

        if tagname == 'plugin':
            try:
                name = tag['name'].lower() # get the attribute
            except KeyError:
                return
            if name in self.plugins['markup']['plugin']:
                plugin = self.plugins['markup']['plugin'][name]
                if not indexing:
                    result = plugin.run(self.serial, tag, tagname, pagename, soup, request, response)
                    self.serial += 1
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


class Plugin:
    """Base class for all Wiki plugins"""

    def __init__(self, registry, settings):
        # Register this (override in child classes)
        registry.register('markup',self, 'plugin', 'base')  

    def run(self, serial, tag, tagname, pagename, soup, request = None, response = None, indexing = False):
        pass
    
