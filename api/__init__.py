#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application routes

Created by: Rui Carmo
"""

import os, sys, logging

log = logging.getLogger()

version = '1'
prefix = '/api/v%s' % version

# install route submodules
import store