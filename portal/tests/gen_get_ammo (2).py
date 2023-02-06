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

data = u'{"poi":[{"subgroups":["Торговые центры","Гипермаркеты","Супермаркеты","Универмаги","Магазины продуктов"],"group":"shops"},{"subgroups":["Кафе","Пиццерии","Рестораны","Спорт-бары","Быстрое питание","Бары, пабы","Закусочные","Суши-бары","Кофейни"],"group":"supper"},{"subgroups":["аптеки"],"group":"drugstore"},{"subgroups":["АЗС"],"group":"gaz"},{"subgroups":["Банкоматы"],"group":"atm"}]}\n'

case = u''
ammo = (u"POST {0} HTTP/1.0\r\n"
"Host: geohelper.yandex.ru\r\n"
"Content-Length: {1}\r\n"
"{2}"
"User-Agent: lunapark-get{4}\r\n\r\n"
"{3}")
user_agent = datetime.now().strftime('%Y%m%d-%H:%M')

def get_request(url, cookies):
    output = ammo.format(url, len(data.encode('utf-8')), u'Cookie: ' + u'; '.join(cookies) + '\r\n' if len(cookies) > 0 else '', data, user_agent)
    # len(output.encode('utf-8'))
    # sys.stdout.write(u"%d %s\n%s" % (len(output.encode('utf-8')), case, output))
    return u"%d %s\n%s" % (len(output.encode('utf-8')), case, output)


with codecs.open("output.ammo", "w", "utf-8") as out:
    with open("geohelper.log.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()
            parts = line.split(' ')
            url = parts[6]
            cookies = [ part for part in parts if 'Session_id' in part or 'sessionid2' in part]
            cookies = [ cookie.replace(';', '') for cookie in cookies ]
            out.write(get_request(url, cookies))
            # get_request(url, cookies)
            # print(type(get_request(url, cookies)))
