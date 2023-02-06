# -*- coding: utf-8 -*-
import logging

import allure
from hamcrest import assert_that

logger = logging.getLogger(__name__)


def get_field(json_data, path, safe=False):
    if isinstance(path, basestring):
        path_list = path.split('.')
    elif isinstance(path, list):
        path_list = path
    else:
        if not safe:
            raise AttributeError('Invalid path for json: "{}"'.format(path))
        else:
            return None

    result = json_data
    current_path = []

    for p in path_list:
        current_path.append(p)
        if isinstance(result, dict) and p in result and result[p] is not None:
                result = result[p]
        elif isinstance(result, (list, tuple)):
            if p.isdigit() and int(p) < len(result):
                result = result[int(p)]
        else:
            logger.error('Failed to get path `{}` from json'.format('.'.join(current_path)))
            if not safe:
                raise KeyError('Failed to get path `{}` from json'.format('.'.join(current_path)))
            else:
                return None

    return result


def check_field(json_data, path, matcher, safe=False):
    with allure.step('Check field {}: {}'.format(path, matcher)):
        value = get_field(json_data, path, safe)

        assert_that(value, matcher, 'Invalid "{}" value'.format(path))

def delete(hashmap, key):
    value = None
    if isinstance(hashmap, dict) and key in hashmap:
        value = hashmap[key]
        del hashmap[key]
    return value

def dump_obj(obj):
    for attr in dir(obj):
        if hasattr( obj, attr ):
            print "obj.%s = %s" % (attr, getattr(obj, attr))

def parse_set_cookie(set_cookie_str = ""):
    # yandexuid=964148831652799476; Expires=Fri, 14-May-2032 14:57:55 GMT; Domain=.yandex.ru; Path=/; Secure; SameSite=None, yuidss=964148831652799476; Expires=Fri, 14-May-2032 14:57:55 GMT; Domain=.yandex.ru; Path=/; Secure; SameSite=None
    week = {
        "sun": 1,
        "mon": 1,
        "tue": 1,
        "wed": 1,
        "thu": 1,
        "fri": 1,
        "sat": 1,
    }
    set_cookie = []
    start = 0
    pos = set_cookie_str.find(",")
    while pos != -1:
        if pos - start > 3 and set_cookie_str[pos-4] == "=" and set_cookie_str[pos-3:pos].lower() in week:
            pos = set_cookie_str.find(",", pos + 1)
        else:
            set_cookie.append(set_cookie_str[start:pos])
            start = pos + 1
            if start >= len(set_cookie_str):
                break
            pos = set_cookie_str.find(",", start)
    if start < len(set_cookie_str):
        set_cookie.append(set_cookie_str[start:])

    return set_cookie

class MadmMockError(Exception):
    pass

def check_madm_error(data):
    if data is not None:
        try:
            assert 'madm_mock_error' not in data
        except AssertionError:
            raise MadmMockError('madm_mock_error={}'.format(data['madm_mock_error']))
