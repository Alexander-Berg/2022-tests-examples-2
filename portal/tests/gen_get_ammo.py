#!/usr/bin/env python
from __future__ import print_function
import urllib2
import sys
import threading
import time
import re
import random
import math
from datetime import date

case = ''
ammo = ("GET /cards/uid?uid={0} HTTP/1.0\r\n"
"Host: postcards.yandex.net\r\n"
"User-Agent: lunapark-get{1}\r\n\r\n")
user_agent = date.today().strftime('%Y%m%d-%H%M')

i = 0
while i < 10000:
    i += 1
    try:
        uid = int(random.random() * 100000)
    except Exception as msg:
        continue
    output = ammo.format(uid, user_agent)
    sys.stdout.write("%d %s\n%s" % (len(output), case, output))



