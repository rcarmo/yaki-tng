#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2012, Rui Carmo
Description: Core utility functions
License: MIT (see LICENSE.md for details)
"""

import os, sys, logging
import json

log = logging.getLogger()

class Struct(dict):
    """An object that recursively builds itself from a dict and allows easy access to attributes"""

    def __init__(self, obj):
        dict.__init__(self, obj)
        for k, v in obj.iteritems():
            if isinstance(v, dict):
                self.__dict__[k] = Struct(v)
            else:
                self.__dict__[k] = v

    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setitem__(self, key, value):
        super(Struct, self).__setitem__(key, value)
        self.__dict__[key] = value

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)


def json_str(item, bind_env=True):
    """Helper function to cast JSON unicode data to plain str and bind environment variables"""

    if isinstance(item, dict):
        return {json_str(key,bind_env=bind_env): json_str(value,bind_env=bind_env) for key, value in item.iteritems()}
    elif isinstance(item, list):
        return [json_str(element, bind_env=bind_env) for element in item]
    elif isinstance(item, unicode) and bind_env:
        try:
            return item.encode('utf-8') % os.environ
        except:
            return item.encode('utf-8')
    else:
        return item


def get_config(filename=None):
    """Parses a configuration file and returns a Struct for managing the configuration"""

    if not filename:
        return Struct({})
    try:
        config = Struct(json.load(open(filename, 'r'),object_hook=json_str))
    except Exception as e:
        if sys.stderr.isatty():
            print >> sys.stderr, ('Error loading configuration file %(filename)s: %(e)s' % locals())
        else:
            log.error('Error loading configuration file %(filename)s: %(e)s' % locals())
        sys.exit(2)
    return config


def path_for(name, script=__file__):
    """Build absolute paths to resources based on app path"""

    if 'uwsgi' in sys.argv:
        return os.path.join(os.path.abspath(os.path.join(os.path.dirname(script),'..')),name)
    return os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),name))


def locate(pattern, root=os.getcwd()):
    """Generator for iterating inside a file tree"""

    for path, dirs, files in os.walk(root):
        for filename in [os.path.abspath(os.path.join(path, filename)) for filename in files if fnmatch.fnmatch(filename, pattern)]:
            yield filename


def safe_eval(buffer):
    """Perform safe evaluation of a (very) small subset of Python functions"""

    if '%' == buffer[0]:
        try:
            return eval(buffer[1:],{"__builtins__":None},{"environ":os.environ})
        except Exception, e:
            log.error('Error %s while doing safe_eval of %s' % (e, buffer))
            return None
    return buffer


def tb():
    """Return a concise traceback summary"""

    etype, value, tb = sys.exc_info()
    return "%s: %s (%s@%s:%d)" % (etype.__name__, value, tb.tb_frame.f_code.co_name, os.path.basename(tb.tb_frame.f_code.co_filename), tb.tb_lineno)
