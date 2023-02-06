#!/usr/bin/env python
from __future__ import print_function
import urllib2
import sys
import threading
import time
import re
from datetime import date

case = ''
ammo = ("GET /feeds/?feed_id={0} HTTP/1.0\r\n"
"Host: rss-storage.yandex.net\r\n"
"User-Agent: lunapark-get{1}\r\n\r\n")
user_agent = date.today().strftime('%Y%m%d-%H%M')

for id_ in sys.stdin:
    try:
        id_ = int(id_.rstrip())
    except :
        continue
    output = ammo.format(id_, user_agent)
    sys.stdout.write("%d %s\n%s" % (len(output), case, output))



