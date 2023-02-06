# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django import test as django_test
from django.core import urlresolvers
import pytest

from taxi.core import async
from taxi.core import db
from taxi.util import data_structures
from taxiadmin.api.views import sms as sms_views

import helpers


@pytest.fixture
def patch_start_task(patch):
    @patch('taxi.internal.sms_sender.start_task')
    def start_task(task_id, schedule_time=None):
        pass


@pytest.fixture
def patch_clean_phone(patch):
    @patch('taxi.internal.city_kit.country_manager.get_countries')
    @async.inline_callbacks
    def get_countries(*args, **kwargs):
        yield
        async.return_value([{
            '_id': 'rus',
            'phone_code': '7',
            'national_access_code': '8',
            'phone_max_length': 11,
            'phone_min_length': 11,
        }])


case = helpers.case_getter(
    'request_data,expected_status,expected_response,expected_route',
)


@pytest.mark.now('2018-10-12 00:00:00')
@pytest.mark.parametrize(
    case.params,
    [
        case(
            request_data={
                'phone': '+79001234567',
                'message': 'test_message',
                'route': 'taxi',
            },
            expected_status=200,
            expected_route='taxi',
        ),
        case(
            request_data={
                'phone': '+79002222222',
                'message': 'test_message',
            },
            expected_status=400,
        ),
        case(
            request_data={
                'phone': '+79001234567',
                'message': 'test_message',
                'route': 'invalid_route',
            },
            expected_status=400,
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.usefixtures('patch_start_task', 'patch_clean_phone')
@pytest.inline_callbacks
def test_send_sms(request_data, expected_status, expected_response,
                  expected_route):
    response = django_test.Client().post(
        urlresolvers.reverse(sms_views.send_sms),
        json.dumps(request_data), 'application/json'
    )
    assert response.status_code == expected_status
    if expected_route is not None:
        sms_task = yield db.sms_queue.find_one({'phone': request_data['phone']})
        assert sms_task['route'] == expected_route
    if expected_response is not None:
        assert response.json() == expected_response


case_bulk = helpers.case_getter(
    'request_phones,request_message,request_route,skip_malformed_phones,'
    'expected_status,expected_response,expected_history,expected_tasks_phones',
    request_message='test_message',
    request_route='uber',
    expected_status=200,
    expected_response={'task_id': 4},  # three tasks are in db already
)


@pytest.mark.now('2018-10-12 00:00:00')
@pytest.mark.parametrize(
    case_bulk.params,
    [
        # just normal case
        case_bulk(
            request_phones=['+79001234567', '+79001111111', '+79002222223'],
            expected_history={
                'yandex_login': 'dmkurilov',
                'route': 'uber',
                'phones_count_valid': 3,
                'phones_count': 3,
            }
        ),
        # +79002222222 has declined receiving (see driver_informed_consent.json)
        case_bulk(
            request_phones=['+79001234567', '+79001111111', '+79002222222'],
            expected_history={
                # only fields that matter
                'phones_count_valid': 2,
                'phones_count': 3,
            },
            expected_tasks_phones=['+79001234567', '+79001111111'],
        ),
        # all phones have declined receiving (see driver_informed_consent.json)
        case_bulk(
            request_phones=['+79002222222', '+79009999999'],
            expected_status=400,
            expected_response={
                'status': 'error',
                'code': 'general',
                'message': 'Для всех указанных телефонов рассылка отключена',
            },
        ),
        # contains broken phone numbers and no flag to skip them
        case_bulk(
            request_phones=['+79001234567', '+7900111111', '+790002222222'],
            expected_status=400,
            expected_response={
                'status': 'error',
                'code': 'general',
                'message': 'Рассылка содержит некорректные телефоны (2 шт.)',
            },
        ),
        # contains broken phone numbers and unset flag to skip them
        case_bulk(
            request_phones=['+79001234567', '+7900111111', '+790002222222'],
            skip_malformed_phones=False,
            expected_status=400,
            expected_response={
                'status': 'error',
                'code': 'general',
                'message': 'Рассылка содержит некорректные телефоны (2 шт.)',
            },
        ),
        # contains broken phone numbers and set flag to skip them
        case_bulk(
            request_phones=['+79001234567', '+790002222222', '+79001111110'],
            skip_malformed_phones=True,
            expected_status=200,
            expected_history={
                'phones_count_valid': 2,
                'phones_count': 3,
            },
            expected_tasks_phones=['+79001234567', '+79001111110'],
        ),
        # contains only broken phone numbers and set flag to skip them
        case_bulk(
            request_phones=['+790002222222', '+7900111111'],
            skip_malformed_phones=True,
            expected_status=400,
            expected_response={
                'status': 'error',
                'code': 'general',
                'message': 'Рассылка не содержит корректных телефонов',
            },
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.usefixtures('patch_start_task', 'patch_clean_phone')
@pytest.inline_callbacks
def test_send_bulk_sms(request_phones, request_message, request_route,
                       skip_malformed_phones,
                       expected_status, expected_response, expected_history,
                       expected_tasks_phones
                       ):
    request_dict = {
        'phones': request_phones,
        'message': request_message,
        'route': request_route,
        'schedule_time': '2018-10-13 00:00:00+0'
    }
    if skip_malformed_phones is not None:
        request_dict['skip_malformed_phones'] = skip_malformed_phones
    response = django_test.Client().post(
        urlresolvers.reverse(sms_views.send_sms_bulk),
        json.dumps(request_dict),
        'application/json'
    )
    assert response.status_code == expected_status
    data = json.loads(response.content)
    assert data == expected_response

    if expected_history is not None:
        # check history
        task_id = data['task_id']
        history = yield db.sms_sending_history.find_one({'task_id': task_id})
        assert history['text'] == request_message
        assert history['phones_count'] == len(request_phones)
        assert history['created'] == datetime.datetime.utcnow()
        assert history['schedule_time'] == datetime.datetime(2018, 10, 13, 0, 0)
        if expected_history:  # use empty dict in test case for no checks here
            partial_history = data_structures.partial_dict(
                history, expected_history.keys()
            )
            assert partial_history == expected_history

        # check routes in sms_queue
        if expected_tasks_phones is None:
            expected_tasks_phones = request_phones
        sms_tasks = yield db.sms_queue.find({'task_id': task_id}).run()
        assert len(sms_tasks) == len(expected_tasks_phones)
        task_phones = set()
        for task in sms_tasks:
            assert task['route'] == request_route
            task_phones.add(task['phone'])
        assert task_phones == set(expected_tasks_phones)


@pytest.mark.config(ADMIN_SMS_USE_STATUS_COUNTER=True)
@pytest.mark.parametrize('params,status_code,expected_indexes', [
    ({}, 200, [0, 1, 2]),
    ({'limit': 1, 'offset': 1}, 200, [1]),
    ({'yandex_login': 'test_login'}, 200, [1, 2]),
    ({'task_id': 3}, 200, [0]),
    (
        {
            'created_from': '2018-10-10T00:00:00',
            'created_to': '2018-10-10T12:00:00'
        },
        200,
        [1]
    ),
    ({'task_id': 'text'}, 400, None),
    ({'created_from': 'text'}, 400, None),
    ({'limit': 'text'}, 400, None),
    ({'offset': -1}, 400, None)
])
@pytest.mark.asyncenv('blocking')
def test_sms_sending_history(params, expected_indexes, status_code):
    data = [
        {'created': 1539216000,
         'phones_count': 3,
         'phones_count_valid': '2',
         'status_counts': {'complete': 1, 'processing': 1, 'new': 1},
         'task_id': 3,
         'text': 'test_text_3',
         'yandex_login': 'test_login_2',
         'route': 'taxi',
         'schedule_time': None},
        {'created': 1539129600,
         'phones_count': 3,
         'phones_count_valid': '(3)',
         'status_counts': {'complete': 1, 'new': 1, 'processing': 1},
         'task_id': 2,
         'text': 'test_text_2',
         'yandex_login': 'test_login',
         'route': 'taxi',
         'schedule_time': None},
        {'created': 1539043200,
         'phones_count': 2,
         'phones_count_valid': '(2)',
         'status_counts': {'complete': 1, 'new': 1},
         'task_id': 1,
         'text': 'test_text_1',
         'yandex_login': 'test_login',
         'route': 'uber',
         'schedule_time': 1539129600}
    ]
    response = django_test.Client().get(
        urlresolvers.reverse(sms_views.get_sms_sending_history),
        params
    )
    assert response.status_code == status_code

    if response.status_code == 200:
        expected = [data[index] for index in expected_indexes]
        assert json.loads(response.content) == expected


@pytest.mark.config(ADMIN_SMS_USE_STATUS_COUNTER=True)
@pytest.mark.now('2018-10-12 00:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_sms_sending_cancel():
    response = django_test.Client().post(
        urlresolvers.reverse(sms_views.cancel_sms_sending),
        data=json.dumps({'task_id': 3}),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert json.loads(response.content) == {
        'complete': 1,
        'processing': 1,
        'cancelled': 1
    }

    cancelled = yield db.sms_queue.find(
        {'task_id': 3, 'status': 'cancelled'}
    ).run()

    assert len(cancelled) == 1
    assert cancelled[0]['cancelled_at'] == datetime.datetime(2018, 10, 12, 0, 0)


@pytest.mark.config(SMS_REQUIRE_TICKET_SIZE=10)
@pytest.mark.parametrize('data,response_code,expected', [
    (
        {
            'phones': ['+79001234567', '+79001111111', '+79002222222',
                       '+79003333333', '+79005555555'],
            'message': 'a' * 161
        },
        400,
        {
            'status': 'error',
            'message': 'Big sms sending requires ticket',
            'code': 'sms_sending_requires_ticket'
        }
    ),
    (
        {
            'phones': ['+79001234567', '+79001111111', '+79002222222',
                       '+79003333333', '+79005555555'],
            'message': 'П' * 71
        },
        400,
        {
            'status': 'error',
            'message': 'Big sms sending requires ticket',
            'code': 'sms_sending_requires_ticket'
        }
    ),
    (
        {
            'phones': ['+79001234567', '+79001111111', '+79002222222',
                       '+79003333333', '+79005555555'],
            'message': 'П' * 71,
            'ticket': 'TAXIRATE-10'
        },
        200,
        {
            'task_id': 4
        }
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.usefixtures('patch_start_task', 'patch_clean_phone')
def test_ticket_sms_bulk(data, response_code, expected):
    response = django_test.Client().post(
        urlresolvers.reverse(sms_views.send_sms_bulk),
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == response_code
    assert json.loads(response.content) == expected


@pytest.mark.config(ADMIN_SMS_MAX_PHONES_COUNT=2)
@pytest.mark.asyncenv('blocking')
@pytest.mark.usefixtures('patch_start_task', 'patch_clean_phone')
def test_max_size_limiter_sms_bulk():
    response = django_test.Client().post(
        urlresolvers.reverse(sms_views.send_sms_bulk),
        data=json.dumps({
            'phones': ['+79001234567', '+79001111111', '+79002222222'],
            'message': 'a' * 79
        }),
        content_type='application/json'
    )
    assert response.status_code == 400
