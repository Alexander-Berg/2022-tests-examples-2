#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import threading
import time
import re
import random
import math
import json
import codecs
from datetime import date

count = 1000

# https://geohelper-v154d1.wdevx.yandex.ru/api/v3/divproxy?id=sport

case = ''
ammo = ("GET /api/v3/divproxy?id={0} HTTP/1.0\r\n"
        "Host: geohelper.yandex.ru\r\n"
        "User-Agent: lunapark-post-{0}-{1}\r\n\r\n")

user_agent = date.today().strftime('%Y%m%d-%H%M')

with codecs.open("divproxy.ammo", "w", "utf-8") as out:
    i = 0
    while i < count:
        i += 1
        output = ammo.format('sport', user_agent)
        line = "%d %s\n%s" % (len(output.encode('utf-8')), case, output)
        out.write(line)

