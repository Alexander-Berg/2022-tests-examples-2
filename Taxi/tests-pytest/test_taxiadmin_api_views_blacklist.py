# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django import test as django_test
import pytest

from taxi.core import async
from taxi.core import db
from taxi.util import helpers


@pytest.mark.config(ADMIN_BLACKLIST_REASONS={
    'test_reason': {
        'title': 'test_reason_title',
        'park_email_tanker_key': '',
        'chat_message_tanker_key': '',
        'sms_tanker_key': '',
        'allow_subventions': True
    }
})
@pytest.mark.parametrize('key,data,code,expected', [
    (
        'add_0',
        {
            'reason': 'test_reason',
            'support_ticket': 'test_otr_ticket',
            'till': '2017-11-11',
        }, 404,
        None
    ),
    (
        'add_1',
        {
            'reason': 'test_reason',
            'support_ticket': 'test_otr_ticket',
            'till': '2017-11-11',
        }, 200,
        {
            'is_blacklisted': True,
            'blacklist_details': {
                'at': datetime.datetime(2017, 7, 20, 10, 0),
                'login': 'dmkurilov',
                'reason': 'test_reason_title',
                'otrs_ticket': 'test_otr_ticket',
                'till': datetime.datetime(2017, 11, 11, 21, 0),
            },
        }
    ),
    (
        'add_2',
        {
            'reason': 'test_reason',
            'support_ticket': 'test_otr_ticket',
        }, 200,
        {
            'is_blacklisted': True,
            'blacklist_details': {
                'at': datetime.datetime(2017, 7, 20, 10, 0),
                'login': 'dmkurilov',
                'reason': 'test_reason_title',
                'otrs_ticket': 'test_otr_ticket',
            },
        }
    ),
    (
        'add_2',
        {
            'otrs_ticket': 'test_otr_ticket',
        }, 400,
        None
    ),
    (
        'add_2',
        {
            'otrs_ticket': 'test_otr_ticket',
        }, 400,
        None
    ),
    (
        'add_2',
        {'arbitrary_reason': 'Random reason which i want to write'},
        200,
        {
            'is_blacklisted': True,
            'blacklist_details': {
                'at': datetime.datetime(2017, 7, 20, 10, 0),
                'login': 'dmkurilov',
                'reason': 'Random reason which i want to write',
            },
        }
    ),
])
@pytest.mark.now('2017-07-20T10:00:00.0')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_cars_blacklist_add(key, data, code, expected):
    car_url = '/api/blacklist/cars/add/'
    car_data = {'car_number': 'car_' + key}
    car_data.update(data)
    response = django_test.Client().post(
        car_url, json.dumps(car_data), 'application/json')
    assert response.status_code == code
    if expected is not None:
        normal_key = helpers.clean_number('car_' + key)
        car = yield db.cars.find_one(normal_key)
        assert car['is_blacklisted'] == expected['is_blacklisted']
        assert car['blacklist_details'] == expected['blacklist_details']


@pytest.mark.config(
    ADMIN_BLACKLIST_REASONS={
        'test_reason': {
            'title': 'test_reason_title',
            'park_email_tanker_key': '',
            'chat_message_tanker_key': '',
            'sms_tanker_key': '',
            'allow_subventions': True,
        }
    },
    ADMIN_BLACKLIST_BULK_MAX_NUMBER={
        'cars': 3,
        'drivers': 3,
    }
)
@pytest.mark.parametrize('keys,data,code,expected', [
    (
        ['add_1', 'add_2'],
        {
            'ticket': 'test_ticket',
            'reason': 'test_reason',
            'support_ticket': 'test_support_ticket',
        }, 200,
        {
            'is_blacklisted': True,
            'blacklist_details': {
                'at': datetime.datetime(2017, 7, 20, 10, 0),
                'login': 'dmkurilov',
                'reason': 'test_reason_title',
                'otrs_ticket': 'test_support_ticket',
            },
        }
    ),
    (
        ['add_1', 'add_2', 'eeee', 'frrfrf'],
        {
            'ticket': 'test_ticket',
            'reason': 'test_reason',
            'support_ticket': 'test_support_ticket',
        }, 400, None
    )
])
@pytest.mark.now('2017-07-20T10:00:00.0')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_cars_blacklist_add_bulk(keys, data, code, expected, patch):
    @patch('taxiadmin.audit.check_ticket')
    @async.inline_callbacks
    def check_ticket(*args, **kwargs):
        yield

    car_url = '/api/blacklist/cars/add_bulk/'

    car_data = {'car_numbers': ['car_' + key for key in keys]}
    car_data.update(data)
    response = django_test.Client().post(
        car_url, json.dumps(car_data), 'application/json')
    assert response.status_code == code
    if expected is not None:
        normal_keys = [
            helpers.clean_number('car_' + key) for key in keys
        ]
        cars = yield db.cars.find(
            {'_id': {'$in': normal_keys}}
        ).run()
        for car in cars:
            assert car['is_blacklisted'] == expected['is_blacklisted']
            assert car['blacklist_details'] == expected['blacklist_details']


@pytest.mark.parametrize('key', [
    'remove_0', 'remove_1'
])
@pytest.mark.now('2017-07-20T10:00:00.0')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_cars_blacklist_remove(key):
    car_url = '/api/blacklist/cars/remove/'
    car_data = {'car_number': 'car_' + key}
    response = django_test.Client().post(
        car_url, json.dumps(car_data), 'application/json')
    assert response.status_code == 200
    normal_key = helpers.clean_number('car_' + key)
    car = yield db.cars.find_one(normal_key)
    if car:
        assert 'is_blacklisted' not in car
        assert 'blacklist_details' not in car


@pytest.mark.parametrize('banned_drivers,banned_cars', [
    (
        {
            'DRIVER_BANNED_1': {
                'at': '2017-07-20T13:00:00+0300',
                'login': 'dmkurilov',
                'reason': 'test_reason_2',
                'support_ticket': 'test_otr_ticket_2',
                'till': 'перманентно'
            },
            'DRIVER_REMOVE_1': {
                'at': '2017-07-20T13:00:00+0300',
                'login': 'dmkurilov',
                'reason': 'test_reason',
                'support_ticket': 'test_otr_ticket',
                'till': 'перманентно'
            }
        },
        {
            'САR_RЕМОVЕ_1': {
                'at': '2017-07-20T13:00:00+0300',
                'login': 'dmkurilov',
                'reason': 'test_reason',
                'support_ticket': 'test_otr_ticket',
                'till': 'перманентно'
            }
        }
    ),
])
@pytest.mark.now('2017-07-20T10:00:00.0')
@pytest.mark.asyncenv('blocking')
def test_get_banned_cars(banned_drivers, banned_cars):
    car_url = '/api/blacklist/cars/'
    response = django_test.Client().get(car_url)
    banned_list = json.loads(response.content)
    for car in banned_list:
        number = car.pop('car_number')
        assert car == banned_cars[number]


@pytest.mark.parametrize('license,car_number,expected', [
    (
        'AB001', 'AA00077',
        {
            'reason_1': {
                'title': 'Причина №1',
                'allow_subventions': True,
                'ru': {
                    'park_email_text': 'Водитель с номером ВУ AB001 '
                                       'заблокирован',
                    'chat_message': 'Водитель с номером ВУ AB001 заблокирован',
                    'sms_text': 'Водитель с номером ВУ AB001 заблокирован'
                },
                'en': {
                    'park_email_text': 'Driver with license AB001 is '
                                       'blacklisted',
                    'chat_message': 'Driver with license AB001 is blacklisted',
                    'sms_text': 'Driver with license AB001 is blacklisted'
                }

            },
            'reason_2': {
                'title': 'Причина №2',
                'allow_subventions': True,
                'ru': {
                    'park_email_text': 'Вы заблокированы (номер автомобиля '
                                       'AA00077)',
                    'chat_message': 'Вы заблокированы (номер автомобиля'
                                    ' AA00077)',
                    'sms_text': 'Водитель с номером ВУ AB001 заблокирован'
                },
                'en': {
                    'park_email_text': 'You are banned',
                    'chat_message': 'You are banned',
                    'sms_text': 'Driver with license AB001 is blacklisted'
                }
            }
        }
    )
])
@pytest.mark.config(ADMIN_BLACKLIST_REASONS={
    'reason_1': {
        'title': 'Причина №1',
        'park_email_tanker_key': 'test_key_1',
        'chat_message_tanker_key': 'test_key_1',
        'sms_tanker_key': 'test_key_1',
        'allow_subventions': True,
    },
    'reason_2': {
        'title': 'Причина №2',
        'park_email_tanker_key': 'test_key_2',
        'chat_message_tanker_key': 'test_key_2',
        'sms_tanker_key': 'test_key_1',
        'allow_subventions': True,
    }
})
@pytest.mark.translations([
    ('taximeter_messages', 'test_key_1', 'ru',
     'Водитель с номером ВУ %(license)s заблокирован'),
    ('taximeter_messages', 'test_key_1', 'en',
     'Driver with license %(license)s is blacklisted'),
    ('taximeter_messages', 'test_key_2', 'ru',
     'Вы заблокированы (номер автомобиля %(car_number)s)'),
    ('taximeter_messages', 'test_key_2', 'en',
     'You are banned'),
])
@pytest.mark.asyncenv('blocking')
def test_get_blacklist_reasons(license, car_number, expected):
    response = django_test.Client().get(
        '/api/blacklist/reasons/?license=%s&car_number=%s' % (
            license, car_number
        )
    )
    assert json.loads(response.content) == expected
