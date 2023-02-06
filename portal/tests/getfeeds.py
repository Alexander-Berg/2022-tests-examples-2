#!/usr/bin/env python

from __future__ import print_function
import urllib2
import sys
import threading
import time

readed = 0
writed = 0
sizes = []
def get_data(num):
    global readed
    readed += 1
    bulka_url = "http://bulca-www.feeds.yandex.net:10020/rss-widget?limit=1000&feed_id={0}".format(num)
    try:
        responce = urllib2.urlopen(bulka_url)
        return responce.read()
    except Exception as msg:
        return None

def post_data(num, data):
    global writed
    writed += 1
    if data is None:
        print('got None data')
        return
    servurl = "http://rss-storage.wdevx.yandex.net/feeds/store/?feed_id={0}".format(num)
    try:
        request = urllib2.Request(servurl)
        request.add_data(data)
        responce = urllib2.urlopen(request)
    except IOError as e:
        #print(e)
        #sys.exit(0)
        pass

class Copier(threading.Thread):
    def __init__(self, list_of_ids):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.list_of_ids = list_of_ids
        pass

    def run(self):
        for i in self.list_of_ids:
            res = get_data(i)
            if not(res is None):
                sizes.append(len(res))
                post_data(i, res)
        self.stop()

    def stop(self):
        self._stop.set()
    def stopped(self):
        return self._stop.isSet()


copiers = []
with open('feed_id') as ids:
    ids_for_thread = []
    for id_ in ids.readlines():
        ids_for_thread.append(int(id_.rstrip()))
        if (len(ids_for_thread)  >= 1000):
            copiers.append(Copier(ids_for_thread))
            ids_for_thread = []

print ('Threads created, now starting')
for t in copiers:
    t.start()

print('Threads started, now show stats')

#for t in copiers:
#    t.join()

starttime = time.time()

def avg_size():
    global sizes
    if len(sizes) == 0:
        return 0
    res = sum(sizes) / float(len(sizes))
    if len(sizes) > 1000:
        sizes = []
    return res

while (not copiers[0].stopped()):
    nowtime = time.time()
    time.sleep(1)
    print('Readed: ', readed,
          'Writed: ', writed,
          'writes per second - {0:.3f}'.format(writed / (nowtime - starttime)),
          'reads per second - {0:.3f}'.format(readed / (nowtime - starttime)),
          'avg size = {0:.2f}kB'.format(avg_size() / 1024.0)
)

