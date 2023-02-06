# -*- coding: utf-8 -*-

"""
Модуль парсинга куки Y*
https://wiki.yandex-team.ru/cookies/y/
Y-кука - это кука-контейнер. Есть два типа y-куки - сессионная и перманентная
*ys - Сессионая y-кука.
*yp - Перманентная y-кука, выставляется до 2038 года синхронизируется через МДА
*yc - Ограниченная по времени y-кука, для выставления в браузере в нее можно писать из клиентского js
"""
from __future__ import print_function
from abc import ABCMeta
import json
import urllib
from hamcrest import equal_to
from common.utils import check_field


class CookieYException(Exception):
    def __init__(self, message):
        self.message = message


class CookieYBadCookie(CookieYException):
    pass


class CookieY(object):
    __metaclass__ = ABCMeta

    def __init__(self, value=None):
        self.blocks = {}
        if value is not None:
            self.parse(value)

    def _parse_block(self, block):
        p = block.split('.')
        if len(p) < 3:
            raise CookieYBadCookie('have not enought parts in cookie block: {}'.format(block))
        return p[1], {'ts': p[0], 'value': urllib.unquote('.'.join(p[2:]))}

    def parse(self, cookie_string):
        """
        Формат y-куки
            Формат сессионной:
                name1.value1#name2.value2#name3.value3
                name - уникальное имя alphanumeric
                value - значение url-encoded без точек см. Проблемы -> Точка в значениях
            Формат перманентной:
                expire1.name1.value1#expire2.name2.value2#expire3.name3.value3
                expire - timestamp в секундах (важно, т.к. например (new Date()).getTime() отдаёт миллисекунды)
                name - уникальное имя alphanumeric
                value - значение url-encoded без точек см. Проблемы -> Точка в значениях
        """
        self.blocks = {}
        cookie_blocks = cookie_string.split('#')
        for block in cookie_blocks:
            name, value = self._parse_block(block)
            self.blocks[name] = value
        return self

    def insert(self, block_id, block_value, ts=None):
        if ts is None:
            self.blocks[block_id] = {
                'value': block_value,
            }
        else:
            self.blocks[block_id] = {
                'ts': ts,
                'value': block_value,
            }
        return self

    def find(self, block_id):
        return self.blocks.get(block_id, None)

    def keys(self):
        return self.blocks.keys()

    def erase(self, block_id):
        if block_id in self.blocks:
            del self.blocks[block_id]
        return self

    def to_string(self):
        results = []
        for name, block in self.blocks.items():
            results.append(block['ts'] + '.' + name + '.' + urllib.quote(block['value'], safe=''))
        return '#'.join(results)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return json.dumps(self.blocks)

    def gpauto_test(self, lat, lon, precision, device):
        gpauto_value = self.find('gpauto')
        assert gpauto_value is not None
        assert gpauto_value['value'] is not None
        gpa_lat, gpa_lon, gpa_precision, gpa_device, ts = gpauto_value['value'].split(':')
        assert gpa_lat == str(lat).replace('.', '_')
        assert gpa_lon == str(lon).replace('.', '_')
        assert gpa_precision == str(precision)
        assert gpa_device == str(device)

    def test_block(self, block_name, block_value):
        value = self.find(block_name)
        check_field(value, 'value', equal_to(block_value))


class CookieYp(CookieY):
    pass


class CookieYc(CookieY):
    pass


class CookieYs(CookieY):

    def _parse_block(self, block):
        p = block.split('.')
        if len(p) < 2:
            raise CookieYBadCookie('have not enought parts in cookie block: {}'.format(block))
        return p[0], {'value': urllib.unquote('.'.join(p[2:]))}

    def to_string(self):
        results = []
        for name, block in self.blocks.items():
            r = name + '.' + urllib.quote(block['value'], safe='')
            results.append(r)
        return '#'.join(results)
