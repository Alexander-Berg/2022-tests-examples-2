import copy

import pytest

from tests_signal_device_api import common

ENDPOINT = 'v1/binaries/check'

CONSUMERS = ['signal_device_api/v1_binaries_check']
SERIAL_NUMBER = 'abcdef1234567890'
SERIAL_NUMBER_MISSING = '0000001234567890'
SERIAL_NUMBERS_INVALID_EXPERIMENTS = [
    '{:016d}'.format(i) for i in range(10 ** 15, 10 ** 15 + 4)
]
REQUEST = {
    'hardware_id': '1',
    'serial_number': SERIAL_NUMBER,
    'linux_version': '0.0.1',
    'rtos_version': '0.0.2',
    'data_version': '0.0.3',
}
RESPONSE = {
    'data': '1.0.0',
    'linux': '1.1.0',
    'rtos': '1.1.1',
    'is_critical': False,
    'partition': 'test',
}
RESPONSE_MISSING = {
    'data': '1.0.0',
    'linux': '1.1.0',
    'rtos': '1.1.1',
    'is_critical': False,
}
RESPONSES_INVALID = [
    dict((k, RESPONSE[k]) for k in RESPONSE if k != key)
    for key in ['data', 'linux', 'rtos', 'is_critical']
]
ERROR_RESPONSE = {'code': '500', 'message': 'Internal Server Error'}
BAD_REQUEST_ERROR = {'code': '400', 'message': 'Bad Request'}


@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': [SERIAL_NUMBER_MISSING],
                'arg_name': 'serial_number',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='special_serial_missing',
    consumers=CONSUMERS,
    clauses=[],
    default_value=RESPONSE_MISSING,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='default',
    consumers=CONSUMERS,
    clauses=[],
    default_value=RESPONSE,
)
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_default_ok(taxi_signal_device_api, pgsql):
    response = await taxi_signal_device_api.post(ENDPOINT, json=REQUEST)
    assert response.status_code == 200, response.text
    assert response.json() == RESPONSE
    common.check_alr_inserted(
        pgsql,
        serial_number=SERIAL_NUMBER,
        field_affected='v1_binaries_check_at',
    )


@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': [SERIAL_NUMBER.upper()],
                'arg_name': 'serial_number',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='special_serial',
    consumers=CONSUMERS,
    clauses=[],
    default_value=RESPONSE,
)
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_special_serial_ok(taxi_signal_device_api, pgsql):
    response = await taxi_signal_device_api.post(ENDPOINT, json=REQUEST)
    assert response.status_code == 200, response.text
    assert response.json() == RESPONSE
    common.check_alr_inserted(
        pgsql,
        serial_number=SERIAL_NUMBER,
        field_affected='v1_binaries_check_at',
    )


@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': [SERIAL_NUMBER],
                'arg_name': 'serial_number',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='missing_consumer',
    consumers=['signal_device_api/v1_missing_consumer'],
    clauses=[],
    default_value=RESPONSE_MISSING,
)
@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': [SERIAL_NUMBER_MISSING],
                'arg_name': 'serial_number',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='special_serial_missing',
    consumers=CONSUMERS,
    clauses=[],
    default_value=RESPONSE_MISSING,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': False},
    name='default_disabled',
    consumers=CONSUMERS,
    clauses=[],
    default_value=RESPONSE_MISSING,
)
async def test_all_missing(taxi_signal_device_api):
    response = await taxi_signal_device_api.post(ENDPOINT, json=REQUEST)
    assert response.status_code == 500, response.text
    assert response.json() == ERROR_RESPONSE


@pytest.mark.parametrize('serial_number', SERIAL_NUMBERS_INVALID_EXPERIMENTS)
@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': [SERIAL_NUMBERS_INVALID_EXPERIMENTS[0]],
                'arg_name': 'serial_number',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='special_serial_invalid_0',
    consumers=CONSUMERS,
    clauses=[],
    default_value=RESPONSES_INVALID[0],
)
@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': [SERIAL_NUMBERS_INVALID_EXPERIMENTS[1]],
                'arg_name': 'serial_number',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='special_serial_invalid_1',
    consumers=CONSUMERS,
    clauses=[],
    default_value=RESPONSES_INVALID[1],
)
@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': [SERIAL_NUMBERS_INVALID_EXPERIMENTS[2]],
                'arg_name': 'serial_number',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='special_serial_invalid_2',
    consumers=CONSUMERS,
    clauses=[],
    default_value=RESPONSES_INVALID[2],
)
@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': [SERIAL_NUMBERS_INVALID_EXPERIMENTS[3]],
                'arg_name': 'serial_number',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='special_serial_invalid_3',
    consumers=CONSUMERS,
    clauses=[],
    default_value=RESPONSES_INVALID[3],
)
async def test_invalid_experiments(taxi_signal_device_api, serial_number):
    request = copy.deepcopy(REQUEST)
    request['serial_number'] = serial_number
    response = await taxi_signal_device_api.post(ENDPOINT, json=request)
    assert response.status_code == 500, response.text
    assert response.json() == ERROR_RESPONSE


@pytest.mark.experiments3(
    match={
        'predicate': {
            'init': {
                'arg_name': 'linux_version',
                'arg_type': 'version',
                'value': '1.3.50',
            },
            'type': 'lt',  # lt - <
        },
        'enabled': True,
    },
    name='linux_version',
    consumers=CONSUMERS,
    clauses=[],
    default_value=RESPONSE,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': False},
    name='default_disabled',
    consumers=CONSUMERS,
    clauses=[],
    default_value=RESPONSE_MISSING,
)
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'linux_version, excepted_response, expected_code',
    [
        ('0.0.1', RESPONSE, 200),
        (
            '1.3.3-3.linux-yandex_2.1-dev_69883f2d_202110251029_TAXICAMERA-1480',  # noqa: E501
            RESPONSE,
            200,
        ),
        (
            '1.3.6-3.linux-yandex_2.1-dev_69883f2d_202110251029_TAXICAMERA-1480',  # noqa: E501
            RESPONSE,
            200,
        ),
        (
            '1.6-3.linux-yandex_2.1-dev_69883f2d_202110251029_TAXICAMERA-1480',  # noqa: E501
            BAD_REQUEST_ERROR,
            400,
        ),
        (
            '1.3.61-3.linux-yandex_2.1-dev_69883f2d_202110251029_TAXICAMERA-1480',  # noqa: E501
            ERROR_RESPONSE,
            500,
        ),
    ],
)
async def test_linux_version_ok(
        taxi_signal_device_api,
        pgsql,
        linux_version,
        excepted_response,
        expected_code,
):
    request = copy.deepcopy(REQUEST)
    request['linux_version'] = linux_version
    response = await taxi_signal_device_api.post(ENDPOINT, json=request)
    assert response.status_code == expected_code, response.text
    assert response.json() == excepted_response
    if expected_code == 200:
        common.check_alr_inserted(
            pgsql,
            serial_number=SERIAL_NUMBER,
            field_affected='v1_binaries_check_at',
        )
