#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A Solr-like API for submitting and searching documents that closely mirrors
http://wiki.apache.org/solr/UpdateJSON
"""

import os, sys, logging, time
from bottle import post, get, abort, request, response

log = logging.getLogger()

import config
from controllers.indexer import Indexer

indexer = Indexer(config.indexer)

@post('/update/json')
def update():
    if request.headers['Content-Type'] != 'application/json':
        abort(415, "Unsupported Media Type")

    if 'add' in request.json:
        add = request.json['add']
        # we're going to deviate slightly from Solr norm and use an array
        # instead of their brain-dead multiple-key approach
        if type(add) == list:
            for item in add:
                indexer.add(item['doc'])
        else:
            indexer.add(add['doc'])

    if 'delete' in request.json:
        delcmd = request.json['delete']
        if 'id' in delcmd:
            indexer.delete_by_id(delcmd['id'])
        if 'query' in delcmd:
            indexer.delete_by_query(delcmd['query'])

    if 'commit' in request.json:
        indexer.commit()

    if 'optimize' in request.json:
        indexer.optimize()


@get('/select')
def select():
    start_time = time.time()
    q = request.get('q','')

    response_header = {
        'status': 0, # except if there's an error
        'params': dict(request.query),
        'QTime' : time.time() - start_time
    }
    response = {
        'numFound': 0,
        'start': 0, # we don't do paged queries yet
        'docs': query_result
    }
    return {'responseHeader': response_header, 'response': response}

