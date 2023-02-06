# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import datetime

from django import test as django_test
import pytest

from taxi import config
from taxi.core import db
from taxi.core import async
from taxi.external import chatterbox
from taxi.external import startrack

CHATTERBOX_TASK_ID = '5b958ac184b597399c0dd9f7'
NEXT_CHATTERBOX_TASK_ID = '5b958ac184b597399c0dd9f8'
WRONG_TASK_ID = '5b958c5084b597399c0dd9f8'
STARTRACK_TICKET_ID = 'TESTQUEUE-123'


@pytest.fixture
def dummy_chatterbox(monkeypatch):
    def dummy_check_task(task_id, src_service, log_extra=None):
        if task_id == WRONG_TASK_ID:
            return False
        return True

    monkeypatch.setattr(chatterbox, 'check_task', dummy_check_task)


@pytest.fixture
def dummy_startrack(monkeypatch):
    def dummy_get_ticket(ticket, profile=None):
        if ticket == STARTRACK_TICKET_ID:
            return {}
        raise startrack.NotFoundError

    monkeypatch.setattr(startrack, 'get_ticket_info', dummy_get_ticket)


@pytest.mark.parametrize('params,expected_code,result', [
    ({}, 200, [
        {
            'created': '2018-06-19T10:00:00',
            'updated': '2018-06-19T10:00:00',
            'operator_login': 'piskarev',
            'zendesk_ticket': '1337',
            'series_id': 'sery',
            'comment': 'test',
            'code': '1337',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [{'reserve': 'a090181bf34643f2bcf73ac4de8f281a'}],
            'phone': '+79055675196',
        },
        {
            'code': '8731',
            'comment': 'test',
            'created': '2018-05-19T11:00:00',
            'operator_login': 'ivankolosov',
            'orders': [],
            'series_id': 'myseries',
            'updated': '2018-05-19T11:00:00',
            'zendesk_ticket': 'myticket',
            'phone_type': 'yandex',
        },
        {
            'created': '2018-05-19T10:00:00',
            'updated': '2018-05-19T10:00:00',
            'operator_login': 'piskarev',
            'zendesk_ticket': 'yataxi_123456',
            'series_id': 'sery',
            'comment': 'test',
            'code': '13377',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [],
            'phone': '+79055675196',
        },
        {
            'created': '2018-01-01T10:00:00',
            'updated': '2018-01-01T10:00:00',
            'operator_login': 'piskarev',
            'zendesk_ticket': CHATTERBOX_TASK_ID,
            'series_id': 'sery',
            'comment': 'test',
            'code': '123456',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [
                {
                    'reserve': '04fd85428ec4a835bc21b3dd',
                    'updated': '2017-05-01T13:00:00+0300',
                }
            ],
            'phone': '+79055675196',
        },
        {
            'created': '2016-12-23T00:00:00',
            'updated': '2016-12-23T00:00:00',
            'operator_login': 'piskarev12',
            'series_id': 'halyava2',
            'comment': 'ololo2',
            'code': '6543212',
            'orders': [],
            'phone': '+79251436219',
        },
        {
            'created': '2016-12-01T00:00:00',
            'updated': '2016-12-01T00:00:00',
            'operator_login': 'piskarev1',
            'series_id': 'halyava',
            'comment': 'ololo',
            'code': '654321',
            'value': 122,
            'user_limit': 2,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [],
            'phone': '+79251436219',
        },
        {
            'code': '8732',
            'comment': 'test',
            'created': '2015-05-19T10:00:00',
            'operator_login': 'ivankolosov',
            'orders': [],
            'phone_type': 'uber',
            'series_id': 'myseries',
            'updated': '2015-05-19T10:00:00',
            'zendesk_ticket': 'myticket',
        },
    ]),
    ({'code': '123456'}, 200, [
        {
            'created': '2018-01-01T10:00:00',
            'updated': '2018-01-01T10:00:00',
            'operator_login': 'piskarev',
            'series_id': 'sery',
            'comment': 'test',
            'zendesk_ticket': CHATTERBOX_TASK_ID,
            'code': '123456',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [
                {
                    'reserve': '04fd85428ec4a835bc21b3dd',
                    'updated': '2017-05-01T13:00:00+0300',
                }
            ],
            'phone': '+79055675196',
        }
    ]),
    # part of operator login
    ({'operator_login': 'Piskarev'}, 200, [
        {
            'created': '2018-06-19T10:00:00',
            'updated': '2018-06-19T10:00:00',
            'operator_login': 'piskarev',
            'zendesk_ticket': '1337',
            'series_id': 'sery',
            'comment': 'test',
            'code': '1337',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [{'reserve': 'a090181bf34643f2bcf73ac4de8f281a'}],
            'phone': '+79055675196',
        },
        {
            'created': '2018-05-19T10:00:00',
            'updated': '2018-05-19T10:00:00',
            'operator_login': 'piskarev',
            'zendesk_ticket': 'yataxi_123456',
            'series_id': 'sery',
            'comment': 'test',
            'code': '13377',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [],
            'phone': '+79055675196',
        },
        {
            'created': '2018-01-01T10:00:00',
            'updated': '2018-01-01T10:00:00',
            'operator_login': 'piskarev',
            'series_id': 'sery',
            'comment': 'test',
            'zendesk_ticket': CHATTERBOX_TASK_ID,
            'code': '123456',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [
                {
                    'reserve': '04fd85428ec4a835bc21b3dd',
                    'updated': '2017-05-01T13:00:00+0300',
                }
            ],
            'phone': '+79055675196',
        },
        {
            'created': '2016-12-23T00:00:00',
            'updated': '2016-12-23T00:00:00',
            'operator_login': 'piskarev12',
            'series_id': 'halyava2',
            'comment': 'ololo2',
            'code': '6543212',
            'orders': [],
            'phone': '+79251436219',
        },
        {
            'created': '2016-12-01T00:00:00',
            'updated': '2016-12-01T00:00:00',
            'operator_login': 'piskarev1',
            'series_id': 'halyava',
            'comment': 'ololo',
            'code': '654321',
            'value': 122,
            'user_limit': 2,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [],
            'phone': '+79251436219',
        },
    ]),
    ({'series_id': 'sery'}, 200, [
        {
            'created': '2018-06-19T10:00:00',
            'updated': '2018-06-19T10:00:00',
            'operator_login': 'piskarev',
            'zendesk_ticket': '1337',
            'series_id': 'sery',
            'comment': 'test',
            'code': '1337',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [{'reserve': 'a090181bf34643f2bcf73ac4de8f281a'}],
            'phone': '+79055675196',
        },
        {
            'created': '2018-05-19T10:00:00',
            'updated': '2018-05-19T10:00:00',
            'operator_login': 'piskarev',
            'zendesk_ticket': 'yataxi_123456',
            'series_id': 'sery',
            'comment': 'test',
            'code': '13377',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [],
            'phone': '+79055675196',
        },
        {
            'created': '2018-01-01T10:00:00',
            'updated': '2018-01-01T10:00:00',
            'operator_login': 'piskarev',
            'zendesk_ticket': CHATTERBOX_TASK_ID,
            'series_id': 'sery',
            'comment': 'test',
            'code': '123456',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [
                {
                    'reserve': '04fd85428ec4a835bc21b3dd',
                    'updated': '2017-05-01T13:00:00+0300',
                }
            ],
            'phone': '+79055675196',
        }
    ]),
    ({'created_after': '2016-12-1T03:00:01+0300'}, 200, [
        {
            'created': '2018-06-19T10:00:00',
            'updated': '2018-06-19T10:00:00',
            'operator_login': 'piskarev',
            'zendesk_ticket': '1337',
            'series_id': 'sery',
            'comment': 'test',
            'code': '1337',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [{'reserve': 'a090181bf34643f2bcf73ac4de8f281a'}],
            'phone': '+79055675196',
        },
        {
            'code': '8731',
            'comment': 'test',
            'created': '2018-05-19T11:00:00',
            'operator_login': 'ivankolosov',
            'orders': [],
            'series_id': 'myseries',
            'updated': '2018-05-19T11:00:00',
            'zendesk_ticket': 'myticket',
            'phone_type': 'yandex',
        },
        {
            'created': '2018-05-19T10:00:00',
            'updated': '2018-05-19T10:00:00',
            'operator_login': 'piskarev',
            'zendesk_ticket': 'yataxi_123456',
            'series_id': 'sery',
            'comment': 'test',
            'code': '13377',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [],
            'phone': '+79055675196',
        },
        {
            'created': '2018-01-01T10:00:00',
            'updated': '2018-01-01T10:00:00',
            'operator_login': 'piskarev',
            'zendesk_ticket': CHATTERBOX_TASK_ID,
            'series_id': 'sery',
            'comment': 'test',
            'code': '123456',
            'value': 250,
            'user_limit': 1,
            'currency': 'RUB',
            'localized_currency': 'руб.',
            'orders': [
                {
                    'reserve': '04fd85428ec4a835bc21b3dd',
                    'updated': '2017-05-01T13:00:00+0300',
                }
            ],
            'phone': '+79055675196',
        },
        {
          "operator_login": "piskarev12",
          "comment": "ololo2",
          "updated": "2016-12-23T00:00:00",
          "code": "6543212",
          "created": "2016-12-23T00:00:00",
          "series_id": "halyava2",
          "phone": "+79251436219",
          "orders": []
        },
    ]),
    (
        {
            'created_after': '2018-01-01T03:00:01+0300',
            'created_before': '2018-02-02T03:00:01+0300'
        }, 200, [
            {
                'created': '2018-01-01T10:00:00',
                'updated': '2018-01-01T10:00:00',
                'operator_login': 'piskarev',
                'zendesk_ticket': CHATTERBOX_TASK_ID,
                'series_id': 'sery',
                'comment': 'test',
                'code': '123456',
                'value': 250,
                'user_limit': 1,
                'currency': 'RUB',
                'localized_currency': 'руб.',
                'orders': [
                    {
                        'reserve': '04fd85428ec4a835bc21b3dd',
                        'updated': '2017-05-01T13:00:00+0300',
                    }
                ],
                'phone': '+79055675196',
            }
    ]),
    # phone number without leading '+' is valid
    (
        {'phone': '79261111111'},
        200,
        [],
    ),
    # phone number without leading '+' is valid
    (
        {'phone': '380000000000'},
        200,
        [],
    ),
    # nonexistent phone number should yield empty set
    (
        {'phone': '+79261111111'},
        200,
        [],
    ),
    # existing phone number should yield promocodes bound to it
    (
        {'phone': '+79251436219'},
        200,
        [
            {
                'created': '2016-12-23T00:00:00',
                'updated': '2016-12-23T00:00:00',
                'operator_login': 'piskarev12',
                'series_id': 'halyava2',
                'comment': 'ololo2',
                'code': '6543212',
                'orders': [],
                'phone': '+79251436219',
            },
            {
                'created': '2016-12-01T00:00:00',
                'updated': '2016-12-01T00:00:00',
                'operator_login': 'piskarev1',
                'series_id': 'halyava',
                'comment': 'ololo',
                'code': '654321',
                'value': 122,
                'user_limit': 2,
                'currency': 'RUB',
                'localized_currency': 'руб.',
                'orders': [],
                'phone': '+79251436219',
            },
        ],
    ),
    # the same number with garbage characters
    (
        {'phone': '+7 (925) 143-62-19'},
        200,
        [
            {
                'created': '2016-12-23T00:00:00',
                'updated': '2016-12-23T00:00:00',
                'operator_login': 'piskarev12',
                'series_id': 'halyava2',
                'comment': 'ololo2',
                'code': '6543212',
                'orders': [],
                'phone': '+79251436219',
            },
            {
                'created': '2016-12-01T00:00:00',
                'updated': '2016-12-01T00:00:00',
                'operator_login': 'piskarev1',
                'series_id': 'halyava',
                'comment': 'ololo',
                'code': '654321',
                'value': 122,
                'user_limit': 2,
                'currency': 'RUB',
                'localized_currency': 'руб.',
                'orders': [],
                'phone': '+79251436219',
            },
        ],
    ),
    # the same number starting with 8
    (
        {'phone': '8 925 143-62-19'},
        200,
        [
            {
                'created': '2016-12-23T00:00:00',
                'updated': '2016-12-23T00:00:00',
                'operator_login': 'piskarev12',
                'series_id': 'halyava2',
                'comment': 'ololo2',
                'code': '6543212',
                'orders': [],
                'phone': '+79251436219',
            },
            {
                'created': '2016-12-01T00:00:00',
                'updated': '2016-12-01T00:00:00',
                'operator_login': 'piskarev1',
                'series_id': 'halyava',
                'comment': 'ololo',
                'code': '654321',
                'value': 122,
                'user_limit': 2,
                'currency': 'RUB',
                'localized_currency': 'руб.',
                'orders': [],
                'phone': '+79251436219',
            },
        ],
    ),
    # the same number starting with 7
    (
        {'phone': '7 925 143-62-19'},
        200,
        [
            {
                'created': '2016-12-23T00:00:00',
                'updated': '2016-12-23T00:00:00',
                'operator_login': 'piskarev12',
                'series_id': 'halyava2',
                'comment': 'ololo2',
                'code': '6543212',
                'orders': [],
                'phone': '+79251436219',
            },
            {
                'created': '2016-12-01T00:00:00',
                'updated': '2016-12-01T00:00:00',
                'operator_login': 'piskarev1',
                'series_id': 'halyava',
                'comment': 'ololo',
                'code': '654321',
                'value': 122,
                'user_limit': 2,
                'currency': 'RUB',
                'localized_currency': 'руб.',
                'orders': [],
                'phone': '+79251436219',
            },
        ],
    ),
    # part of code
    (
        {'code': '33'},
        200,
        [
            {
                'created': '2018-06-19T10:00:00',
                'updated': '2018-06-19T10:00:00',
                'operator_login': 'piskarev',
                'zendesk_ticket': '1337',
                'series_id': 'sery',
                'comment': 'test',
                'code': '1337',
                'value': 250,
                'user_limit': 1,
                'currency': 'RUB',
                'localized_currency': 'руб.',
                'orders': [{'reserve': 'a090181bf34643f2bcf73ac4de8f281a'}],
                'phone': '+79055675196',
            },
            {
                'created': '2018-05-19T10:00:00',
                'updated': '2018-05-19T10:00:00',
                'operator_login': 'piskarev',
                'zendesk_ticket': 'yataxi_123456',
                'series_id': 'sery',
                'comment': 'test',
                'code': '13377',
                'value': 250,
                'user_limit': 1,
                'currency': 'RUB',
                'localized_currency': 'руб.',
                'orders': [],
                'phone': '+79055675196',
            },
        ],
    ),
    # part of series
    (
        {'series_id': 'lya'},
        200,
        [
            {
                'created': '2016-12-23T00:00:00',
                'updated': '2016-12-23T00:00:00',
                'operator_login': 'piskarev12',
                'series_id': 'halyava2',
                'comment': 'ololo2',
                'code': '6543212',
                'orders': [],
                'phone': '+79251436219',
            },
            {
                'created': '2016-12-01T00:00:00',
                'updated': '2016-12-01T00:00:00',
                'operator_login': 'piskarev1',
                'series_id': 'halyava',
                'comment': 'ololo',
                'code': '654321',
                'value': 122,
                'user_limit': 2,
                'currency': 'RUB',
                'localized_currency': 'руб.',
                'orders': [],
                'phone': '+79251436219',
            },
        ],
    ),
    # part of series, with uppercase letters
    (
        {'series_id': 'LyA'},
        200,
        [
            {
                'created': '2016-12-23T00:00:00',
                'updated': '2016-12-23T00:00:00',
                'operator_login': 'piskarev12',
                'series_id': 'halyava2',
                'comment': 'ololo2',
                'code': '6543212',
                'orders': [],
                'phone': '+79251436219',
            },
            {
                'created': '2016-12-01T00:00:00',
                'updated': '2016-12-01T00:00:00',
                'operator_login': 'piskarev1',
                'series_id': 'halyava',
                'comment': 'ololo',
                'code': '654321',
                'value': 122,
                'user_limit': 2,
                'currency': 'RUB',
                'localized_currency': 'руб.',
                'orders': [],
                'phone': '+79251436219',
            },
        ],
    ),
    # ticket
    (
        {'zendesk_ticket': CHATTERBOX_TASK_ID},
        200,
        [
            {
                'created': '2018-01-01T10:00:00',
                'updated': '2018-01-01T10:00:00',
                'operator_login': 'piskarev',
                'zendesk_ticket': CHATTERBOX_TASK_ID,
                'series_id': 'sery',
                'comment': 'test',
                'code': '123456',
                'value': 250,
                'user_limit': 1,
                'currency': 'RUB',
                'localized_currency': 'руб.',
                'orders': [
                    {
                        'reserve': '04fd85428ec4a835bc21b3dd',
                        'updated': '2017-05-01T13:00:00+0300',
                    }
                ],
                'phone': '+79055675196',
            },
        ],
    ),
    (
        {'phone_type': 'yandex'},
        200,
        [
            {
                'code': '8731',
                'comment': 'test',
                'created': '2018-05-19T11:00:00',
                'operator_login': 'ivankolosov',
                'orders': [],
                'series_id': 'myseries',
                'updated': '2018-05-19T11:00:00',
                'zendesk_ticket': 'myticket',
                'phone_type': 'yandex',
            },
        ],
    ),
    (
        {'phone_type': 'uber'},
        200,
        [
            {
                'code': '8732',
                'comment': 'test',
                'created': '2015-05-19T10:00:00',
                'operator_login': 'ivankolosov',
                'orders': [],
                'phone_type': 'uber',
                'series_id': 'myseries',
                'updated': '2015-05-19T10:00:00',
                'zendesk_ticket': 'myticket',
            },
        ],
    ),
    (
        {'phone_type': 'nosuchtaxiever'},
        400,
        None,
    ),
])
@pytest.mark.translations([
    ('tariff', 'currency.rub', 'ru', 'руб.'),
])
@pytest.mark.asyncenv('blocking')
def test_api_support_promocodes_list(params, expected_code, result):
    response = django_test.Client().get(
        '/api/support_promocodes/list/', params
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response = json.loads(response.content)
        assert result == response['support_promocodes']


@pytest.mark.translations([
    ('tariff', 'currency.rub', 'ru', 'руб.'),
])
@pytest.mark.asyncenv('blocking')
def test_api_support_promocodes_list_w_limit():
    response = django_test.Client().get(
        '/api/support_promocodes/list/?offset=3;limit=1'
    )
    assert response.status_code == 200

    response = json.loads(response.content)

    assert len(response['support_promocodes']) == 1
    assert {
        'operator_login': 'piskarev',
        'comment': 'test',
        'updated': '2018-01-01T10:00:00',
        'code': '123456',
        'localized_currency': 'руб.',
        'zendesk_ticket': CHATTERBOX_TASK_ID,
        'created': '2018-01-01T10:00:00',
        'value': 250,
        'series_id': 'sery',
        'phone': '+79055675196',
        'user_limit': 1,
        'currency': 'RUB',
        'orders': [
           {
               'reserve': '04fd85428ec4a835bc21b3dd',
               'updated': '2017-05-01T13:00:00+0300',
           }
        ],
    } in response['support_promocodes']


# Generate support promocode
@pytest.mark.parametrize(
    'phone,phone_type,zendesk_ticket,expected_code,phone_count',
    [
        # no such phone yet
        ('+79162623362', 'uber', CHATTERBOX_TASK_ID, 200, 1),
        # existing Uber phone
        ('+79162623363', 'uber', CHATTERBOX_TASK_ID, 200, 1),
        # existing Yandex phone
        ('+79162623364', 'yandex', CHATTERBOX_TASK_ID, 200, 1),
        # existing Yandex phone (without type field)
        ('+79162623365', 'yandex', CHATTERBOX_TASK_ID, 200, 1),
        # no such phone yet, and it's too short for Russia, but OK for Estonia
        ('+3722623365', 'uber', CHATTERBOX_TASK_ID, 200, 1),
        # ticket id with whitespaces
        ('+79162623365', 'yandex', '  {} '.format(CHATTERBOX_TASK_ID), 200, 1),
        # ticket id with whitespaces
        ('+3722623365', 'uber', ' {} \t\r'.format(CHATTERBOX_TASK_ID), 200, 1),
        # Belize phone number (no such country)
        ('+5012623365', 'uber', CHATTERBOX_TASK_ID, 400, None),
        # Phone number without leading plus sign
        ('3722623365', 'uber', CHATTERBOX_TASK_ID, 400, None),
        # Chatterbox ticket
        ('+79162623362', 'yandex', CHATTERBOX_TASK_ID, 200, 1),
        # Startrack ticket
        ('+79162623362', 'yandex', STARTRACK_TICKET_ID, 200, 1),
        # Chatterbox ticket
        ('+79162623362', 'yandex', CHATTERBOX_TASK_ID + '  \t\n', 200, 1),
        # Startrack ticket
        ('+79162623362', 'yandex', '\t\n' + STARTRACK_TICKET_ID, 200, 1),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True)
@pytest.mark.now('2016-05-31 15:30:00+03')
@pytest.mark.parametrize("use_coupons", [True, False])
@pytest.inline_callbacks
def test_api_support_promocodes_generate(
        patch, phone, phone_type, zendesk_ticket, expected_code, phone_count,
        dummy_chatterbox, dummy_startrack,
        use_coupons_exp3, use_coupons, coupons_count, coupons_insert):
    use_coupons_exp3(use_coupons)

    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        yield
        async.return_value({'id': 'personal_id', 'phone': value})

    response = django_test.Client().get(
        '/api/support_promocodes/generate/',
    )
    assert response.status_code == 405

    new_promocode = {
        'series_id': 'halyava',
        'phone': phone,
        'comment': 'ololo',
        'zendesk_ticket': zendesk_ticket,
        'phone_type': phone_type,
    }

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(new_promocode),
        'application/json',
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        response = json.loads(response.content)

        inserted_promocode = yield db.secondary.support_promocodes.find_one(
            {
                'code': response['code'],
            },
        )
        assert inserted_promocode is not None

        unique_promocode = yield db.secondary.promocodes.find_one(
            {
                'code': inserted_promocode['code'],
            },
        )
        assert unique_promocode is not None
        assert unique_promocode['updated_at'] == datetime.datetime(2016, 5, 31, 12, 30)

        user_phone = yield db.secondary.user_phones.find_one(
            {
                '_id': unique_promocode['phone_id'],
            }
        )
        assert user_phone is not None
        assert user_phone.get('type', 'yandex') == new_promocode['phone_type']

        assert new_promocode['series_id'] == inserted_promocode['series_id']
        assert new_promocode['phone_type'] == inserted_promocode['phone_type']
        assert new_promocode['phone'] == user_phone['phone']
        actual_phone_count = yield db.secondary.user_phones.find({
            'phone': user_phone['phone']}
        ).count()
        assert phone_count == actual_phone_count


@pytest.mark.config(SUPPORT_PROMOCODE_ACCESS_BY_COUNTRY=True)
@pytest.mark.config(SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True)
@pytest.mark.parametrize(
    'permissions, expected_code',
    [
        (
            {},
            403
        ),
        (
            {
                'edit_support_promocodes': {
                    'mode': 'unrestricted'
                }
            },
            200
        ),
        (
            {
                'edit_support_promocodes': {
                    'mode': 'countries_filter',
                    'countries_filter': {'rus'}
                }
            },
            200
        ),
        (
            {
                'edit_support_promocodes': {
                    'mode': 'countries_filter',
                    'countries_filter': {'civ'}
                }
            },
            406
        )
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize("use_coupons", [True, False])
@pytest.inline_callbacks
def test_api_support_promocodes_generate_by_country(
    dummy_chatterbox, patch, permissions, expected_code,
    use_coupons_exp3, use_coupons, coupons_count, coupons_insert
):
    use_coupons_exp3(use_coupons)

    @patch('taxiadmin.permissions.get_user_permissions')
    @async.inline_callbacks
    def get_user_permissions(request):
        yield
        async.return_value(
            permissions
        )

    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        yield
        async.return_value({'id': 'personal_id', 'phone': value})

    promocode = {
        'series_id': 'halyava',
        'phone': '+79162623362',
        'comment': 'ololo',
        'zendesk_ticket': CHATTERBOX_TASK_ID,
        'phone_type': 'uber',
    }

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(promocode),
        'application/json',
    )
    yield
    assert response.status_code == expected_code


# Load series list
@pytest.mark.parametrize('data, expected_data', [
    (
        {},
        [
            {
                'id': 'sery2',
                'value': 150,
                'currency': 'RUB',
                'descr': 'descr',
            },
            {
                'id': 'sery',
                'value': 250,
                'currency': 'RUB',
                'descr': 'descr',
            },
            {
                'id': 'sery3',
                'value': 50,
                'currency': 'USD',
                'descr': 'descr',
            },
        ]
    ),
    (
            {
                'value_from': 100,
                'value_to': 200,
            },
            [
                {
                    'id': 'sery2',
                    'value': 150,
                    'currency': 'RUB',
                    'descr': 'descr',
                },
            ]
    ),
    (
            {
                'value_from': 200,
            },
            [
                {
                    'id': 'sery',
                    'value': 250,
                    'currency': 'RUB',
                    'descr': 'descr',
                },
            ]
    ),
    (
            {'currency': 'USD'},
            [
                {
                    'id': 'sery3',
                    'value': 50,
                    'currency': 'USD',
                    'descr': 'descr',
                },
            ]
    ),
])
@pytest.mark.asyncenv('blocking')
def test_series_list(data, expected_data):
    response = django_test.Client().post(
        '/api/support_promocodes/series/search/',
        json.dumps(data),
        'application/json',
    )
    assert response.status_code == 200

    response = json.loads(response.content)
    assert response == expected_data


# Must not generate support promocode because ticket limit exceeded
@pytest.mark.config(
    SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True,
    SUPPORT_PROMOCODE_GENERATIONS_LIMIT_PER_TICKET=1,
)
@pytest.mark.asyncenv('blocking')
def test_api_support_promocodes_generate_user_limit_exceeded(
        patch, dummy_chatterbox):
    new_promocode = {
        'series_id': 'sery',
        'phone': '+79162623362',
        'comment': 'ololo',
        'zendesk_ticket': CHATTERBOX_TASK_ID,
    }

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(new_promocode),
        'application/json',
    )

    assert response.status_code == 406


# Must not generate support promocode because daily limit exceeded
@pytest.mark.config(
    SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True,
    SUPPORT_PROMOCODE_GENERATIONS_DAILY_LIMIT=1,
)
@pytest.mark.now('2018-01-01T10:00:00')
@pytest.mark.asyncenv('blocking')
def test_api_support_promocodes_generate_daily_limit_exceeded(
        patch, dummy_chatterbox):

    new_promocode = {
        'series_id': 'sery',
        'phone': '+79162623362',
        'comment': 'ololo',
        'zendesk_ticket': CHATTERBOX_TASK_ID,
    }

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(new_promocode),
        'application/json',
    )

    assert response.status_code == 406


# Must not generate support promocode because ticket does not exist
@pytest.mark.config(
    SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True,
)
@pytest.mark.asyncenv('blocking')
def test_api_support_promocodes_generate_wrong_ticket(patch, dummy_chatterbox):

    new_promocode = {
        'series_id': 'sery',
        'phone': '+79162623362',
        'comment': 'ololo',
        'zendesk_ticket': '123123',
    }

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(new_promocode),
        'application/json',
    )

    assert response.status_code == 406


@pytest.mark.config(
    SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True,
)
@pytest.mark.asyncenv('blocking')
def test_api_support_promocodes_generate_wrong_chatterbox_task_id(
        patch, dummy_chatterbox):

    new_promocode = {
        'series_id': 'sery',
        'phone': '+79162623362',
        'comment': 'ololo',
        'zendesk_ticket': WRONG_TASK_ID,
    }

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(new_promocode),
        'application/json',
    )

    assert response.status_code == 406


@pytest.mark.config(
    SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True,
    STRICT_CHECK_FINANCE_TICKET=True,
)
@pytest.mark.asyncenv('blocking')
def test_api_support_promocodes_generate_wrong_chatterbox_task_id_strict(
        patch, dummy_chatterbox):

    new_promocode = {
        'series_id': 'sery',
        'phone': '+79162623362',
        'comment': 'ololo',
        'zendesk_ticket': WRONG_TASK_ID,
        'ticket_type': chatterbox.CHATTERBOX_TICKET_TYPE,
    }

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(new_promocode),
        'application/json',
    )

    assert response.status_code == 406


@pytest.mark.config(
    SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True,
    STRICT_CHECK_FINANCE_TICKET=True,
)
@pytest.mark.asyncenv('blocking')
def test_api_support_promocodes_generate_ticket_type_missing(dummy_chatterbox):
    new_promocode = {
        'series_id': 'sery',
        'phone': '+79162623362',
        'comment': 'ololo',
        'zendesk_ticket': CHATTERBOX_TASK_ID,
    }

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(new_promocode),
        'application/json',
    )

    assert response.status_code == 406


@pytest.mark.asyncenv('blocking')
def test_api_support_promocodes_generate_conflict(dummy_chatterbox):
    new_promocode = {
        'series_id': 'some-yandex-series',
        'phone': '+79162623362',
        'comment': 'ololo',
        'zendesk_ticket': CHATTERBOX_TASK_ID,
        'phone_type': 'uber',
    }
    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(new_promocode),
        'application/json',
    )
    assert response.status_code == 409

    new_promocode = {
        'series_id': 'some-uber-series',
        'phone': '+79162623362',
        'comment': 'ololo',
        'zendesk_ticket': CHATTERBOX_TASK_ID,
        'phone_type': 'yandex',
    }
    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(new_promocode),
        'application/json',
    )
    assert response.status_code == 409


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True)
def test_api_support_promocodes_bad_series(patch, dummy_chatterbox):
    data = {
        'series_id': 'not-existing-series',
        'phone': '+79162623362',
        'comment': 'ololo',
        'zendesk_ticket': CHATTERBOX_TASK_ID,
        'phone_type': 'yandex',
    }

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(data),
        'application/json',
    )

    assert response.status_code == 406


@pytest.mark.parametrize('data, expected_code', [
    (
        {
            'series_id': 'sery2',
            'phone': '+79162623362',
            'comment': 'ololo',
            'zendesk_ticket': NEXT_CHATTERBOX_TASK_ID,
        },
        200
    ),
    (
        {
            'series_id': 'sery',
            'phone': '+79162623362',
            'comment': 'ololo',
            'zendesk_ticket': CHATTERBOX_TASK_ID,
        },
        406
    ),
    (
        {
            'series_id': 'sery',
            'phone': '+79162623362',
            'comment': 'ololo',
            'zendesk_ticket': WRONG_TASK_ID,
        },
        406
    ),
])
@pytest.mark.config(
    SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True,
    SUPPORT_PROMOCODE_GENERATIONS_LIMIT_PER_TICKET=1
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize("use_coupons", [True, False])
def test_api_support_promocodes_check_ticket(
    patch, data, expected_code, dummy_chatterbox,
    use_coupons_exp3, use_coupons, coupons_count, coupons_insert
):
    use_coupons_exp3(use_coupons)

    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        yield
        async.return_value({'id': 'personal_id', 'phone': value})

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(data),
        'application/json',
    )

    assert response.status_code == expected_code


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True)
@pytest.mark.parametrize("use_coupons", [True, False])
@pytest.inline_callbacks
def test_chatterbox_api_generate(
    patch,
    dummy_chatterbox,
    use_coupons_exp3,
    coupons_insert,
    coupons_count,
    use_coupons
):
    use_coupons_exp3(use_coupons)

    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        yield
        async.return_value({'id': 'personal_id', 'phone': value})

    new_promocode = {
        'series_id': 'halyava',
        'phone': '+79162623362',
        'comment': 'ololo',
        'zendesk_ticket': CHATTERBOX_TASK_ID,
        'phone_type': 'yandex',
    }

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(new_promocode),
        'application/json',
        HTTP_X_YATAXI_API_KEY='test_token',
    )
    assert response.status_code == 200

    response = json.loads(response.content)

    inserted_promocode = yield db.secondary.support_promocodes.find_one(
        {
            'code': response['code'],
        },
    )
    assert inserted_promocode is not None

    unique_promocode = yield db.secondary.promocodes.find_one(
        {
            'code': inserted_promocode['code'],
        },
    )
    assert unique_promocode is not None

    user_phone = yield db.secondary.user_phones.find_one(
        {
            '_id': unique_promocode['phone_id'],
        }
    )
    assert user_phone is not None
    assert user_phone.get('type', 'yandex') == new_promocode['phone_type']

    assert new_promocode['series_id'] == inserted_promocode['series_id']
    assert new_promocode['phone_type'] == inserted_promocode['phone_type']
    assert new_promocode['phone'] == user_phone['phone']
    assert inserted_promocode['operator_login'] == 'some_robot_login'
    actual_phone_count = yield db.secondary.user_phones.find({
        'phone': user_phone['phone']}
    ).count()
    assert actual_phone_count == 1


@pytest.mark.config(SUPPORT_PROMOCODE_ACCESS_BY_COUNTRY=True)
@pytest.mark.filldb(support_promocodes='countries')
@pytest.mark.filldb(promocode_series='countries')
@pytest.mark.translations([
    ('tariff', 'currency.rub', 'ru', 'руб.'),
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('permissions, request_data, expected_code, '
                         'expected', [
    ({}, {}, 403, None),
    (
        {
            'view_support_promocodes': {
                'mode': 'unrestricted'
            }
        },
        {},
        200,
        [
            {'series_id': 's1', 'code': '1'},
            {'series_id': 's1', 'code': '2'},
            {'series_id': 's2', 'code': '3'},
        ]
    ),
    (
            {
                'view_support_promocodes': {
                    'mode': 'countries_filter',
                    'countries_filter': {'rus'}
                }
            },
            {},
            200,
            [
                {'series_id': 's1', 'code': '1'},
                {'series_id': 's1', 'code': '2'},
            ]
    ),
    (
            {
                'view_support_promocodes': {
                    'mode': 'countries_filter',
                    'countries_filter': {'civ'}
                }
            },
            {},
            200,
            [
                {'series_id': 's2', 'code': '3'}
            ]
    ),
    (
            {
                'view_support_promocodes': {
                    'mode': 'countries_filter',
                    'countries_filter': {'rus'}
                }
            },
            {
                'series_id': 's1'
            },
            200,
            [
                {'series_id': 's1', 'code': '1'},
                {'series_id': 's1', 'code': '2'},
            ]
    ),
    (
            {
                'view_support_promocodes': {
                    'mode': 'countries_filter',
                    'countries_filter': {'rus'}
                }
            },
            {
                'series_id': 's2'
            },
            200,
            []
    )
])
def test_support_promocode_list_by_country(patch, request_data, permissions,
                                           expected_code, expected):
    @patch('taxiadmin.permissions.get_user_permissions')
    @async.inline_callbacks
    def get_user_permissions(request):
        yield
        async.return_value(
            permissions
        )

    response = django_test.Client().get(
        '/api/support_promocodes/list/', request_data
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        promocodes = json.loads(response.content)['support_promocodes']
        assert len(promocodes) == len(expected)
        for promo, expected_promo in zip(promocodes, expected):
            assert promo['series_id'] == expected_promo['series_id']
            assert promo['code'] == expected_promo['code']


@pytest.mark.config(
    SUPPORT_PROMOCODE_GENERATION_ZENDESK_TICKET_REQUIRED=True,
    SUPPORT_PROMOCODE_GENERATIONS_LIMIT_PER_TICKET=1,
    SUPPORT_PROMOCODE_GENERATION_RETRY_LIMIT=10,
    SUPPORT_PROMOCODE_LENGTH=2
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize("use_coupons", [True, False])
@pytest.inline_callbacks
def test_api_support_promocodes_max_retry(
    patch,
    dummy_chatterbox,
    use_coupons_exp3,
    coupons_insert,
    coupons_count,
    use_coupons
):
    use_coupons_exp3(use_coupons)

    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        yield
        async.return_value({'id': 'personal_id', 'phone': value})

    series = 'sery'
    max_length_code = yield config.SUPPORT_PROMOCODE_LENGTH.get()
    # generate all promocodes in series
    for code in xrange(1, 10 ** max_length_code):
        doc = {
            'series_id': series,
            'code': series + str(code).zfill(max_length_code),
            'value': 100,
        }
        db.promocodes.insert(doc)

    new_promocode = {
        'series_id': series,
        'phone': '+79160000001',
        'comment': 'ololo',
        'zendesk_ticket': NEXT_CHATTERBOX_TASK_ID,
    }

    response = django_test.Client().post(
        '/api/support_promocodes/generate/',
        json.dumps(new_promocode),
        'application/json',
    )
    assert response.status_code == 406
    text = json.loads(response.content)['message']
    assert 'Can\'t create unique promocode series \'sery\' in 10 retry' == text
