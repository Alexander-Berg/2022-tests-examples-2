#!/usr/bin/env python
from __future__ import print_function
import urllib2
import sys
import threading
import time
import re
from datetime import date
import base64

def get_data(num):
    bulka_url = "http://localhost/feeds/?limit=20&feed_id={0}".format(num)
    try:
        responce = urllib2.urlopen(bulka_url)
        return responce.read()
    except Exception as msg:
        return None

datas = []
class Reader(threading.Thread):
    def __init__(self, list_of_ids):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.list_of_ids = list_of_ids
        pass

    def run(self):
        for i in self.list_of_ids:
            res = get_data(i)
            if not(res is None):
                datas.append((i, res))
        self.stop()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class Writer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

    def run(self):
        while(not self._stop.isSet()):
            if len(datas) > 0:
                id_, data = datas.pop()
                output = ammo.format(id_, user_agent, len(data), data)
                sys.stdout.write("%d %s\n%s\r\n" % (len(output), case, output))
            else:
                pass

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


#servurl = "http://rss-storage.wdevx.yandex.net/feeds/store/?limit=30&feed_id={0}".format(num)
case = ''
ammo = ("POST /feeds/store/?feed_id={0} HTTP/1.0\r\n"
   "Host: rss-storage.yandex.net\r\n"
   "User-Agent: lunapark-{1}\r\n"
   "Connection: close\r\n"
   "Content-Length: {2}\r\n"
   "\r\n"
   "{3}")

readers = []
ids = []
user_agent = date.today().strftime('%Y%m%d-%H%M')
writer = Writer()
writer.start()

try:
    for id_ in sys.stdin:
        ids.append(int(id_.rstrip()))
        if len(ids) >= 1000:
            r = Reader(ids)
            r.start()
            readers.append(r)
            ids = []
    #print(ids)
    r = Reader(ids)
    r.start()
    readers.append(r)
    ids = []

    flag = True
    while(flag):
        flag = False
        for r in readers:
            if not r.stopped():
                flag = True
        if len(datas) > 0:
            flag = True
        time.sleep(0.1)
    writer.stop()

except KeyboardInterrupt as exc:
    for r in readers:
        r.stop()
    print("\nInterrupted by user.\n")
    sys.exit(1)
