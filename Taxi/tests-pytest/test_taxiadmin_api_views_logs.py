# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy
import datetime
import json
import pytest

from django import test as django_test

from taxi.util import dates

from taxiadmin.logreader import common
from taxiadmin.logreader import elasticsearch

ELASTIC_DATA = [
    {
        'code': '404',
        'level': 'error',
        'time': datetime.datetime(2012, 11, 11, 23, 00, 01),
        'user_id': 'test_user_id_1',
        'user_uid': 'test_user_uid_1',
        'phone_id': '70686f6e655f696450000001',
        'order_id': 'test_order_id_1',
        'park_id': 'test_park_id_1',
        'driver_id': 'test_driver_id_1',
        'type': 'email',
        'delay': 1.23,
        '_link': 'test_link_1',
        'useragent': 'KeepAliveClient',
    },
    {
        'code': '404',
        'level': 'error',
        'time': datetime.datetime(2012, 11, 11, 23, 00, 01),
        'user_id': 'test_user_id_1',
        'user_uid': 'test_user_uid_1',
        'phone_id': '70686f6e655f696450000001',
        'order_id': 'test_order_id_1',
        'park_id': 'test_park_id_1',
        'driver_id': 'test_driver_id_1',
        'type': 'routeinfo',
        'delay': 1.44,
        '_link': 'test_link_1',
    },
    {
        'code': '200',
        'level': 'info',
        'time': datetime.datetime(2012, 11, 11, 23, 00, 01),
        'user_id': 'test_user_id_2',
        'user_uid': 'test_user_uid_2',
        'phone_id': '70686f6e655f696450000002',
        'order_id': 'test_order_id_2',
        'park_id': 'test_park_id_2',
        'driver_id': 'test_driver_id_2',
        'type': 'email',
        'delay': 1.23,
        '_link': 'test_link_2',
    },
    {
        'code': '200',
        'level': 'info',
        'time': datetime.datetime(2012, 10, 11, 23, 00, 01, 1),
        'user_id': 'test_user_id_3',
        'user_uid': 'test_user_uid_3',
        'phone_id': '70686f6e655f696450000003',
        'order_id': 'test_order_id_3',
        'park_id': 'test_park_id_3',
        'driver_id': 'test_driver_id_3',
        'type': 'test_type',
        'delay': 1.277,
        '_link': 'test_link_3',
    },
    {
        'code': '200',
        'level': 'info',
        'time': datetime.datetime(2012, 9, 11, 23, 00, 01),
        'user_id': 'test_user_id_4',
        'user_uid': 'test_user_uid_4',
        'phone_id': '70686f6e655f696450000004',
        'order_id': 'test_order_id_4',
        'park_id': 'test_park_id_4',
        'driver_id': 'test_driver_id_4',
        'type': 'test_type',
        'delay': 1.277,
        '_link': 'test_link_4',
    },
    {
        'code': '200',
        'level': 'info',
        'time': datetime.datetime(2012, 9, 11, 23, 00, 01),
        'user_id': 'test_user_id_5',
        'user_uid': 'test_user_uid_5',
        'phone_id': '70686f6e655f696450000005',
        'order_id': 'test_order_id_5',
        'park_id': 'test_park_id_5',
        'driver_id': 'test_driver_id_5',
        'type': 'test_type_1',
        'delay': 1.277,
        '_link': 'test_link_7'
    },
    {
        'code': '200',
        'level': 'info',
        'time': datetime.datetime(2012, 9, 11, 23, 00, 01),
        'user_id': 'test_user_id_6',
        'user_uid': 'test_user_uid_6',
        'phone_id': '70686f6e655f696450000006',
        'order_id': 'test_order_id_6',
        'park_id': 'test_park_id_6',
        'driver_id': 'test_driver_id_6',
        'type': 'test_type_1',
        'delay': 1.277,
        '_link': 'test_link_8'
    },
    {
        'code': '200',
        'level': 'info',
        'time': datetime.datetime(2012, 9, 11, 23, 00, 02),
        'user_id': 'test_user_id_4',
        'user_uid': 'test_user_uid_4',
        'phone_id': '70686f6e655f696450000004',
        'order_id': 'test_order_id_4',
        'park_id': 'test_park_id_4',
        'driver_id': 'test_driver_id_4',
        'type': 'test_type_1',
        'delay': 1.277,
        '_link': 'test_link_5',
        'method': 'POST'
    },
    {
        'code': '200',
        'level': 'info',
        'time': datetime.datetime(2012, 9, 11, 23, 00, 01),
        'user_id': 'test_user_id_4',
        'user_uid': 'test_user_uid_4',
        'phone_id': '70686f6e655f696450000004',
        'order_id': 'test_order_id_4',
        'park_id': 'test_park_id_4',
        'driver_id': 'test_driver_id_4',
        'type': 'test_type_1',
        'delay': 1.277,
        '_link': 'test_link_6',
        'method': 'GET'
    },
    {
        'code': '401',
        'level': 'error',
        'time': datetime.datetime(2012, 11, 11, 23, 00, 03),
        'user_id': 'test_user_id_2',
        'user_uid': 'test_user_uid_2',
        'phone_id': '70686f6e655f696450000002',
        'order_id': 'test_order_id_2',
        'park_id': 'test_park_id_2',
        'driver_id': 'test_driver_id_2',
        'type': 'auth',
        'delay': 1.44,
        '_link': 'test_link_9',
    },
    {
        'code': '401',
        'level': 'error',
        'time': datetime.datetime(2012, 11, 11, 23, 00, 02),
        'user_id': 'test_user_id_4',
        'user_uid': 'test_user_uid_4',
        'order_id': 'test_order_id_4',
        'park_id': 'test_park_id_4',
        'driver_id': 'test_driver_id_4',
        'type': 'auth',
        'delay': 1.44,
        '_link': 'test_link_10',
    },
]

DETAILS_ELASTIC_DATA = {
    'hits': {
        'hits': [
            {
                'sort': [1519991929795],
                '_type': 'request',
                '_source': {
                    'cgroups': ['taxi_unstable_xiva_proxy'],
                    'thread': '7fa7e20d7700',
                    'level': 'INFO',
                    '@version': '1',
                    '@timestamp': '2018-03-02T11:58:49.795Z',
                    'tags': ['_logstash_parsed'],
                    'text': 'start handling /ping',
                    'uri': '/ping',
                    'module': ('handleRequest ( common/src/handler_util/base.c'
                               'pp:130 )'),
                    'source': 'yandex-taxi',
                    'host': 'xiva-proxy-man-01.taxi.dev.yandex.net',
                    'link': 'ccdc443157fb49cd847faf00bb4e7e44',
                    'span_id': '30f40771c9f543d9a5b3a7a1dfb9ff30',
                    'path': ('/var/log/fastcgi2/taxi-xiva-proxy/taxi-xiva-pro'
                             'xy.log'),
                    'useragent': 'KeepAliveClient',
                    'message': ('tskv\ttimestamp=2018-03-02 14:58:49,795567\tm'
                                'odule=handleRequest ( common/src/handler_util'
                                '/base.cpp:130 )\tlevel=INFO\tthread=7fa7e20d7'
                                '700\tlink=ccdc443157fb49cd847faf00bb4e7e44\t'
                                'seragent=KeepAliveClient\turi=/ping\tacceptla'
                                'ng=\thost=\t_type=request\tbody=\tremote_ip=2'
                                'a02:6b8:0:e00::b16a\tmethod=GET\ttext=start h'
                                'andling /ping\t'),
                    'type': 'request',
                    'method': 'GET',
                    'remote_ip': '2a02:6b8:0:e00::b16a'
                },
                '_score': None,
                '_index': 'yandex-taxi-2018.03.02.11',
                '_id': 'AWHmlDkE_1yDx1deXuOP'
            },
            {
                'sort': [1519991929795],
                '_type': 'response',
                '_source': {
                    'body': '{ "status": "ok"}',
                    'cgroups': ['taxi_unstable_xiva_proxy'],
                    'thread': '7fa7e20d7700',
                    'level': 'INFO',
                    '@version': '1',
                    '@timestamp': '2018-03-02T11:58:49.795Z',
                    'tags': ['_logstash_parsed'],
                    'uri': '/ping',
                    'module': ('handleRequest ( common/src/handler_util/base.c'
                               'pp:181 )'),
                    'delay': '0.000100',
                    'source': 'yandex-taxi',
                    'host': 'xiva-proxy-man-01.taxi.dev.yandex.net',
                    'meta_type': 'ping',
                    'link': 'ccdc443157fb49cd847faf00bb4e7e44',
                    'span_id': '30f40771c9f543d9a5b3a7a1dfb9ff30',
                    'text': 'finish handling /ping',
                    'meta_code': '200',
                    'path': ('/var/log/fastcgi2/taxi-xiva-proxy/taxi-xiva-pro'
                             'xy.log'),
                    'message': ('tskv\ttimestamp=2018-03-02 14:58:49,795629\t'
                                'module=handleRequest ( common/src/handler_uti'
                                'l/base.cpp:181 )\tlevel=INFO\tthread=7fa7e20d'
                                '7700\tlink=ccdc443157fb49cd847faf00bb4e7e44\t'
                                'meta_type=ping\thost=\turi=/ping\t_type=resp'
                                'onse\tmeta_code=200\tdelay=0.000100\tbody={ "'
                                'status": "ok"}\ttext=finish handling /ping'
                                '\t'),
                    'type': 'response'
                },
                '_score': None,
                '_index': 'yandex-taxi-2018.03.02.11',
                '_id': 'AWHmlDkE_1yDx1deXuOQ'
            },
            {
                'sort': [1519991929795],
                '_type': 'log',
                '_source': {
                    'cgroups': ['taxi_unstable_xiva_proxy'],
                    'thread': '7fa7e20d7700',
                    'level': 'ERROR',
                    '@version': '1',
                    '@timestamp': '2018-03-02T11:58:49.795Z',
                    'tags': ['_logstash_parsed'],
                    'text': 'ERRRROOORRRR',
                    'uri': '/ping',
                    'module': ('handleRequest ( common/src/handler_util/base.c'
                               'pp:130 )'),
                    'source': 'yandex-taxi',
                    'host': 'xiva-proxy-man-01.taxi.dev.yandex.net',
                    'link': 'ccdc443157fb49cd847faf00bb4e7e44',
                    'span_id': '30f40771c9f543d9a5b3a7a1dfb9ff30',
                    'path': ('/var/log/fastcgi2/taxi-xiva-proxy/taxi-xiva-pro'
                             'xy.log'),
                    'useragent': 'KeepAliveClient',
                    'message': ('tskv\ttimestamp=2018-03-02 14:58:49,795567\tm'
                                'odule=handleRequest ( common/src/handler_util'
                                '/base.cpp:130 )\tlevel=INFO\tthread=7fa7e20d7'
                                '700\tlink=ccdc443157fb49cd847faf00bb4e7e44\t'
                                'seragent=KeepAliveClient\turi=/ping\tacceptla'
                                'ng=\thost=\t_type=request\tbody=\tremote_ip=2'
                                'a02:6b8:0:e00::b16a\tmethod=GET\ttext=start h'
                                'andling /ping\t'),
                    'type': 'request',
                    'method': 'GET',
                    'remote_ip': '2a02:6b8:0:e00::b16a'
                },
                '_score': None,
                '_index': 'yandex-taxi-2018.03.02.11',
                '_id': 'AWHmlDkE_1yDx1deXuOP'
            },
            {
                'sort': [1519991929795],
                '_type': 'log',
                '_source': {
                    'body': '{ "status": "ok"}',
                    'cgroups': ['taxi_unstable_xiva_proxy'],
                    'thread': '7fa7e20d7700',
                    'level': 'INFO',
                    '@version': '1',
                    '@timestamp': '2018-03-02T11:58:49.795Z',
                    'tags': ['_logstash_parsed'],
                    'uri': '/ping',
                    'module': ('handleRequest ( common/src/handler_util/base.c'
                               'pp:181 )'),
                    'delay': '0.000100',
                    'source': 'yandex-taxi',
                    'host': 'xiva-proxy-man-01.taxi.dev.yandex.net',
                    'meta_type': 'ping',
                    'link': 'ccdc443157fb49cd847faf00bb4e7e44',
                    'span_id': '30f40771c9f543d9a5b3a7a1dfb9ff30',
                    'text': 'finish handling /ping',
                    'meta_code': '200',
                    'path': ('/var/log/fastcgi2/taxi-xiva-proxy/taxi-xiva-pro'
                             'xy.log'),
                    'message': ('tskv\ttimestamp=2018-03-02 14:58:49,795629\t'
                                'module=handleRequest ( common/src/handler_uti'
                                'l/base.cpp:181 )\tlevel=INFO\tthread=7fa7e20d'
                                '7700\tlink=ccdc443157fb49cd847faf00bb4e7e44\t'
                                'meta_type=ping\thost=\turi=/ping\t_type=resp'
                                'onse\tmeta_code=200\tdelay=0.000100\tbody={ "'
                                'status": "ok"}\ttext=finish handling /ping'
                                '\t'),
                    'type': 'response'
                },
                '_score': None,
                '_index': 'yandex-taxi-2018.03.02.11',
                '_id': 'AWHmlDkE_1yDx1deXuOQ'
            }
        ],
        'total': 4,
        'max_score': None
    },
    '_shards': {
        'successful': 78,
        'failed': 0,
        'total': 78
    },
    'took': 8304,
    'timed_out': False
}


@pytest.mark.parametrize('code,params,expected', [
    (
        400, {
            'time_from': 'asd',
            'limit': 5,
            'type': 'email,routeinfo',
            'status_code': '404'
        }, None
    ),
    (
        400, {
            'type': 'email,routeinfo',
            'status_code': '404'
        }, None
    ),
    (
        400, {
            'limit': 'wrew',
            'type': 'email,routeinfo',
            'status_code': '404'
        }, None
    ),
    (
        200, {
            'limit': 5,
            'type': 'email,routeinfo',
            'status_code': '404'
        },
        [
            {
                'code': '404',
                'level': 'error',
                'time': '2012-11-12T03:00:01.000000+0400',
                'user_id': 'test_user_id_1',
                'user_uid': 'test_user_uid_1',
                'user_phone': 'test_phone_1',
                'order_id': 'test_order_id_1',
                'park_id': 'test_park_id_1',
                'driver_id': 'test_driver_id_1',
                'type': 'email',
                'delay': '1.230',
                'park_name': 'test_park_name_1',
                'link': 'test_link_1',
                'useragent': 'KeepAliveClient',
            },
            {
                'code': '404',
                'level': 'error',
                'time': '2012-11-12T03:00:01.000000+0400',
                'user_id': 'test_user_id_1',
                'user_uid': 'test_user_uid_1',
                'user_phone': 'test_phone_1',
                'order_id': 'test_order_id_1',
                'park_id': 'test_park_id_1',
                'driver_id': 'test_driver_id_1',
                'type': 'routeinfo',
                'park_name': 'test_park_name_1',
                'delay': '1.440',
                'link': 'test_link_1',
            }
        ]
    ),
    (
        200, {
            'limit': 5,
            'type': 'email,routeinfo,test_type',
            'time_from': '2012-10-11',
            'time_to': '2012-10-13'
        },
        [
            {
                'code': '200',
                'level': 'info',
                'time': '2012-10-12T03:00:01.000001+0400',
                'user_id': 'test_user_id_3',
                'user_uid': 'test_user_uid_3',
                'user_phone': 'test_phone_3',
                'order_id': 'test_order_id_3',
                'park_id': 'test_park_id_3',
                'driver_id': 'test_driver_id_3',
                'type': 'test_type',
                'delay': '1.277',
                'link': 'test_link_3',
            }
        ]
    ),
    (
        200, {
            'limit': 5,
            'type': 'routeinfo,test_type',
            'order_id': 'test_order_id_1',
        },
        [
            {
                'code': '404',
                'level': 'error',
                'time': '2012-11-12T03:00:01.000000+0400',
                'user_id': 'test_user_id_1',
                'user_uid': 'test_user_uid_1',
                'user_phone': 'test_phone_1',
                'order_id': 'test_order_id_1',
                'park_id': 'test_park_id_1',
                'driver_id': 'test_driver_id_1',
                'type': 'routeinfo',
                'delay': '1.440',
                'link': 'test_link_1',
                'park_name': 'test_park_name_1',
            }
        ]
    ),
    (
        200, {
            'limit': 5,
            'type': 'routeinfo,test_type',
            'order_id': 'test_order_id_1',
        },
        [
            {
                'code': '404',
                'level': 'error',
                'time': '2012-11-12T03:00:01.000000+0400',
                'user_id': 'test_user_id_1',
                'user_uid': 'test_user_uid_1',
                'user_phone': 'test_phone_1',
                'order_id': 'test_order_id_1',
                'park_id': 'test_park_id_1',
                'driver_id': 'test_driver_id_1',
                'type': 'routeinfo',
                'delay': '1.440',
                'link': 'test_link_1',
                'park_name': 'test_park_name_1',
            }
        ]
    ),
    (
        200, {
            'limit': 5,
            'type': 'routeinfo,test_type',
            'user_id': 'test_user_id_1',
        },
        [
            {
                'code': '404',
                'level': 'error',
                'time': '2012-11-12T03:00:01.000000+0400',
                'user_id': 'test_user_id_1',
                'user_uid': 'test_user_uid_1',
                'user_phone': 'test_phone_1',
                'order_id': 'test_order_id_1',
                'park_id': 'test_park_id_1',
                'driver_id': 'test_driver_id_1',
                'type': 'routeinfo',
                'delay': '1.440',
                'link': 'test_link_1',
                'park_name': 'test_park_name_1',
            }
        ]
    ),
    (
        200, {
            'limit': 5,
            'type': 'routeinfo,test_type',
            'user_id': 'test_user_id_1',
        },
        [
            {
                'code': '404',
                'level': 'error',
                'time': '2012-11-12T03:00:01.000000+0400',
                'user_id': 'test_user_id_1',
                'user_uid': 'test_user_uid_1',
                'user_phone': 'test_phone_1',
                'order_id': 'test_order_id_1',
                'park_id': 'test_park_id_1',
                'driver_id': 'test_driver_id_1',
                'type': 'routeinfo',
                'delay': '1.440',
                'link': 'test_link_1',
                'park_name': 'test_park_name_1',
            }
        ]
    ),
    (
        200, {
            'limit': 5,
            'type': 'routeinfo,test_type',
            'user_uid': 'test_user_uid_1',
        },
        [
            {
                'code': '404',
                'level': 'error',
                'time': '2012-11-12T03:00:01.000000+0400',
                'user_id': 'test_user_id_1',
                'user_uid': 'test_user_uid_1',
                'user_phone': 'test_phone_1',
                'order_id': 'test_order_id_1',
                'park_id': 'test_park_id_1',
                'driver_id': 'test_driver_id_1',
                'type': 'routeinfo',
                'delay': '1.440',
                'link': 'test_link_1',
                'park_name': 'test_park_name_1',
            }
        ]
    ),
    (
        200, {
            'limit': 5,
            'type': 'routeinfo,test_type',
            'user_phone': '+123123',
        },
        [
            {
                'code': '200',
                'level': 'info',
                'time': '2012-09-12T03:00:01.000000+0400',
                'user_id': 'test_user_id_4',
                'user_uid': 'test_user_uid_4',
                'user_phone': '+123123',
                'order_id': 'test_order_id_4',
                'park_id': 'test_park_id_4',
                'driver_id': 'test_driver_id_4',
                'type': 'test_type',
                'delay': '1.277',
                'link': 'test_link_4',
            }
        ]
    ),
    (
        200, {
            'limit': 5,
            'type': 'routeinfo,test_type',
            'park_name': 'test_park_name_1',
        },
        [
            {
                'code': '404',
                'level': 'error',
                'time': '2012-11-12T03:00:01.000000+0400',
                'user_id': 'test_user_id_1',
                'user_uid': 'test_user_uid_1',
                'user_phone': 'test_phone_1',
                'order_id': 'test_order_id_1',
                'park_id': 'test_park_id_1',
                'driver_id': 'test_driver_id_1',
                'type': 'routeinfo',
                'delay': '1.440',
                'link': 'test_link_1',
                'park_name': 'test_park_name_1',
            }
        ]
    ),
    (400, {'limit': 1, 'http_method': 'booyaka'}, None),
    (
        200,
        {
            'limit': 1,
            'http_method': 'post'
        },
        [
            {
                'code': '200',
                'level': 'info',
                'time': '2012-09-12T03:00:02.000000+0400',
                'user_id': 'test_user_id_4',
                'user_uid': 'test_user_uid_4',
                'user_phone': '+123123',
                'order_id': 'test_order_id_4',
                'park_id': 'test_park_id_4',
                'driver_id': 'test_driver_id_4',
                'type': 'test_type_1',
                'delay': '1.277',
                'link': 'test_link_5',
            },
        ],
    ),
    (
        200,
        {
            'limit': 1,
            'http_method': 'Post'
        },
        [
            {
                'code': '200',
                'level': 'info',
                'time': '2012-09-12T03:00:02.000000+0400',
                'user_id': 'test_user_id_4',
                'user_uid': 'test_user_uid_4',
                'user_phone': '+123123',
                'order_id': 'test_order_id_4',
                'park_id': 'test_park_id_4',
                'driver_id': 'test_driver_id_4',
                'type': 'test_type_1',
                'delay': '1.277',
                'link': 'test_link_5',
            },
        ],
    ),
    (400, {'limit': 1, 'http_method': 'post,booyaka'}, None),
    (
        200,
        {
            'limit': 2,
            'http_method': 'post,get'
        },
        [
            {
                'code': '200',
                'level': 'info',
                'time': '2012-09-12T03:00:02.000000+0400',
                'user_id': 'test_user_id_4',
                'user_uid': 'test_user_uid_4',
                'user_phone': '+123123',
                'order_id': 'test_order_id_4',
                'park_id': 'test_park_id_4',
                'driver_id': 'test_driver_id_4',
                'type': 'test_type_1',
                'delay': '1.277',
                'link': 'test_link_5',
            },
            {
                'code': '200',
                'level': 'info',
                'time': '2012-09-12T03:00:01.000000+0400',
                'user_id': 'test_user_id_4',
                'user_uid': 'test_user_uid_4',
                'user_phone': '+123123',
                'order_id': 'test_order_id_4',
                'park_id': 'test_park_id_4',
                'driver_id': 'test_driver_id_4',
                'type': 'test_type_1',
                'delay': '1.277',
                'link': 'test_link_6',
            },
        ],
    ),
    (
        200,
        {
            'limit': 2,
            'http_method': 'post, get,put'
        },
        [
            {
                'code': '200',
                'level': 'info',
                'time': '2012-09-12T03:00:02.000000+0400',
                'user_id': 'test_user_id_4',
                'user_uid': 'test_user_uid_4',
                'user_phone': '+123123',
                'order_id': 'test_order_id_4',
                'park_id': 'test_park_id_4',
                'driver_id': 'test_driver_id_4',
                'type': 'test_type_1',
                'delay': '1.277',
                'link': 'test_link_5',
            },
            {
                'code': '200',
                'level': 'info',
                'time': '2012-09-12T03:00:01.000000+0400',
                'user_id': 'test_user_id_4',
                'user_uid': 'test_user_uid_4',
                'user_phone': '+123123',
                'order_id': 'test_order_id_4',
                'park_id': 'test_park_id_4',
                'driver_id': 'test_driver_id_4',
                'type': 'test_type_1',
                'delay': '1.277',
                'link': 'test_link_6',
            },
        ]
    ),
    (
        200,
        {
            'limit': 1,
            'http_method': '-get',
            'from_archive': True
        },
        [
            {
                'code': '200',
                'level': 'info',
                'time': '2012-09-12T03:00:02.000000+0400',
                'user_id': 'test_user_id_4',
                'user_uid': 'test_user_uid_4',
                'user_phone': '+123123',
                'order_id': 'test_order_id_4',
                'park_id': 'test_park_id_4',
                'driver_id': 'test_driver_id_4',
                'type': 'test_type_1',
                'delay': '1.277',
                'link': 'test_link_5',
            },
        ],
    ),
    (400, {'limit': 1, 'http_method': 'get,-get'}, None),
    (400, {'limit': 1, 'uber_users': 'true'}, None),
    (200, {'limit': 1, 'uber_users': 'true', 'user_phone': '+123123'}, []),
    (
            200,
            {
                'limit': 2,
                'uber_users': 'true',
                'user_phone': '+54321'
            },
            [
                {
                    'code': '200',
                    'level': 'info',
                    'time': '2012-09-12T03:00:01.000000+0400',
                    'user_id': 'test_user_id_5',
                    'user_uid': 'test_user_uid_5',
                    'user_phone': '+54321',
                    'order_id': 'test_order_id_5',
                    'park_id': 'test_park_id_5',
                    'driver_id': 'test_driver_id_5',
                    'type': 'test_type_1',
                    'delay': '1.277',
                    'link': 'test_link_7'
                },
            ]
    ),
    (
            200,
            {
                'limit': 2,
                'user_phone': '+54321'
            },
            [
                {
                    'code': '200',
                    'level': 'info',
                    'time': '2012-09-12T03:00:01.000000+0400',
                    'user_id': 'test_user_id_5',
                    'user_uid': 'test_user_uid_5',
                    'user_phone': '+54321',
                    'order_id': 'test_order_id_5',
                    'park_id': 'test_park_id_5',
                    'driver_id': 'test_driver_id_5',
                    'type': 'test_type_1',
                    'delay': '1.277',
                    'link': 'test_link_7'
                },
                {
                    'code': '200',
                    'level': 'info',
                    'time': '2012-09-12T03:00:01.000000+0400',
                    'user_id': 'test_user_id_6',
                    'user_uid': 'test_user_uid_6',
                    'user_phone': '+54321',
                    'order_id': 'test_order_id_6',
                    'park_id': 'test_park_id_6',
                    'driver_id': 'test_driver_id_6',
                    'type': 'test_type_1',
                    'delay': '1.277',
                    'link': 'test_link_8'
                },
            ]
    ),
    (200, {'limit': 1, 'user_phone': '+123123123'}, []),
    (
        200,
        {
            'limit': 5,
            'type': 'auth',
        },
        [
            {
                'code': '401',
                'level': 'error',
                'time': '2012-11-12T03:00:03.000000+0400',
                'user_id': 'test_user_id_2',
                'user_uid': 'test_user_uid_2',
                'user_phone': 'test_phone_2',
                'order_id': 'test_order_id_2',
                'park_id': 'test_park_id_2',
                'driver_id': 'test_driver_id_2',
                'type': 'auth',
                'delay': '1.440',
                'link': 'test_link_9',
            },
            {
                'code': '401',
                'level': 'error',
                'time': '2012-11-12T03:00:02.000000+0400',
                'user_id': 'test_user_id_4',
                'user_uid': 'test_user_uid_4',
                'user_phone': '+123123',
                'order_id': 'test_order_id_4',
                'park_id': 'test_park_id_4',
                'driver_id': 'test_driver_id_4',
                'type': 'auth',
                'delay': '1.440',
                'link': 'test_link_10',
            },
        ]
    ),
])
@pytest.mark.asyncenv('blocking')
def test_get_list(code, params, expected, patch):
    @patch('taxiadmin.logreader.elasticsearch.get_requests')
    def get_requests(filters, offset, limit, time_storage,
                     preference=None, from_index=None, log_extra=None):
        result = []
        for log in ELASTIC_DATA:
            if _check_for_filters(log, filters):
                result.append(log)
        return result, None

    response = django_test.Client().get(
        '/api/logs/list/', data=params,
    )

    assert response.status_code == code
    if code == 200:
        assert json.loads(response.content) == expected


def _check_for_filters(log, filters):
    if filters.time_from:
        if log['time'] < filters.time_from:
            return False
    if filters.time_to:
        if log['time'] >= filters.time_to:
            return False
    if filters.user_id:
        if log['user_id'] != filters.user_id:
            return False
    if filters.user_uid:
        if log['user_uid'] != filters.user_uid:
            return False
    if filters.user_phone_id is not None:
        if 'phone_id' in log:
            if log['phone_id'] not in filters.user_phone_id:
                return False
    if filters.user_phone_by_user is not None:
        if log['user_id'] not in filters.user_phone_by_user:
            return False
    if filters.order_id:
        if log['order_id'] != filters.order_id:
            return False
    if filters.taxi_alias_id:
        if log['taxi_alias_id'] != filters.taxi_alias_id:
            return False
    if filters.park_id:
        if log['park_id'] != filters.park_id:
            return False
    if filters.driver_id:
        if log['driver_id'] != filters.driver_id:
            return False
    if filters.type_:
        types, no_types = filters.type_
        if log['type'] not in types:
            return False
    if filters.status_code:
        if int(log['code']) != filters.status_code:
            return False
    if filters.http_methods:
        methods, excluded_methods = filters.http_methods
        method = log.get('method')
        if method is None:
            return False
        if excluded_methods and method in excluded_methods:
            return False
        if methods and method not in methods:
            return False
    return True


@pytest.mark.parametrize('code,expected,link_id,data', [
    (
        200,
        {
            'host': 'xiva-proxy-man-01.taxi.dev.yandex.net',
            'lang': 'json',
            'log_extra_link': 'ccdc443157fb49cd847faf00bb4e7e44',
            'span_id': '30f40771c9f543d9a5b3a7a1dfb9ff30',
            'method': 'GET',
            'request_body': (
                '\u0422\u0435\u043b\u043e \u0437\u0430\u043f\u0440\u043e'
                '\u0441\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435'
                '\u043d\u043e, \u0432\u043e\u0437\u043c\u043e\u0436\u043d'
                '\u043e, \u043b\u043e\u0433\u0438\u0440\u043e\u0432\u0430'
                '\u043d\u0438\u0435 \u043e\u0442\u043a\u043b\u044e\u0447'
                '\u0435\u043d\u043e.'
            ),
            'response_body': '{ "status": "ok"}',
            'uri': '/ping',
            'useragent': 'KeepAliveClient',
            'logs': [
                {
                    'time': '2018-03-02T14:58:49.795000+0300',
                    'message': ('(useragent=KeepAliveClient, method=GET, remot'
                                'e_ip=2a02:6b8:0:e00::b16a) ERRRROOORRRR'),
                    'level': 'error'
                },
                {
                    'time': '2018-03-02T14:58:49.795000+0300',
                    'message': 'finish handling /ping',
                    'level': 'info'
                },
            ]
        }, 'ccdc443157fb49cd847faf00bb4e7e44', {}
    ),
    (
        200,
        {
            'host': 'xiva-proxy-man-01.taxi.dev.yandex.net',
            'lang': 'json',
            'log_extra_link': 'ccdc443157fb49cd847faf00bb4e7e44',
            'span_id': '30f40771c9f543d9a5b3a7a1dfb9ff30',
            'method': 'GET',
            'request_body': (
                '\u0422\u0435\u043b\u043e \u0437\u0430\u043f\u0440\u043e'
                '\u0441\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435'
                '\u043d\u043e, \u0432\u043e\u0437\u043c\u043e\u0436\u043d'
                '\u043e, \u043b\u043e\u0433\u0438\u0440\u043e\u0432\u0430'
                '\u043d\u0438\u0435 \u043e\u0442\u043a\u043b\u044e\u0447'
                '\u0435\u043d\u043e.'
            ),
            'response_body': '{ "status": "ok"}',
            'uri': '/ping',
            'useragent': 'KeepAliveClient',
            'logs': [
                {
                    'time': '2018-03-02T14:58:49.795000+0300',
                    'message': ('(useragent=KeepAliveClient, method=GET, remot'
                                'e_ip=2a02:6b8:0:e00::b16a) ERRRROOORRRR'),
                    'level': 'error'
                },
            ]
        }, 'ccdc443157fb49cd847faf00bb4e7e44', {'level': 'error'}
    )
])
@pytest.mark.asyncenv('blocking')
def test_get_by_link(code, expected, link_id, data, patch):
    @patch('taxiadmin.logreader.elasticsearch.get_request_details')
    def get_request_details(log_id, id_type, level=None, preference=None):
        return _prepare_request_info(DETAILS_ELASTIC_DATA, level=level)

    url = '/api/logs/%s/' % link_id
    response = django_test.Client().get(url, data=data)

    assert response.status_code == code
    if code == 200:
        assert json.loads(response.content) == expected


@pytest.mark.parametrize('code,expected,span_id,data', [
    (
        200,
        {
            'host': 'xiva-proxy-man-01.taxi.dev.yandex.net',
            'lang': 'json',
            'span_id': '30f40771c9f543d9a5b3a7a1dfb9ff30',
            'method': 'GET',
            'request_body': (
                '\u0422\u0435\u043b\u043e \u0437\u0430\u043f\u0440\u043e'
                '\u0441\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435'
                '\u043d\u043e, \u0432\u043e\u0437\u043c\u043e\u0436\u043d'
                '\u043e, \u043b\u043e\u0433\u0438\u0440\u043e\u0432\u0430'
                '\u043d\u0438\u0435 \u043e\u0442\u043a\u043b\u044e\u0447'
                '\u0435\u043d\u043e.'
            ),
            'response_body': '{ "status": "ok"}',
            'uri': '/ping',
            'useragent': 'KeepAliveClient',
            'logs': [
                {
                    'time': '2018-03-02T14:58:49.795000+0300',
                    'message': ('(useragent=KeepAliveClient, method=GET, remot'
                                'e_ip=2a02:6b8:0:e00::b16a) ERRRROOORRRR'),
                    'level': 'error'
                },
                {
                    'time': '2018-03-02T14:58:49.795000+0300',
                    'message': 'finish handling /ping',
                    'level': 'info'
                },
            ]
        },
        '30f40771c9f543d9a5b3a7a1dfb9ff30', {}
    )
])
@pytest.mark.asyncenv('blocking')
def test_get_by_span(code, expected, span_id, data, patch):
    @patch('taxiadmin.logreader.elasticsearch.get_request_details')
    def get_request_details(log_id, id_type, level=None, preference=None):
        return _prepare_request_info(DETAILS_ELASTIC_DATA, level=level)

    url = '/api/logs/by_span/%s/' % span_id
    response = django_test.Client().get(url, data=data)

    assert response.status_code == code
    if code == 200:
        assert json.loads(response.content) == expected


def _prepare_request_info(log, level=None):
    log = copy.deepcopy(log)
    request = None
    response = None
    logs = []
    for result in log['hits']['hits']:
        if result['_type'] == 'request':
            request = result['_source']
        elif result['_type'] == 'response':
            response = result['_source']
        else:
            logs.append(result['_source'])

    if request is None or response is None:
        message = '%s:%s' % (request, response)
        raise elasticsearch.NotFound(message)

    if response:
        keys_to_drop = set(response.keys())
    else:
        keys_to_drop = []

    messages = [
        {
            'time': dates.parse_timestring(l['@timestamp']),
            'message': _make_message(l, keys_to_drop),
            'level': l['level'].lower(),
        }
        for l in logs
        if not level or l['level'].lower() == level
    ]

    request_body = _decode(request.get('body'))
    response_body = _decode(response.get('body'))
    exception = _decode(response.get('exc_info'))
    return common.RequestInfo(
        request, response, messages, request_body, response_body, exception
    )


def _decode(string):
    if string is not None:
        return string.replace('\\n', '\n')
    else:
        return string


def _make_message(row, keys_to_drop):
    text = row.pop('text', '')
    pairs = []
    for k, v in row.iteritems():
        if k not in keys_to_drop:
            pairs.append('%s=%s' % (k, v))
    if pairs:
        extra = ', '.join(pairs)
        return '(%s) %s' % (extra, text)
    else:
        return text


@pytest.mark.parametrize('params,tracing_status,admin_status', [
    ({'span_id': '30f40771c9f543d9a5b3a7a1dfb9ff30'}, 200, 200),
    ({'span_id': '1234'}, 404, 404),
    ({}, None, 400)
])
@pytest.mark.asyncenv('blocking')
def test_tracing_span(areq_request, load, params, tracing_status, admin_status):
    if tracing_status == 200:
        expected = json.loads(load('expected_tracing_log.json'))
    else:
        expected = None

    @areq_request
    def tracing_api(method, url, **kwargs):
        assert method == 'POST'
        assert url == 'http://tracing.taxi.tst.yandex.net/v2/span_trace'
        assert kwargs['params'] == params
        if tracing_status == 200:
            return areq_request.response(tracing_status, json.dumps(expected))
        return areq_request.response(tracing_status)

    response = django_test.Client().get('/api/logs/tracing/span/', params)

    assert response.status_code == admin_status
    if response.status_code == 200:
        assert json.loads(response.content) == expected

    if tracing_status is not None:
        assert tracing_api.call


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('limit,offset,search,expected_ids,is_error_expected', [
    (None, None, None, [
        '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
        '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
        '21', '22', '23', '24', '25', '26', '27'
    ], False),
    (12, 0, None, [
        '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
        '11', '12'
    ], False),
    (2, 5, None, ['06', '07'], False),
    (5, 30, None, [], False),
    (-1, 0, None, [], True),
    (1, -1, None, [], True),
    (None, 5, None, [
        '06', '07', '08', '09', '10', '11', '12', '13', '14', '15',
        '16', '17', '18', '19', '20', '21', '22', '23', '24', '25',
        '26', '27'
    ], False),
    (5, None, None, ['01', '02', '03', '04', '05'], False),
    (None, None, 'type_1', ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19'], False),
    (5, 6, 'TYPE_0', ['07', '08', '09'], False)
])
def test_log_types_from_db(limit, offset, search, expected_ids, is_error_expected):
    params = {}
    if limit is not None:
        params['limit'] = limit
    if offset is not None:
        params['offset'] = offset
    if search is not None:
        params['type'] = search

    response = django_test.Client().get('/api/logs/types/list/', params)

    if is_error_expected:
        assert response.status_code == 400
        return

    expected = ['test_type_{}'.format(i) for i in expected_ids]

    content = json.loads(response.content)
    assert response.status_code == 200
    assert content == {'types': expected}
