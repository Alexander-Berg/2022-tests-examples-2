#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import threading
import time
import re
import random
import math
import json
import codecs
from datetime import datetime

case = u''
ammo = (u"GET /get_cinema_sessions?id={0}&geoid=213&lang=ru HTTP/1.1\r\n"
"Host: geohelper.yandex.ru\r\n"
"Content-Length: {1}\r\n"
"User-Agent: lunapark-get{2}\r\n\r\n")
user_agent = datetime.now().strftime('%Y%m%d-%H:%M')

def get_request(id):
    output = ammo.format(id, 0, user_agent)
    # len(output.encode('utf-8'))
    # sys.stdout.write(u"%d %s\n%s" % (len(output.encode('utf-8')), case, output))
    return u"%d %s\n%s" % (len(output.encode('utf-8')), case, output)


with codecs.open("output.ammo", "w", "utf-8") as out:
    with open("ids.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()
            # get_request(url, cookies)
            out.write(get_request(line))
