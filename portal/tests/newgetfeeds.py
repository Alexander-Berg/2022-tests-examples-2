#!/usr/bin/env python

from __future__ import print_function
import urllib2
import sys
import threading
import time

def get_data(num):
    bulka_url = "http://bulca-www.feeds.yandex.net:10020/rss-widget?limit=2&feed_id={0}".format(num)
    try:
        responce = urllib2.urlopen(bulka_url)
        return responce.read()
    except Exception as msg:
        return None

def post_data(num, data):
    if data is None:
        return
    servurl = "http://localhost/feeds/store/?feed_id={0}".format(num)
    #servurl = "http://rss-storage.wdevx.yandex.net/feeds/store/?feed_id={0}".format(num)
    try:
        request = urllib2.Request(servurl)
        request.add_data(data)
        responce = urllib2.urlopen(request)
        return True
    except IOError as e:
        #print(e)
        #sys.exit(0)
        return False
for i in sys.stdin:
    try:
        i = int(i.rstrip())
    except :
        continue
    print('got', i, end="")
    res = get_data(i)
    print(' read data with size:', len(res), end="")
    print(' writed: ', post_data(i, res))
    print('piece of data:', res[:100])

