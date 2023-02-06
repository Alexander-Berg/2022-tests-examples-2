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
from datetime import date

count = 1000

coords = [
    ('msk', 55.79869798, 37.48825134),
    ('msk', 55.75690249, 37.40448059),
    ('msk', 55.70110514, 37.63519348),
    ('msk', 55.66774351, 37.69561829),
    ('msk', 55.84856138, 37.63519348),
    ('msk', 55.62774220, 37.61102023),
    ('msk', 55.66501946, 37.51763644),
    ('msk', 55.67782529, 37.78748812),
    ('msk', 55.71893070, 37.57703127),
    ('msk', 55.73791759, 37.79126467),
    ('msk', 55.67685530, 37.55147215),
    ('msk', 55.70280686, 37.44054847),
]

data = '{"poi":[{"subgroups":["Торговые центры","Гипермаркеты","Супермаркеты","Универмаги","Магазины продуктов"],"group":"shops"},{"subgroups":["Кафе","Пиццерии","Рестораны","Спорт-бары","Быстрое питание","Бары, пабы","Закусочные","Суши-бары","Кофейни"],"group":"supper"},{"subgroups":["аптеки"],"group":"drugstore"},{"subgroups":["АЗС"],"group":"gaz"},{"subgroups":["Банкоматы"],"group":"atm"}]}\n'

case = ''
ammo = ("POST /get?geo_id={0}&lat={1}&lon={2} HTTP/1.0\r\n"
"Host: geohelper.yandex.ru\r\n"
# "Connection: close\r\n"
"Content-Length: {3}\r\n"
"User-Agent: lunapark-get-{0}-{1}-{2}\r\n\r\n"
"{4}")
user_agent = date.today().strftime('%Y%m%d-%H%M')

i = 0
while i < count:
    i += 1
    try:
        ind = int(random.random() * len(coords))
        c = coords[ind]
    except Exception as msg:
        continue
    output = ammo.format(c[0], c[1], c[2], len(data), data)
    # print(len(output.encode('utf-8')), case)
    # print(output)
    sys.stdout.write("%d %s\n%s" % (len(output.encode('utf-8')), case, output))
