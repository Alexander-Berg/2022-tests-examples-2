#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import urllib2
import time
import sys
import random


class Profiler(object):
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type_, value, traceback):
        print ("Elapsed time: {0:.3f} sec in section {1}".format(time.time() - self._startTime, self.message))


def get_answer(num):
    response = urllib2.urlopen('http://localhost:9999/feeds/?feed_id=%d'%(num))
    if response.code == 200:
        res = response.read()
        #print (res)
        return res == 'Internal Server Error\n'
    else:
        return False

def delete_feed(num):
    request = urllib2.Request('http://localhost:9999/feeds/delete/?feed_id=%d'%(num))
    request.get_method = lambda: 'DELETE'
    responce = urllib2.urlopen(request)
    return responce.read()

for i in xrange(1000,10000):
    if get_answer(i):
        print(i, delete_feed(i).rstrip())
