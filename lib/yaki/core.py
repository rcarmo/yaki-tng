#!/usr/bin/env python
# encoding: utf-8
"""
Core classes

Created by Rui Carmo on 2006-09-10.
Published under the MIT license.
"""

class Singleton(type):
    """Implement the Singleton pattern - it might be seen as evil, but it's handy."""

    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
            return cls.__instance