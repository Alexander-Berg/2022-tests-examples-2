# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import json

from bson import ObjectId

import pytest

from django import test as django_test
from django.core.files import uploadedfile

from taxi.core import async
from taxi.core import db
from taxi.external import archive
from taxi.external import userapi
from taxi.util import dates


EMPTY_DICT = {}
REQUEST_LOGIN = 'dmkurilov'
TICKET = 'TAXIRATE-1'


def get_collection_from_type(type):
    if type == 'phone' or type == 'phone_id':
        return db.antifraud_stat_phones
    elif type == 'user':
        return db.antifraud_stat_users
    elif type == 'device':
        return db.antifraud_stat_devices

    assert False


def _stat_type_by_ban_type(ban_type):
    return {
        'phone': 'phone_id',
        'phone_id': 'phone_id',
        'user': 'user_id',
        'device': 'device_id',
    }[ban_type]


def _check_equal_field(field1, dict1, dict2, field2=None):
    if field2 is None:
        field2 = field1
    if field1 in dict1:
        assert dict1[field1] == dict2[field2]
    else:
        assert field2 not in dict2


@pytest.mark.config(
    SVO_PHONE='+70000000000',
    SVO_USER_ID='297d52da8caf4b5f86abf4cbd58e5a88',
    AFS_USER_BAN_DEFAULT_DURATION={
        'days': 2,
        'months': 3,
        'years': 1,
    },
    AFS_STORE_USER_IDS_BLOCKS_SEPARATELY=True,
)
@pytest.mark.parametrize('ban_data,code,id,expected,exp_blocked_by_id', [
    ({}, 400, None, None, None),
    (
        {
            'type': 'phone',
            'value': '+7 (999) 666-33-21',
            'phone_type': 'yandex',
            'ticket': TICKET,
        },
        200,
        '5a09782d83b59b80e13ab0f1',
        {
            '_id': '5a09782d83b59b80e13ab0f1',
            'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'blocked_till': datetime.datetime(2018, 12, 12, 10, 0),
            'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'afs_block_reason': 'support_blocking',
            'block_reason': 'unknown reason',
            'blocked_times': 2,
            'block_initiator': {
                'login': REQUEST_LOGIN,
                'ticket': TICKET
            },
        },
        {
            'value': '5a09782d83b59b80e13ab0f1',
            'type': 'phone_id',
            'until': datetime.datetime(2018, 12, 12, 10, 0),
            'created': datetime.datetime(2017, 9, 10, 10, 0),
            'updated': datetime.datetime(2017, 9, 10, 10, 0),
        },
    ),
    (
        {
            'type': 'phone',
            'value': '+7 (000) 000-00-00',
            'phone_type': 'yandex',
            'ticket': TICKET,
        },
        403, None, None, None,
    ),
    (
        {
            'type': 'user',
            'value': '297d52da8caf4b5f86abf4cbd58e5a88',
            'ticket': TICKET,
        },
        403, None, None, None,
    ),
    (
        {
            'type': 'phone',
            'value': '7 999 666 33 21',
            'phone_type': 'yandex',
            'till': '2017-11-30 10:00',
            'ticket': TICKET,
        },
        200,
        '5a09782d83b59b80e13ab0f1',
        {
            '_id': '5a09782d83b59b80e13ab0f1',
            'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'block_reason': 'unknown reason',
            'afs_block_reason': 'support_blocking',
            'blocked_times': 2,
            'block_initiator': {
                'login': REQUEST_LOGIN,
                'ticket': TICKET
            },
        },
        {
            'value': '5a09782d83b59b80e13ab0f1',
            'type': 'phone_id',
            'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'created': datetime.datetime(2017, 9, 10, 10, 0),
            'updated': datetime.datetime(2017, 9, 10, 10, 0),
        },
    ),
    (
        {
            'type': 'phone',
            'value': '8 999 111 22 35',
            'phone_type': 'yandex',
            'till': '2017-11-30 10:00',
            'reason': 'test_reason',
            'ticket': TICKET,
        },
        200,
        '5a09782d83b59b80e13ab0f5',
        {
            '_id': '5a09782d83b59b80e13ab0f5',
            'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'block_reason': 'test_reason',
            'blocked_times': 2,
            'block_initiator': {
                'login': REQUEST_LOGIN,
                'ticket': TICKET
            },
            'total': 3,
            'complete': 1,
            'bad_driver_cancels': 2,
            'afs_block_reason': 'support_blocking',
            'multiorder_total': 1,
            'multiorder_complete': 1,
            'multiorder_blocked_till': datetime.datetime(2018, 8, 31, 21, 0, 0),
            'multiorder_block_reason': 'bad gay',
            'multiorder_rehabilitated': datetime.datetime(2019, 8, 31, 21, 0, 0),
            'multiorder_rehabilitate_reason': 'some reason',
            'multiorder_afs_rehabilitate_reason': 'some_reason',
            'multiorder_rehabilitate_initiator': 'support',
        },
        {
            'value': '5a09782d83b59b80e13ab0f5',
            'type': 'phone_id',
            'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'created': datetime.datetime(2017, 9, 10, 10, 0),
            'updated': datetime.datetime(2017, 9, 10, 10, 0),
        },
    ),
    (
        {
            'type': 'phone_id',
            'value': '5a09782d83b59b80e13ab0f3',
            'reason': 'test_reason',
            'till': '2017-11-30 10:00',
            'ticket': TICKET,
        },
        200,
        '5a09782d83b59b80e13ab0f3',
        {
            '_id': '5a09782d83b59b80e13ab0f3',
            'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'block_reason': 'test_reason',
            'afs_block_reason': 'support_blocking',
            'blocked_times': 3,
            'block_initiator': {
                'login': REQUEST_LOGIN,
                'ticket': TICKET
            }
        },
        {
            'value': '5a09782d83b59b80e13ab0f3',
            'type': 'phone_id',
            'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'created': datetime.datetime(2017, 9, 10, 10, 0),
            'updated': datetime.datetime(2017, 9, 10, 10, 0),
        },
    ),
    (
        {
            'type': 'phone_id',
            'value': '5a09782d83b59b80e13ab0f3',
            'reason': 'test_reason',
            'till': '2017-11-30 10:00',
        },
        200,
        '5a09782d83b59b80e13ab0f3',
        {
            '_id': '5a09782d83b59b80e13ab0f3',
            'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'block_reason': 'test_reason',
            'afs_block_reason': 'support_blocking',
            'blocked_times': 3,
            'block_initiator': {
                'login': REQUEST_LOGIN
            }
        },
        {
            'value': '5a09782d83b59b80e13ab0f3',
            'type': 'phone_id',
            'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'created': datetime.datetime(2017, 9, 10, 10, 0),
            'updated': datetime.datetime(2017, 9, 10, 10, 0),
        },
    ),
    (
        {
            'type': 'phone_id',
            'value': '5a09782d83b59b80e13ab0f3',
            'reason': 'test_reason',
            'till': '2017-11-30 10:00',
            'ticket': None,
        },
        400,
        None,
        None,
        None,
    ),
    (
        {
            'type': 'user',
            'value': 'ban_user_id_test',
            'reason': 'test_reason',
            'till': '2017-11-30 10:00',
        },
        200,
        'ban_user_id_test',
        {
            '_id': 'ban_user_id_test',
            'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'block_reason': 'test_reason',
            'afs_block_reason': 'support_blocking',
            'blocked_times': 8,
            'block_initiator': {
                'login': REQUEST_LOGIN
            }
        },
        None,
    ),
    (
        {
            'type': 'device',
            'value': 'device_id_which_was_not_known',
            'reason': 'test_reason',
            'till': '2017-11-30 10:00',
            'support_template_reason': 'bad_bad_bad',
        },
        200,
        'device_id_which_was_not_known',
        {
            '_id': 'device_id_which_was_not_known',
            'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'block_reason': 'test_reason',
            'support_template_block_reason': 'bad_bad_bad',
            'afs_block_reason': 'support_blocking',
            'blocked_times': 1,
            'block_initiator': {
                'login': REQUEST_LOGIN
            },
            'created': datetime.datetime(2017, 9, 10, 10, 0),
        },
        {
            'value': 'device_id_which_was_not_known',
            'type': 'device_id',
            'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'created': datetime.datetime(2017, 9, 10, 10, 0),
            'updated': datetime.datetime(2017, 9, 10, 10, 0),
        },
    ),
    (
        {
            'type': 'device',
            'value': 'test_ban_device_id',
            'reason': 'test_reason',
            'till': '2017-11-30 10:00',
            'ticket': TICKET,
        },
        200,
        'test_ban_device_id',
        {
            '_id': 'test_ban_device_id',
            'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'block_reason': 'test_reason',
            'afs_block_reason': 'support_blocking',
            'blocked_times': 3,
            'block_initiator': {
                'login': REQUEST_LOGIN,
                'ticket': TICKET,
            },
        },
        {
            'value': 'test_ban_device_id',
            'type': 'device_id',
            'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
            'created': datetime.datetime(2017, 9, 10, 10, 0),
            'updated': datetime.datetime(2017, 9, 10, 10, 0),
        },
    ),
])
@pytest.mark.now('2017-09-10 10:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_ban_user(patch, patch_user_factory, ban_data, code, id, expected,
                  exp_blocked_by_id):
    @patch('taxiadmin.api.views.bad_users._check_ticket')
    @async.inline_callbacks
    def check_ticket(*args, **kwargs):
        yield async.return_value()

    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_personal(data_type, request_value, validate=True, log_extra=None):
        assert data_type == 'phones'
        personal_ids = {
            '+79991112235': '1010101010101010',
            '+79996663321': '0101010101010101',
        }
        yield
        async.return_value(
            {
                'id': personal_ids.get(request_value, 'personal_id'),
                'phone': request_value
            }
        )

    now = datetime.datetime.utcnow()

    response = django_test.Client().post(
        '/api/user/ban/', json.dumps(ban_data), 'application/json'
    )
    assert response.status_code == code
    if expected:
        user_doc = yield get_collection_from_type(
            ban_data['type']).find_one({'_id': id})
        assert user_doc == expected

        events = yield db.antifraud_block_events.find().run()
        assert len(events) == 1
        event = events[0]
        assert event['id'] == id
        assert event['id_type'] == _stat_type_by_ban_type(ban_data['type'])
        assert event['event_type'] == 'block'
        assert event['created'] == now
        assert event['blocked_till'] == expected['blocked_till']
        assert event['initiator'] == expected['block_initiator']['login']
        _check_equal_field('ticket', expected['block_initiator'], event)
        _check_equal_field('support_template_block_reason', expected,
                           event, 'template_reason')
        assert event['internal_reason'] == expected['afs_block_reason']
        assert not event['is_multiorder']

    if exp_blocked_by_id is not None:
        blocked_by_id = list((yield db.antifraud_user_blocked_ids.find(
            {},
            {'_id': False},
        ).run()))
        assert blocked_by_id == [exp_blocked_by_id]


def _check_is_subdict(_dict, _sub_dict):
    return all(
        key in _dict and _dict[key] == _sub_dict[key] for key in _sub_dict)


@pytest.mark.config(
    SVO_PHONE='+70000000000',
    SVO_USER_ID='297d52da8caf4b5f86abf4cbd58e5a88',
    AFS_STORE_USER_IDS_BLOCKS_SEPARATELY=True,
)
@pytest.mark.parametrize('ban_data,expected,ids,exp_blocked_by_id', [
    (
        {
            'type': 'all',
            'value': '+79998887766',
            'phone_type': 'yandex',
            'ticket': TICKET,
            'support_template_reason': 'bad',
        },
        {
            'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'blocked_till': datetime.datetime(2018, 3, 10, 10, 0, 0),
            'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'afs_block_reason': 'support_blocking',
            'block_reason': 'unknown reason',
            'block_initiator': {
                'login': REQUEST_LOGIN,
                'ticket': TICKET
            },
            'support_template_block_reason': 'bad',
        },
        {
            'users': [
                'user_shuld_be_blocked_all_ids_1',
                'user_shuld_be_blocked_all_ids_2',
            ],
            'phones': ['ababdcfeababababab3ababa'],
            'devices': [
                'device_shuld_be_blocked_all_ids_1',
                'device_shuld_be_blocked_all_ids_2',
            ],
        },
        [
            {
                'value': 'ababdcfeababababab3ababa',
                'type': 'phone_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
            {
                'value': 'device_shuld_be_blocked_all_ids_1',
                'type': 'device_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
            {
                'value': 'device_shuld_be_blocked_all_ids_2',
                'type': 'device_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
        ],
    ),
    (
        {
            'type': 'personal_all',
            'value': '9876543210123456',
            'phone_type': 'yandex',
            'ticket': TICKET,
            'support_template_reason': 'bad',
        },
        {
            'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'blocked_till': datetime.datetime(2018, 3, 10, 10, 0, 0),
            'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'afs_block_reason': 'support_blocking',
            'block_reason': 'unknown reason',
            'block_initiator': {
                'login': REQUEST_LOGIN,
                'ticket': TICKET
            },
            'support_template_block_reason': 'bad',
        },
        {
            'users': [
                'user_shuld_be_blocked_all_ids_1',
                'user_shuld_be_blocked_all_ids_2',
            ],
            'phones': ['ababdcfeababababab3ababa'],
            'devices': [
                'device_shuld_be_blocked_all_ids_1',
                'device_shuld_be_blocked_all_ids_2',
            ],
        },
        [
            {
                'value': 'ababdcfeababababab3ababa',
                'type': 'phone_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
            {
                'value': 'device_shuld_be_blocked_all_ids_1',
                'type': 'device_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
            {
                'value': 'device_shuld_be_blocked_all_ids_2',
                'type': 'device_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
        ],
    ),
    (
        {
            'type': 'personal_all',
            'value': '9876543210123456',
            'phone_type': 'all',
            'ticket': TICKET,
            'support_template_reason': 'bad',
        },
        {
            'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'blocked_till': datetime.datetime(2018, 3, 10, 10, 0, 0),
            'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
            'afs_block_reason': 'support_blocking',
            'block_reason': 'unknown reason',
            'block_initiator': {
                'login': REQUEST_LOGIN,
                'ticket': TICKET
            },
            'support_template_block_reason': 'bad',
        },
        {
            'users': [
            ],
            'phones': [
                'ababdcfeababababab4ababa',
                'ababdcfeababababab5ababa',
            ],
            'devices': [
                'device_partner',
            ],
        },
        [
            {
                'value': 'ababdcfeababababab3ababa',
                'type': 'phone_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
            {
                'value': 'ababdcfeababababab4ababa',
                'type': 'phone_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
            {
                'value': 'ababdcfeababababab5ababa',
                'type': 'phone_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
            {
                'value': 'device_partner',
                'type': 'device_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
            {
                'value': 'device_shuld_be_blocked_all_ids_1',
                'type': 'device_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
            {
                'value': 'device_shuld_be_blocked_all_ids_2',
                'type': 'device_id',
                'until': datetime.datetime(2018, 3, 10, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            }
        ],
    )
])
@pytest.mark.now('2017-09-10 10:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_ban_all_ids(patch, patch_user_factory, ban_data, ids,
                     expected, exp_blocked_by_id):
    @patch('taxiadmin.api.views.bad_users._check_ticket')
    @async.inline_callbacks
    def check_ticket(*args, **kwargs):
        yield async.return_value()

    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_personal(data_type, request_value, validate=True, log_extra=None):
        assert data_type == 'phones'
        personal_ids = {
            '+79998887766': '9876543210123456',
        }
        yield
        async.return_value(
            {
                'id': personal_ids.get(request_value, 'personal_id'),
                'phone': request_value
            }
        )

    now = datetime.datetime.utcnow()
    response = django_test.Client().post(
        '/api/user/ban/', json.dumps(ban_data), 'application/json'
    )
    assert response.status_code == 200

    def _check_events(event, id_type):
        assert event['id_type'] == id_type
        assert event['event_type'] == 'block'
        assert event['created'] == now
        assert event['blocked_till'] == expected['blocked_till']
        assert event['reason'] == expected['block_reason']
        _check_equal_field('support_template_block_reason',
                           expected, event, 'template_reason')
        assert event['internal_reason'] == expected['afs_block_reason']
        assert event['initiator'] == expected['block_initiator']['login']
        _check_equal_field('ticket', expected['block_initiator'], event)
        assert not event['is_multiorder']

    for _id in ids['phones']:
        phone_result = yield db.antifraud_stat_phones.find_one({'_id': _id})
        assert _check_is_subdict(phone_result, expected)

        phone_events = yield db.antifraud_block_events.find({'id': _id}).run()
        assert len(phone_events) == 1
        phone_event = phone_events[0]
        _check_events(phone_event, 'phone_id')

    for _id in ids['users']:
        user_result = yield db.antifraud_stat_users.find_one({'_id': _id})
        assert _check_is_subdict(user_result, expected)

        events = yield db.antifraud_block_events.find({'id': _id}).run()
        assert len(phone_events) == 1
        event = events[0]
        _check_events(event, 'user_id')

    for _id in ids['devices']:
        device_result = yield db.antifraud_stat_devices.find_one({'_id': _id})
        assert _check_is_subdict(device_result, expected)

        events = yield db.antifraud_block_events.find({'id': _id}).run()
        assert len(phone_events) == 1
        event = events[0]
        _check_events(event, 'device_id')
    if exp_blocked_by_id is not None:
        blocked_by_id = list((yield db.antifraud_user_blocked_ids.find(
            {},
            {'_id': False, 'updated': False},
        ).run()))
        assert sorted(
            blocked_by_id,
            key=lambda k: (k['value'], k['type'])
        ) == sorted(
            exp_blocked_by_id,
            key=lambda k: (k['value'], k['type'])
        )


@pytest.mark.config(AFS_STORE_USER_IDS_BLOCKS_SEPARATELY=True)
@pytest.mark.parametrize('csv_phones_data,status_code,till,expected,ids,'
                         'exp_blocked_by_id', [
    (
        (
            '+79879134680;uber\n'
            '\n'
            '+380989728107;yandex,uber\n'
            '+79104312696;yandex,google\n'
            '+77767154600\n'
            '+77767154600;\n'
            '+77767154600;yandex,uber;extra\n'
            '+77006507583;yandex'
        ),
        400,
        '',
        {
            'status': 'error',
            'message': (
                'Ошибки при парсинге номеров в строках: 3,4,5,6'
            ),
            'code': 'general',
        },
        None,
        [],
    ),
    (
        (
            '+7 999 666 33 21;uber\n'
            '+7 999 666 33 21;uber\r'
            '+7 999 666 33 21;uber\r'
            '+7 999 666 33 21;uber\r\n'
            '+7 999 666 33 21;uber\n\r'
            '+7 999 666 33 21;uber\n'
            '8 999 111 22 35;yandex,uber'
        ),
        200,
        '2023-03-28T10:00:00.0',
        {
            'banned_counts': {
                'phones': 3,
                'users': 2,
                'devices': 2,
            }
        },
        {
            'phone_ids': [
                '5a09782d83b59b80e13ab0a1',
                '5a09782d83b59b80e13ab0f5',
                '5a09782d83b59b80e13ab0a5'
            ],
            'user_ids': [
                'user_should_be_bulk_blocked_1',
                'user_should_be_bulk_blocked_3',
            ],
            'device_ids': [
                'device_should_be_bulk_blocked_1',
                'device_should_be_bulk_blocked_2',
            ]
        },
        [
            {
                'value': '5a09782d83b59b80e13ab0a1',
                'type': 'phone_id',
                'until': datetime.datetime(2023, 3, 28, 7, 0),
                'created': datetime.datetime(2019, 3, 28, 10, 0),
            },
            {
                'value': '5a09782d83b59b80e13ab0f5',
                'type': 'phone_id',
                'until': datetime.datetime(2023, 3, 28, 7, 0),
                'created': datetime.datetime(2019, 3, 28, 10, 0),
            },
            {
                'value': '5a09782d83b59b80e13ab0a5',
                'type': 'phone_id',
                'until': datetime.datetime(2023, 3, 28, 7, 0),
                'created': datetime.datetime(2019, 3, 28, 10, 0),
            },
            {
                'value': 'device_should_be_bulk_blocked_1',
                'type': 'device_id',
                'until': datetime.datetime(2023, 3, 28, 7, 0),
                'created': datetime.datetime(2019, 3, 28, 10, 0),
            },
            {
                'value': 'device_should_be_bulk_blocked_2',
                'type': 'device_id',
                'until': datetime.datetime(2023, 3, 28, 7, 0),
                'created': datetime.datetime(2019, 3, 28, 10, 0),
            },
        ],
    ),
])
@pytest.mark.now('2019-03-28T10:00:00.0')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_bulk_users_ban(patch_bulk_retrieve_phones_by_personal,
                        csv_phones_data, status_code,
                        till, expected, patch, ids, exp_blocked_by_id):
    @patch('taxiadmin.audit.check_ticket')
    def check_ticket(ticket, login, **kwargs):
        return

    @patch('taxi.external.personal.bulk_store')
    @async.inline_callbacks
    def mock_personal(data_type, request_values, validate=True, log_extra=None):
        assert data_type == 'phones'
        personal_ids = {
            '+79991112235': '1010101010101010',
            '+79996663321': '0101010101010101',
        }
        _response = [{
            'id': personal_ids.get(request_value, 'personal_id'),
            'phone': request_value,
        } for request_value in request_values]

        yield async.return_value(_response)

    bulk_users_ban_csv_file = uploadedfile.SimpleUploadedFile(
        "bulk_users_ban_csv_file.csv",
        csv_phones_data,
    )
    data = {
        'bulk_users_ban_csv_file': bulk_users_ban_csv_file,
        'ticket': 'T1',
        'till': till,
        'support_template_reason': 'bad_men',
    }

    now = datetime.datetime.utcnow()
    ticket = data['ticket']

    def _check_ids(docs):
        dt_till = dates.parse_timestring(till)
        for doc in docs:
            assert 'rehabilitated' not in doc
            assert 'rehabilitate_reason' not in doc
            assert 'rehabilitate_initiator' not in doc

            assert doc['block_time'] == now
            assert doc['block_initiator']['login'] == 'dmkurilov'
            assert doc['block_initiator']['ticket'] == ticket
            assert doc['blocked_till'] == dt_till
            assert 'blocked_times' in doc
            assert doc['block_reason'] == 'unknown reason'
            assert doc['support_template_block_reason'] == 'bad_men'
            assert doc['updated'] == now

    def _check_events(docs, id_type):
        dt_till = dates.parse_timestring(till)
        for doc in docs:
            assert doc['id_type'] == id_type
            assert doc['event_type'] == 'block'
            assert doc['created'] == now
            assert doc['blocked_till'] == dt_till
            assert doc['reason'] == 'unknown reason'
            assert doc['template_reason'] == 'bad_men'
            assert doc['internal_reason'] == 'support_blocking'
            assert doc['initiator'] == 'dmkurilov'
            assert doc['ticket'] == ticket
            assert not doc['is_multiorder']

    response = django_test.Client().post(
        '/api/user/bulk_ban/', data
    )
    assert response.status_code == status_code

    if status_code == 200:
        phone_docs = yield db.antifraud_stat_phones.find(
            {'_id': {'$in': ids['phone_ids']}}).run()
        _check_ids(phone_docs)

        phone_events = yield db.antifraud_block_events.find(
            {'id': {'$in': ids['phone_ids']}}).run()
        assert len(phone_events) == len(ids['phone_ids'])
        _check_events(phone_events, 'phone_id')

        user_docs = yield db.antifraud_stat_users.find(
            {'_id': {'$in': ids['user_ids']}}).run()
        _check_ids(user_docs)

        user_events = yield db.antifraud_block_events.find(
            {'_id': {'$in': ids['user_ids']}}).run()
        _check_events(user_events, 'user_id')

        device_docs = yield db.antifraud_stat_devices.find(
            {'_id': {'$in': ids['device_ids']}}).run()
        _check_ids(device_docs)

        device_events = yield db.antifraud_block_events.find(
            {'_id': {'$in': ids['device_ids']}}).run()
        _check_events(device_events, 'device_id')

    assert json.loads(response.content) == expected

    if exp_blocked_by_id is not None:
        blocked_by_id = list((yield db.antifraud_user_blocked_ids.find(
            {},
            {'_id': False, 'updated': False},
        ).run()))
        assert sorted(
            exp_blocked_by_id,
            key=lambda k: (k['value'], k['type']
        )) == sorted(
            blocked_by_id,
            key=lambda k: (k['value'], k['type'])
        )


@pytest.mark.filldb(antifraud_block_events='check')
@pytest.mark.parametrize('data,code,expected', [
    ({}, 400, None),
    (
        {
            'phone': '+79996663322',
            'phone_type': 'yandex',
        },
        200,
        {
            'phone_doc': {
                'id': '5a09782d83b59b80e13ab0f3',
                'blocked_times': 2,
                'phone': '+79996663322',
                'block_history': [],
            },
            'users': [{
                'id': 'user_1',
                'blocked_till': '2017-11-01T00:00:00+0300',
                'device_id': 'device_id_1',
                'block_history': [
                    {
                        'created': '2017-11-01T00:00:00+0300',
                        'is_multiorder': False,
                        'initiator': 'me',
                        'event_type': 'unblock',
                    },
                    {
                        'created': '2016-09-01T00:00:00+0300',
                        'blocked_till': '2019-09-01T00:00:00+0300',
                        'reason': 'test',
                        'is_multiorder': False,
                        'event_type': 'block',
                    },
                ],
            }],
            'devices': [
                {
                    'id': 'device_id_1',
                    'blocked_till': '2018-09-01T00:00:00+0300',
                    'block_history': [],
                }
            ],
            'unpaid_credit_order_ids': ['order_3', 'order_4', 'order_7', 'order_8'],
        },
    ),
    (
        {
            'phone': '+79991112233',
            'phone_type': 'yandex',
        },
        200,
        {
            'phone_doc': {
                'id': '5b69748d07d86b5cd389f38a',
                'blocked_times': 15,
                'phone': '+79991112233',
                'block_initiator': {
                    'ticket': TICKET,
                    'login': REQUEST_LOGIN
                },
                'blocked_reason': 'cached using citymobil',
                'support_template_reason': 'need_to_be_blocked',
                'rehabilitated': '2017-09-01T00:00:00+0300',
                'rehabilitate_reason': 'looks nice',
                'rehabilitate_initiator': 'support',
                'multiorder_blocked_till': '2017-09-01T00:00:00+0300',
                'multiorder_rehabilitated': '2017-09-01T00:00:00+0300',
                'multiorder_block_time': '2017-09-01T00:00:00+0300',
                'multiorder_blocked_reason': '...',
                'multiorder_blocked_times': 700,
                'multiorder_rehabilitate_initiator': 'support1',
                'multiorder_rehabilitate_reason': 'looks bad',
                'block_history': [
                    {
                        'created': '2017-11-01T00:00:00+0300',
                        'is_multiorder': False,
                        'initiator': 'me',
                        'event_type': 'unblock',
                    },
                    {
                        'created': '2016-09-01T00:00:00+0300',
                        'blocked_till': '2019-09-01T00:00:00+0300',
                        'reason': 'test',
                        'is_multiorder': False,
                        'event_type': 'block',
                    },
                ],
            },
            'users': [{
                'id': 'user_4',
                'blocked_till': '2020-11-01T00:00:00+0300',
                'device_id': 'device_id_3',
                'blocked_reason': 'Не справился с управлением',
                'block_initiator': {
                    'ticket': TICKET,
                    'login': REQUEST_LOGIN
                },
                'block_history': [],
            }],
            'devices': [
                {
                    'id': 'device_id_3',
                    'blocked_till': '2017-11-01T00:00:00+0300',
                    'block_initiator': {
                        'ticket': TICKET,
                        'login': REQUEST_LOGIN
                    },
                    'block_history': [],
                }
            ],
            'unpaid_credit_order_ids': [],
        }
    )
])
@pytest.mark.now('2017-09-10 10:00:00')
@pytest.mark.asyncenv('blocking')
def test_check_user(patch, patch_user_factory, data, code, expected):
    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_phones_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        personal_phone_id = {
            '+79996663322': '1122334455667788',
            '+79991112233': '8877665544332211',
        }.get(value)
        async.return_value({'id': personal_phone_id, 'phone': value})

    response = django_test.Client().post(
        '/api/user/check/', json.dumps(data), 'application/json'
    )
    assert response.status_code == code
    if expected:
        response_doc = json.loads(response.content)
        assert response_doc['phone_doc'] == expected['phone_doc']
        assert (response_doc['users'] == expected['users'])
        assert (response_doc['devices'] == expected['devices'])
        assert (sorted(response_doc['unpaid_credit_order_ids'])
                == expected['unpaid_credit_order_ids'])


@pytest.mark.parametrize('data,code,user_id,expected', [
    (
        {
            'phone': '+79996000002',
            'phone_type': 'yandex',
            'reason': 'test_reason'
        }, 404, None, None
    ),
    (
        {
            'phone': '+79996663311',
            'phone_type': 'yandex',
            'reason': 'test_reason'
        }, 200, 'user_2', True
    )
])
@pytest.mark.now('2017-09-10 10:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_unauthorize_user(patch, data, code, user_id, expected):
    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_phones_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        personal_phone_id = {
            '+79996000002': '31337',
            '+79996663311': '1234567812345678',
        }.get(value)
        async.return_value({'id': personal_phone_id, 'phone': value})

    @patch('taxi.external.userapi._request')
    @async.inline_callbacks
    def _request(path, timeout, retries, **kwargs):
        if path == userapi.USER_PHONES_BY_PERSONAL_BULK:
            user_info = {
                'id': '123123123',
                'phone': '+79996663311',
                'type': 'yandex',
            }
            items = [user_info]
        if path == userapi.USERS_SEARCH:
            user = {
                'yandex_uid': '123123123',
            }
            items = [user]
        response = {
            'items': items,
        }
        async.return_value(response)

    @patch('taxi.external.passport_internal.user_logout')
    def user_logout(uid, tvm_src_service, consumer=None, log_extra=None):
        async.return_value({})

    response = django_test.Client().post(
        '/api/user/unauthorize/', json.dumps(data), 'application/json'
    )
    assert response.status_code == code
    if expected:
        user = yield db.users.find_one({'_id': user_id})
        authorized_field = user.get('authorized')
        assert authorized_field is None
        assert json.loads(response.content) == EMPTY_DICT


def _check_unban_event(event, id_type, now, reason,
                       login, is_multiorder):
    assert event['id_type'] == id_type
    assert event['event_type'] == 'unblock'
    assert event['created'] == now
    assert event['reason'] == reason
    assert event['initiator'] == login
    assert event['is_multiorder'] == is_multiorder


@pytest.mark.parametrize('data,code,ids,expected', [
    (
        {
            'phone': '+79996000002',
            'phone_type': 'yandex',
            'reason': 'test_reason'
        }, 404, None, None
    ),
    (
        {
            'phone': '+79996123124',
            'phone_type': 'yandex',
            'reason': 'Тестовая причина',
        },
        200,
        {
            'user': ['user_3'],
            'device': ['device_id_2'],
            'phone': ['5a09782d83b59b80e13ab0f4'],
        },
        {
            'stat_phones': {
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitate_reason': 'Тестовая причина',
                'rehabilitate_initiator': 'dmkurilov',
            },
            'stat_users': {
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitate_reason': 'Тестовая причина',
                'rehabilitate_initiator': 'dmkurilov',
                'multiorder_blocked_till':
                    datetime.datetime(2018, 8, 31, 21, 0),
                'multiorder_block_reason': 'multimetr'
            },
            'stat_devices': {
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitate_reason': 'Тестовая причина',
                'rehabilitate_initiator': 'dmkurilov',
            },
        },
    ),
    (
        {
            'personal_phone_id': '2233445566778811',
            'phone_type': 'yandex',
            'reason': 'Тестовая причина',
        }, 200,
        {
            'user': ['user_3'],
            'device': ['device_id_2'],
            'phone': ['5a09782d83b59b80e13ab0f4'],
        },
        {
            'stat_phones': {
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitate_reason': 'Тестовая причина',
                'rehabilitate_initiator': 'dmkurilov',
            },
            'stat_users': {
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitate_reason': 'Тестовая причина',
                'rehabilitate_initiator': 'dmkurilov',
                'multiorder_blocked_till':
                    datetime.datetime(2018, 8, 31, 21, 0),
                'multiorder_block_reason': 'multimetr'
            },
            'stat_devices': {
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitate_reason': 'Тестовая причина',
                'rehabilitate_initiator': 'dmkurilov',
            },
        },
    ),
    (
        {
            'personal_phone_id': '9876543210123456_all',
            'phone_type': 'all',
            'reason': 'Тестовая причина',
        }, 200,
        {
            'user': [],
            'device': ['device_partner_unblock'],
            'phone': [
                '2babdcfeababababab5ababa',
                '1babdcfeababababab5ababa',
            ],
        },
        {
            'stat_phones': {
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitate_reason': 'Тестовая причина',
                'rehabilitate_initiator': 'dmkurilov',
            },
            'stat_users': None,
            'stat_devices': {
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'rehabilitate_reason': 'Тестовая причина',
                'rehabilitate_initiator': 'dmkurilov',
            },
        },
    ),
])
@pytest.mark.now('2017-09-10 10:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(AFS_STORE_USER_IDS_BLOCKS_SEPARATELY=True)
@pytest.mark.filldb(antifraud_user_blocked_ids='unban_user')
@pytest.inline_callbacks
def test_unban_user(patch, patch_user_factory, data, code, ids, expected):
    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_phones_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        personal_phone_id = {
            '+79996000002': '31337',
            '+79996123124': '2233445566778811',
        }.get(value)
        async.return_value({'id': personal_phone_id, 'phone': value})

    @async.inline_callbacks
    def _need_check(collection, ids):
        raws = yield collection.find({'_id': {'$in': ids}}).run()
        blocked_ids = set()
        for raw in raws:
            if 'blocked_till' in raw and raw['blocked_till'] > now:
                blocked_ids.add(raw['_id'])

        async.return_value(blocked_ids)

    now = datetime.datetime.utcnow()

    response = django_test.Client().post(
        '/api/user/unban/', json.dumps(data), 'application/json'
    )
    assert response.status_code == code
    if expected:
        stat_phones = yield db.antifraud_stat_phones.find_one(
            {'_id': {'$in': ids['phone']}}, {'_id': False}
        )
        stat_users = yield db.antifraud_stat_users.find_one(
            {'_id': {'$in': ids['user']}}, {'_id': False}
        )
        stat_devices = yield db.antifraud_stat_devices.find_one(
            {'_id': {'$in': ids['device']}}, {'_id': False}
        )
        assert stat_phones == expected['stat_phones']
        assert stat_users == expected['stat_users']
        assert stat_devices == expected['stat_devices']

        user_ids_to_check = yield _need_check(db.antifraud_stat_users, ids['user'])
        phone_ids_to_check = yield _need_check(db.antifraud_stat_phones, ids['phone'])
        device_ids_to_check = yield _need_check(db.antifraud_stat_devices, ids['device'])

        if phone_ids_to_check:
            phone_events = yield db.antifraud_block_events.find(
                {'id': {'$in': ids['phone']}}).run()
            assert len(phone_events) == len(phone_ids_to_check)
            for phone_event in phone_events:
                _check_unban_event(phone_event, 'phone_id', now,
                                   data['reason'], 'dmkurilov', False)

        if user_ids_to_check:
            user_events = yield db.antifraud_block_events.find(
                {'id': {'$in': ids['user']}}).run()
            assert len(user_events) == len(user_ids_to_check)
            for user_event in user_events:
                _check_unban_event(user_event, 'user_id', now,
                                   data['reason'], 'dmkurilov', False)

        if device_ids_to_check:
            device_events = yield db.antifraud_block_events.find(
                {'id': {'$in': ids['device']}}).run()
            assert len(device_events) == len(device_ids_to_check)
            for device_event in device_events:
                _check_unban_event(device_event, 'device_id', now,
                                   data['reason'], 'dmkurilov', False)

    if ids:
        assert [] == (yield db.antifraud_user_blocked_ids.find({
            'value': {'$in': ids['phone'] + ids['device']}
        }).run())


@pytest.mark.parametrize('data,code,ids,expected', [
    (
        {
            'phone': '+79996000002',
            'phone_type': 'yandex',
            'reason': 'test_reason'
        }, 404, None, None
    ),
    (
        {
            'phone': '+79991138238',
            'phone_type': 'yandex',
            'reason': 'test_reason'
        }, 200,
        {
            'user': 'user_5',
            'device': 'device_id_5',
            'phone': '5ce1437d4046476f46cd53ae',
        },
        {
            'stat_phones': {
                '_id': '5ce1437d4046476f46cd53ae',
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitate_reason': 'test_reason',
                'multiorder_rehabilitate_initiator': 'dmkurilov',
                'blocked_times': 1,
                'blocked_till': datetime.datetime(2017, 10, 31, 21, 0),
                'afs_block_reason': 'python programmer',
            },
            'stat_users': {
                '_id': 'user_5',
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitate_reason': 'test_reason',
                'multiorder_rehabilitate_initiator': 'dmkurilov',
            },
            'stat_devices': {
                '_id': 'device_id_5',
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitate_reason': 'test_reason',
                'multiorder_rehabilitate_initiator': 'dmkurilov',
            },
        },
    ),
    (
        {
            'personal_phone_id': '3344556677881122',
            'phone_type': 'yandex',
            'reason': 'test_reason'
        }, 200,
        {
            'user': 'user_5',
            'device': 'device_id_5',
            'phone': '5ce1437d4046476f46cd53ae',
        },
        {
            'stat_phones': {
                '_id': '5ce1437d4046476f46cd53ae',
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitate_reason': 'test_reason',
                'multiorder_rehabilitate_initiator': 'dmkurilov',
                'blocked_times': 1,
                'blocked_till': datetime.datetime(2017, 10, 31, 21, 0),
                'afs_block_reason': 'python programmer',
            },
            'stat_users': {
                '_id': 'user_5',
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitate_reason': 'test_reason',
                'multiorder_rehabilitate_initiator': 'dmkurilov',
            },
            'stat_devices': {
                '_id': 'device_id_5',
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_blocked_till': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitated': datetime.datetime(2017, 9, 10, 10, 0),
                'multiorder_rehabilitate_reason': 'test_reason',
                'multiorder_rehabilitate_initiator': 'dmkurilov',
            },
        },
    ),
])
@pytest.mark.now('2017-09-10 10:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_unban_multiorder(patch, data, code, ids, expected):
    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_phones_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        personal_phone_id = {
            '+79996000002': '31337',
            '+79991138238': '3344556677881122',
        }.get(value)
        async.return_value({'id': personal_phone_id, 'phone': value})

    now = datetime.datetime.utcnow()

    @async.inline_callbacks
    def _need_check(collection, _id):
        raw = yield collection.find_one({'_id': _id})
        if 'blocked_till' not in raw:
            async.return_value(False)

        async.return_value(raw['multiorder_blocked_till'] > now)

    response = django_test.Client().post(
        '/api/user/unban_multiorder/', json.dumps(data), 'application/json'
    )
    assert response.status_code == code
    if expected:
        phone = yield db.antifraud_stat_phones.find_one({'_id': ids['phone']})
        user = yield db.antifraud_stat_users.find_one({'_id': ids['user']})
        device = yield db.antifraud_stat_devices.find_one({'_id': ids['device']})
        assert phone == expected['stat_phones']
        assert user == expected['stat_users']
        assert device == expected['stat_devices']

        need_check_user = yield _need_check(db.antifraud_stat_users, ids['user'])
        need_check_phone = yield _need_check(db.antifraud_stat_phones, ids['phone'])
        need_check_device = yield _need_check(db.antifraud_stat_devices, ids['device'])

        if need_check_phone:
            phone_events = yield db.antifraud_block_events.find(
                {'id': ids['phone']}).run()
            assert len(phone_events) == 1
            phone_event = phone_events[0]
            _check_unban_event(phone_event, 'phone_id', now,
                               data['reason'], 'dmkurilov', True)

        if need_check_user:
            user_events = yield db.antifraud_block_events.find(
                {'id': ids['user']}).run()
            assert len(user_events) == 1
            user_event = user_events[0]
            _check_unban_event(user_event, 'user_id', now,
                               data['reason'], 'dmkurilov', True)

        if need_check_device:
            device_events = yield db.antifraud_block_events.find(
                {'id': ids['device']}).run()
            assert len(device_events) == 1
            device_event = device_events[0]
            _check_unban_event(device_event, 'device_id', now,
                               data['reason'], 'dmkurilov', True)


@pytest.mark.parametrize('data,code,phonelock_id,expected', [
    (
        {
            'phone': '+79996000002',
            'phone_type': 'yandex',
            'reason': 'test_reason'
        }, 404, None, None
    ),
    (
        {
            'phone': '+79996663322',
            'phone_type': 'yandex',
            'reason': 'test_reason'
        }, 200,
        ObjectId('5a09782d83b59b80e13ab0f3'),
        {
            'i': ObjectId('5a09782d83b59b80e13ab0f3'),
            'o': ['order_1', 'order_2'],
            'x': []
        }
    )
])
@pytest.mark.now('2017-09-10 10:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_unban_user_card(patch, data, code, phonelock_id, expected):
    @patch('taxi.external.archive._perform_post')
    @pytest.inline_callbacks
    def _perform_post(location, payload, src_tvm_service=None, log_extra=None):
        raise archive.NotFoundError

    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_phones_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        personal_phone_id = {
            '+79996000002': '31337',
            '+79996663322': '1122334455667788',
        }.get(value)
        async.return_value({'id': personal_phone_id, 'phone': value})

    response = django_test.Client().post(
        '/api/user/unban_card/', json.dumps(data), 'application/json'
    )
    assert response.status_code == code
    if expected:
        phonelock = yield db.phonelocks.find_one({'i': phonelock_id})
        phonelock.pop('_id')
        assert phonelock == expected
        assert json.loads(response.content) == EMPTY_DICT
