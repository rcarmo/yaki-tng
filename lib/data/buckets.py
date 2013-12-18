#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created by Rui Carmo on 2009-02-28.
Published under the MIT license.
"""

import os, sys, time, json, logging

log = logging.getLogger()

class TimedBucket:
    """Store measurements over time slots with automatic expiration of older samples"""

    def __init__(self, granularity, expiration):
        self.__granularity = granularity
        self.__expiration = expiration
        self.__buckets = {}
        self.__start = time.time()


    def add(self, value=1):
        now = time.time()

        # use integer division
        currslot = int(now) / self.__granularity * self.__granularity
        if currslot in self.__buckets.keys():
            self.__buckets[currslot] = self.__buckets[currslot] + value
        else:
            self.__buckets[currslot] = value
        try:
            del self.__buckets[currslot - self.__expiration]
        except:
            pass


    def buckets(self):
        return self.__buckets


    def json(self):
        return json.dumps(self.__buckets)


if __name__ == '__main__':
    a = TimedBucket(5, 15)
    for x in range(120):
        a.add(1)
        print a.buckets()
        time.sleep(2)
