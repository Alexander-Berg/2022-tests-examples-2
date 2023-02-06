import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'v1/parks/users/list'

TEST_MISSING_PARK_ID = [
    (
        ['1'],
        400,
        {'code': '400', 'message': 'Field \'query.park\' is missing'},
    ),
]


@pytest.mark.redis_store(
    ['hmset', 'User:Items:park1', {'user1': json.dumps({'YandexUid': '1'})}],
)
@pytest.mark.parametrize(
    'passport_uid, code, expected_response', TEST_MISSING_PARK_ID,
)
async def test_missing_park_id(
        taxi_dispatcher_access_control, passport_uid, code, expected_response,
):
    request_body = {
        'query': {'user': {'passport_uid': passport_uid}},
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json()['code'] == str(code)


TEST_PARK_ID_INVALID_TYPE = [
    (
        ['1'],
        None,
        400,
        {
            'code': '400',
            'message': (
                'Field \'query.park.id\' is of '
                'a wrong type. Expected: '
                'stringValue, actual: nullValue'
            ),
        },
    ),
    (
        ['1'],
        42,
        400,
        {
            'code': '400',
            'message': (
                'Field \'query.park.id\' is of '
                'a wrong type. Expected: stringValue, '
                'actual: intValue'
            ),
        },
    ),
]


@pytest.mark.redis_store(
    ['hmset', 'User:Items:park1', {'user1': json.dumps({'YandexUid': '1'})}],
)
@pytest.mark.parametrize(
    'passport_uid, park_id, code, expected_response',
    TEST_PARK_ID_INVALID_TYPE,
)
async def test_park_id_invalid_type(
        taxi_dispatcher_access_control,
        passport_uid,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'passport_uid': passport_uid},
        },
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json()['code'] == str(code)


TEST_INVALID_REQUEST_PARAMS_LIMITS = [
    (
        {
            'query': {
                'park': {'id': 'park1'},
                'user': {'passport_uid': [str(num) for num in range(101)]},
            },
            'limit': 100,
        },
        400,
        {
            'code': '400',
            'message': (
                'Value of \'query.user.passport_uid\': incorrect size,'
                ' must be 100 (limit) >= 101 (value)'
            ),
        },
    ),
    (
        {
            'query': {
                'park': {'id': 'park1'},
                'user': {'passport_uid': ['1']},
            },
            'limit': 0,
        },
        400,
        {
            'code': '400',
            'message': (
                'Value of \'limit\': out of bounds, '
                'must be 1 (limit) <= 0 (value)'
            ),
        },
    ),
    (
        {
            'query': {
                'park': {'id': 'park1'},
                'user': {'passport_uid': ['1']},
            },
            'limit': 101,
        },
        400,
        {
            'code': '400',
            'message': (
                'Value of \'limit\': out of bounds, '
                'must be 100 (limit) >= 101 (value)'
            ),
        },
    ),
]


@pytest.mark.parametrize(
    'request_body, code, expected_response',
    TEST_INVALID_REQUEST_PARAMS_LIMITS,
)
async def test_invalid_request_limits(
        taxi_dispatcher_access_control, request_body, code, expected_response,
):
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    if expected_response:
        assert response.json()['code'] == str(code)
