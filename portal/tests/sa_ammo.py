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

coords = [
    ('213', 55.79869798, 37.48825134),
    ('213', 55.75690249, 37.40448059),
    ('213', 55.70110514, 37.63519348),
    ('213', 55.66774351, 37.69561829),
    ('213', 55.84856138, 37.63519348),
    ('213', 55.62774220, 37.61102023),
    ('213', 55.66501946, 37.51763644),
    ('213', 55.67782529, 37.78748812),
    ('213', 55.71893070, 37.57703127),
    ('213', 55.73791759, 37.79126467),
    ('213', 55.67685530, 37.55147215),
    ('213', 55.70280686, 37.44054847),
]

payload = '{"edadeal":{"ttl":300,"action_url":"yellowskin://?background_color=%234b9645&buttons_color=%23ffffff&' \
          'omnibox_color=%23288736&status_bar_theme=dark&text_color=%23ffffff&url=https%3A%2F%2Fedadeal.ru%2Fsankt' \
          '-peterburg%3Fsource%3Dyandex_portal%26lat%3D59.91%26lng%3D30.43%26appsearch_header%3D1","yellow_skin":{"' \
          'background_color":"#4b9645","omnibox_color":"#288736","buttons_color":"#ffffff","status_bar_theme":"dark",' \
          '"text_color":"#ffffff"},"background_color":"#399847","ttv":1200,"url":"yellowskin://?background_color=%234' \
          'b9645&buttons_color=%23ffffff&omnibox_color=%23288736&status_bar_theme=dark&text_color=%23ffffff&url=https' \
          '%3A%2F%2Fedadeal.ru%2Fsankt-peterburg%3Fsource%3Dyandex_portal%26lat%3D59.91%26lng%3D30.43%26appsearch_hea' \
          'der%3D1","action_text":"ВСЕ СКИДКИ","type":"gallery","id":"edadeal","item_layout_kind":"portrait","text_co' \
          'lor":"#ffffff"},"homeparams":{"country":"RU","topic":{"edadeal":"edadeal_card"},"route_t' \
          'itle":"","version":"999999999","poi_title":"Рядом с вами","menu":{"edadeal":{"button_color":"#ffffffff","m' \
          'enu_list":[{"text":"Настройки ленты","action":"opensettings://?screen=feed"},{"text":"Скрыть карточку","ac' \
          'tion":"hidecard://?topic_card_ids=edadeal_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%' \
          'D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83"}]},"poi":{"menu_list":[{"text":"Настройки ' \
          'ленты","action":"opensettings://?screen=feed"},{"text":"Скрыть карточку","action":"hidecard://?topic_card_' \
          'ids=poi2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%' \
          'D1%82%D0%BE%D1%87%D0%BA%D1%83"}]}},"edadeal_title":"Скидки рядом","geo_country":225,"layout":[{"type":"sea' \
          'rch","id":"search","heavy":0},{"type":"div","id":"route","heavy":1},{"type":"topnews","id":"topnews","heav' \
          'y":0},{"type":"zen","id":"zen","heavy":0},{"type":"weather","id":"weather","heavy":0},{"type":"stocks","id' \
          '":"stocks","heavy":0},{"type":"transportmap","id":"transportmap","heavy":0},{"type":"gallery","id":"edadea' \
          'l","heavy":1},{"type":"tv","id":"tv","heavy":0},{"type":"afisha","id' \
          '":"afisha","heavy":0},{"type":"gallery","id":"collections","heavy":0},{"type":"services","id":"services","' \
          'heavy":0}],"platform":"android","scale_factor":1},"route":{"direction":"reverse","dummy":{"topic":"assist_' \
          'workhome_card","ttv":1200,"utime":1512478473,"ttl":900,"on_swiped_action":"flipcard://?card_ids=route&expi' \
          're_timestamp=1513083273000&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA' \
          '%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83","id":"route","type":"div","data":{"background":[{"color":"#fff' \
          'fff","type":"div-solid-background"}],"states":[{"blocks":[{"text":"МАРШРУТ НА АВТОМОБИЛЕ","type":"div-titl' \
          'e-block","menu_items":[{"text":"Настройки ленты","url":"opensettings://?screen=feed"},{"text":"Скрыть карт' \
          'очку","url":"flipcard://?card_ids=route&expire_timestamp=1513083273000&undo_snackbar_text=%D0%92%D1%8B%20%' \
          'D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83"},{"text":"Отказать' \
          'ся от этой темы","url":"hidecard://?topic_card_ids=assist_workhome_card&undo_snackbar_text=%D0%92%D1%8B%20' \
          '%D0%BD%D0%B5%20%D0%B1%D1%83%D0%B4%D0%B5%D1%82%D0%B5%20%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B0%D1%82%D1%8C%20%' \
          'D1%83%D0%B2%D0%B5%D0%B4%D0%BE%D0%BC%D0%BB%D0%B5%D0%BD%D0%B8%D1%8F%20%D0%BD%D0%B0%20%D1%8D%D1%82%D1%83%20%D' \
          '1%82%D0%B5%D0%BC%D1%83"},{"text":"Изменить адреса","url":"yellowskin://?background_color=%23fefefe&buttons' \
          '_color=%2391989b&omnibox_color=%23f0f0f0&status_bar_theme=light&text_color=%23000000&url=https%3A%2F%2Fyan' \
          'dex.ru%2Ftune%2Fplaces"}]},{"type":"div-separator-block","size":"xs"},{"title":"Домой &#160;&#160; мин","s' \
          'ide_element":{"size":"s","element":{"ratio":1,"image_url":"https://api.yastatic.net/morda-logo/i/yandex-ap' \
          'p/route/toHomeGray.1.png","type":"div-image-element"}},"type":"div-universal-block"},{"type":"div-separato' \
          'r-block","size":"s"}],"state_id":1,"action":{"url":"yellowskin://?background_color=%23fefefe&buttons_color' \
          '=%2391989b&omnibox_color=%23f0f0f0&status_bar_theme=light&text_color=%23000000&url=https%3A%2F%2Fyandex.ru' \
          '%2Fmaps%2F%3Frt%3D30.40527%2C59.958628~30.469758%2C59.867742%26l%3Dmap%2Ctrf%2Ctrfe%26rtt%3Dauto%26mode%3D' \
          'routes%26rtm%3Datm","log_id":"whole_card"}}]}},"rt":"30.40527,59.958628~30.469758,59.867742"}}'

case = ''
ammo = ("POST /geohelper/api/v1/sa_heavy?geo_id={0}&lang=ru&lat={1}&lon={2} HTTP/1.0\r\n"
        "Host: geohelper.yandex.ru\r\n"
        "Content-Length: {3}\r\n"
        "User-Agent: lunapark-post-{0}-{1}-{2}\r\n\r\n"
        "{4}")
user_agent = date.today().strftime('%Y%m%d-%H%M')

with codecs.open("sa.ammo", "w", "utf-8") as out:
    i = 0
    while i < count:
        i += 1
        try:
            ind = int(random.random() * len(coords))
            c = coords[ind]
        except Exception as msg:
            continue
        output = ammo.format(c[0], c[1], c[2], len(payload), payload)
        line = "%d %s\n%s" % (len(output.encode('utf-8')), case, output)
        # sys.stdout.write(line)
        out.write(line)

