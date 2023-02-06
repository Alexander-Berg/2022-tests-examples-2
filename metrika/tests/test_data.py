# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from passport.utils.time_utils import datetime_to_integer_unixtime


TEST_EXISTING_URL = 'http://www.artlebedev.ru/kovodstvo/104/'
TEST_NEW_URL = 'https://www.theguardian.com/books/2015/jul/03/dune-50-years-on-science-fiction-novel-world'
TEST_USER_IP = '127.0.0.1'
TEST_DEFAULT_URL = 'http://test-clck.ru'

INITIAL_TEST_DB_DATA = {
    'urls': [
        {
            'url_sum': '03b0520767b781996436a62c9ddf4605',
            'url': 'http://www.artlebedev.ru/kovodstvo/104/',
            'updated': datetime(1, 1, 1, 0, 0, 0),
        },
        {
            'url_sum': 'a34dad11a832ee984443b7f3147e6690',
            'url': 'http://bobuk.habrahabr.ru/blog/43619.html',
            'updated': datetime.now() - timedelta(days=90),
        },
    ],
    'urlcounters': [
        {
            'id': 2,
            'hits': 17,
        },
    ],
    'blacklist': [
        {
            'item': 'banned.domain',
            'added': datetime.now() - timedelta(days=50),
            'author': 'vickenty',
            'comment': 'general tests',
        },
        {
            'item': 'xn--80atjc.xn--p1ai',
            'added': datetime.now() - timedelta(days=40),
            'author': 'test.user',
            'comment': 'punicode tests',
        },
    ],
    'whitelist': [
        {
            'item': 'yandex.ru',
            'added': datetime.now() - timedelta(days=100),
            'author': 'nesusvet',
            'comment': 'Don\'t limit urls to yandex.ru and subdomains',
        },
    ],
    'domain_rate': [
        {
            'period_len': 600,
            'period_start': datetime_to_integer_unixtime(datetime.now() - timedelta(minutes=5)),
            'domain': 'yandex.ru',
            'count': 300,
        },
        {
            'period_len': 600,
            'period_start': datetime_to_integer_unixtime(datetime.now() - timedelta(minutes=4)),
            'domain': 'yandex.ru',
            'count': 50,
        },
        {
            'period_len': 600,
            'period_start': datetime_to_integer_unixtime(datetime.now() - timedelta(minutes=5)),
            'domain': 'habrahabr.ru',
            'count': 100,
        },
        {
            'period_len': 600,
            'period_start': datetime_to_integer_unixtime(datetime.now() - timedelta(minutes=6)),
            'domain': 'habrahabr.ru',
            'count': 1,
        },
    ],
    'search_index': [],
}
