#!/usr/bin/env python
# encoding: utf-8
"""
Core classes

Created by Rui Carmo on 2006-09-10.
Published under the MIT license.
"""

import logging

log = logging.getLogger()

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]