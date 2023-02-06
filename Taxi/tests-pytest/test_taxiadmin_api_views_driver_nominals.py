import datetime
import json

from django import test as django_test
import pytest

from taxi.core import db
from taxi.internal import audit_actions


NOMINAL_1 = {
    'series_id': 'nominal_1',
    'created_by': 'login_1',
    'start': '2018-09-01T13:35:00+0300',
    'finish': '2018-10-01T13:35:00+0300',
    'is_active': True,
    'country': 'rus',
    'currency': 'RUB',
    'duration_hours': 12,
    'description': 'some description',
    'limit_count': 50,
    'used_count': 0,
    'actual': False
}

NOMINAL_2 = {
    'series_id': 'nominal_2',
    'created_by': 'login_2',
    'start': '2018-09-01T13:35:00+0300',
    'finish': '2018-10-01T13:35:00+0300',
    'is_active': False,
    'country': 'rus',
    'currency': 'RUB',
    'duration_hours': 24,
    'description': 'some description',
    'limit_count': 50,
    'used_count': 10,
    'actual': False
}

NOMINAL_3 = {
    'series_id': 'nominal_3',
    'created_by': 'login_3',
    'start': '2018-11-01T13:35:00+0300',
    'finish': '2018-12-01T13:35:00+0300',
    'is_active': True,
    'country': 'rus',
    'currency': 'RUB',
    'duration_hours': 24,
    'description': 'some description',
    'limit_count': 30,
    'used_count': 15,
    'actual': True
}

NOMINAL_4 = {
    'series_id': 'nominal_4',
    'created_by': 'login_4',
    'start': '2018-11-01T13:35:00+0300',
    'finish': '2018-12-01T13:35:00+0300',
    'is_active': True,
    'country': 'blr',
    'currency': 'BYN',
    'duration_hours': 36,
    'description': 'some description',
    'limit_count': 30,
    'used_count': 15,
    'actual': True
}

NOMINAL_5 = {
    'series_id': 'nominal_5',
    'created_by': 'login_5',
    'start': '2018-11-01T13:35:00+0300',
    'finish': '2018-12-01T13:35:00+0300',
    'is_active': True,
    'country': 'blr',
    'currency': 'BYN',
    'duration_hours': 36,
    'description': 'some description',
    'limit_count': 30,
    'used_count': 30,
    'actual': False
}


@pytest.mark.parametrize('request_json,expected_response', [
    (
        {},
        [
            NOMINAL_5,
            NOMINAL_4,
            NOMINAL_3,
            NOMINAL_2,
            NOMINAL_1
        ]
    ),
    (
        {
            'skip': 1,
            'limit': 1,
        },
        [
            NOMINAL_4
        ]
    ),
    (
        {
            'country': 'blr'
        },
        [
            NOMINAL_5,
            NOMINAL_4
        ]
    ),
    (
        {
            'country': 'rus',
            'active_from': '2018-11-12T00:00:00+03:00'
        },
        [
            NOMINAL_3
        ]
    ),
    (
        {
            'country': 'rus',
            'active_to': '2018-09-12T00:00:00+03:00'
        },
        [
            NOMINAL_2,
            NOMINAL_1
        ]
    ),
    (
        {
            'country': 'rus',
            'active': True
        },
        [
            NOMINAL_3,
            NOMINAL_1
        ]
    ),
    (
        {
            'active': False
        },
        [
            NOMINAL_2
        ]
    ),
    (
        {
            'actual': True,
        },
        [
            NOMINAL_4,
            NOMINAL_3
        ]
    )
])
@pytest.mark.now('2018-11-15T12:00:00+03:00')
@pytest.mark.asyncenv('blocking')
def test_nominals_list(request_json, expected_response):
    client = django_test.Client()
    response = client.post(
        '/api/driver_nominals/list/',
        json.dumps(request_json),
        'application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data == {
        'items': expected_response
    }


@pytest.mark.parametrize('request_json,expected_code,expected_data', [
    (
        {
            'series_id': 'new_nominal',
            'start': '2018-09-10T12:00:00+03:00',
            'finish': '2018-12-10T12:00:00+03:00',
            'country': 'rus',
            'duration_hours': 24,
            'description': 'new nominal',
            'limit_count': 25,
            'ticket': 'TAXIRATE-123'
        },
        200,
        {
            'series_id': 'new_nominal',
            'created_by': 'dmkurilov',
            'created': datetime.datetime(2018, 9, 1, 9, 0),
            'updated': datetime.datetime(2018, 9, 1, 9, 0),
            'start': datetime.datetime(2018, 9, 10, 9, 0),
            'finish': datetime.datetime(2018, 12, 10, 9, 0),
            'is_active': True,
            'country': 'rus',
            'currency': 'RUB',
            'duration_hours': 24,
            'description': 'new nominal',
            'limit_count': 25,
            'used_count': 0,
            'version': 1
        }
    ),
    (
        {
            'series_id': 'new_nominal',
            'start': '2018-09-10T12:00:00+03:00',
            'finish': '2018-12-10T12:00:00+03:00',
            'country': 'usa',
            'duration_hours': 24,
            'description': 'new nominal',
            'limit_count': 25,
            'ticket': 'TAXIRATE-123'
        },
        400,
        None
    ),
    (
        {
            'series_id': 'nominal_3',
            'start': '2018-09-10T12:00:00+03:00',
            'finish': '2018-12-10T12:00:00+03:00',
            'country': 'rus',
            'duration_hours': 24,
            'description': 'new nominal',
            'limit_count': 25,
            'ticket': 'TAXIRATE-123'
        },
        400,
        None
    )
])
@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.now('2018-09-01T12:00:00+03:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_add_nominal(request_json, expected_code, expected_data):
    client = django_test.Client()
    response = client.post(
        '/api/driver_nominals/add/',
        json.dumps(request_json),
        'application/json'
    )
    response.status_code == expected_code

    if expected_code == 200:
        data = json.loads(response.content)
        assert data == {}

        doc = yield db.driver_nominals.find_one({
            'series_id': request_json['series_id']
        })
        doc.pop('_id')
        assert doc == expected_data

        action = yield db.log_admin.find_one({
            'action': audit_actions.add_nominal.id,
        })
        assert action is not None
        assert action['ticket'] == 'TAXIRATE-123'


@pytest.mark.parametrize('request_json,expected_code,expected_data', [
    (
        {
            'series_id': 'nominal_1',
            'ticket': 'TAXIRATE-123'
        },
        200,
        {
            'series_id': 'nominal_1',
            'created_by': 'login_1',
            'created': datetime.datetime(2018, 9, 1, 10, 35),
            'updated': datetime.datetime(2018, 9, 1, 12, 0),
            'start': datetime.datetime(2018, 9, 1, 10, 35),
            'finish': datetime.datetime(2018, 10, 1, 10, 35),
            'is_active': False,
            'country': 'rus',
            'currency': 'RUB',
            'duration_hours': 12,
            'description': 'some description',
            'limit_count': 50,
            'used_count': 0,
            'version': 1
        }
    ),
    (
        {
            'series_id': 'wrong_nominal',
            'ticket': 'TAXIRATE-123'
        },
        404,
        None,
    )
])
@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.now('2018-09-01T12:00:00+03:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_delete_nominal(request_json, expected_code, expected_data):
    client = django_test.Client()
    response = client.post(
        '/api/driver_nominals/delete/',
        json.dumps(request_json),
        'application/json'
    )
    response.status_code == expected_code

    if expected_code == 200:
        data = json.loads(response.content)
        assert data == {}

        doc = yield db.driver_nominals.find_one({
            'series_id': request_json['series_id']
        })
        doc.pop('_id')
        assert doc == expected_data

        action = yield db.log_admin.find_one({
            'action': audit_actions.edit_nominal.id,
        })
        assert action is not None
        assert action['ticket'] == 'TAXIRATE-123'
