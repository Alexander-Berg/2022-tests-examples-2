import pytest

from tests_signal_device_api import common

ENDPOINT = 'v1/config'

DEVICE_PRIMARY_KEY = 1
DEVICE_ID = '13c140cb-7dde-499c-be6e-57c010a45299'
TIMESTAMP = '2019-04-19T13:40:00Z'
CONSUMERS = ['signal_device_api/v1_config']
SERIAL_NUMBER = 'abcdef1234567890'
SERIAL_NUMBERS_INVALID_EXPERIMENTS = ['invalid_serial1', 'invalid_serial2']
SOFTWARE_VERSION = '1.2-3'
REQUEST_JSON_OK = {
    'device_id': DEVICE_ID,
    'timestamp': TIMESTAMP,
    'serial_number': SERIAL_NUMBER,
    'software_version': SOFTWARE_VERSION,
}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='test_ok_serial_match',
    consumers=CONSUMERS,
    clauses=[
        {
            'title': 'experiment_invalid_serial_list',
            'value': common.COMPLEX_CONFIG,
            'predicate': {
                'init': {
                    'set': [SERIAL_NUMBER],
                    'arg_name': 'serial_number',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
        {
            'title': 'experiment_default',
            'value': common.SIMPLE_CONFIG,
            'predicate': {'type': 'true'},
        },
    ],
    default_value=common.SIMPLE_CONFIG,
)
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok_serial_match(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, serial_number=SERIAL_NUMBER,
    )
    json_body = REQUEST_JSON_OK
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'config_fingerprint': (
            '81be00623d0be3416b50d42586f840a46b6e26c2c8224da110da7da53c89850e'
        ),
        'config_value': common.COMPLEX_CONFIG,
    }


@pytest.mark.parametrize(
    'software_version, expected_config',
    [
        (
            '1.2-3',
            {
                'config_fingerprint': (
                    'cb87ef968fd29f44d410745f7362c892'
                    'e7232eadad9facf26ac90620e163d1ff'
                ),
                'config_value': common.COMPLEX_CONFIG,
            },
        ),
        (
            '1.2-3.smth',
            {
                'config_fingerprint': (
                    'cb87ef968fd29f44d410745f7362c892'
                    'e7232eadad9facf26ac90620e163d1ff'
                ),
                'config_value': common.COMPLEX_CONFIG,
            },
        ),
        (
            '1.1.2-3',
            {
                'config_fingerprint': (
                    '9347bf184bd7a4b8da9358f5807acb81'
                    '7b3f0b4acc4b67d58ef4523f0facd84e'
                ),
                'config_value': common.SIMPLE_CONFIG2,
            },
        ),
        (
            '1.1.2-3.smth',
            {
                'config_fingerprint': (
                    '9347bf184bd7a4b8da9358f5807acb81'
                    '7b3f0b4acc4b67d58ef4523f0facd84e'
                ),
                'config_value': common.SIMPLE_CONFIG2,
            },
        ),
        (
            '0.0.0-0',
            {
                'config_fingerprint': (
                    'bbc0b529a92c7e62edc3dde67d28dd2d'
                    'f0cb57161aed31d356a99609c66dccef'
                ),
                'config_value': common.SIMPLE_CONFIG3,
            },
        ),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='test_ok_software_version_filter',
    consumers=CONSUMERS,
    clauses=[
        {
            'title': 'new_software_version',
            'value': common.SIMPLE_CONFIG2,
            'predicate': {
                'init': {
                    'arg_name': 'software_version',
                    'arg_type': 'string',
                    'value': '0000000001.0000000001.0000000002-0000000003',
                },
                'type': 'gte',
            },
        },
        {
            'title': 'experiment_software_version_filter_gt',
            'value': common.SIMPLE_CONFIG,
            'predicate': {
                'init': {
                    'arg_name': 'software_version',
                    'arg_type': 'string',
                    'value': '0000000000.0000000001.0000000002-0000000003',
                },
                'type': 'gt',
            },
        },
        {
            'title': 'experiment_software_version_filter_match',
            'value': common.COMPLEX_CONFIG,
            'predicate': {
                'init': {
                    'arg_name': 'software_version',
                    'arg_type': 'string',
                    'value': '0000000000.0000000001.0000000002-0000000003',
                },
                'type': 'gte',
            },
        },
    ],
    default_value=common.SIMPLE_CONFIG3,
)
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok_software_version_filter(
        taxi_signal_device_api, pgsql, software_version, expected_config,
):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, serial_number=SERIAL_NUMBER,
    )
    json_body = REQUEST_JSON_OK
    json_body['software_version'] = software_version
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_config


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='test_ok_software_canonization',
    consumers=CONSUMERS,
    clauses=[
        {
            'title': 'experiment_software_version_filter_canonization',
            'value': common.SIMPLE_CONFIG,
            'predicate': {
                'init': {
                    'arg_name': 'software_version',
                    'arg_type': 'string',
                    'value': '0000000000.0000000090.0000020020-0000300000',
                },
                'type': 'gt',
            },
        },
        {
            'title': 'experiment_software_version_filter_match',
            'value': common.COMPLEX_CONFIG,
            'predicate': {
                'init': {
                    'arg_name': 'software_version',
                    'arg_type': 'string',
                    'value': '0000000000.0000000090.0000020020-0000000000',
                },
                'type': 'gte',
            },
        },
        {
            'title': 'experiment_default',
            'value': common.SIMPLE_CONFIG,
            'predicate': {'type': 'true'},
        },
    ],
    default_value=common.SIMPLE_CONFIG,
)
@pytest.mark.pgsql('signal_device_api_meta_db')
@pytest.mark.parametrize(
    'software_version',
    [
        '090.0020020-1',
        '090.0020020-1.SOME_ENDING',
        '090.0020020-1.',
        '0.090.0020020-1',
        '0.090.0020020-1.SOME_ENDING',
        '0.090.0020020-1.',
    ],
)
async def test_ok_software_canonization(
        taxi_signal_device_api, pgsql, software_version,
):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, serial_number=SERIAL_NUMBER,
    )
    json_body = REQUEST_JSON_OK
    json_body['software_version'] = software_version
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'config_fingerprint': (
            'd33720c7b7994c0f476fd39b217fabd04b3372377071930ea2cab00cbba8d103'
        ),
        'config_value': common.COMPLEX_CONFIG,
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='test_ok_default',
    consumers=CONSUMERS,
    clauses=[
        {
            'title': 'experiment_invalid_serial_list',
            'value': common.SIMPLE_CONFIG,
            'predicate': {
                'init': {
                    'set': SERIAL_NUMBERS_INVALID_EXPERIMENTS,
                    'arg_name': 'serial_number',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
        {
            'title': 'experiment_default',
            'value': common.COMPLEX_CONFIG,
            'predicate': {'type': 'true'},
        },
    ],
    default_value=common.SIMPLE_CONFIG,
)
@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_ok_default(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    json_body = REQUEST_JSON_OK
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'config_fingerprint': (
            '45c359cec5092d881728031ce4f87753d73aed14c871e26aba6ecc858ba651de'
        ),
        'config_value': common.COMPLEX_CONFIG,
    }


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_unregistered_device(taxi_signal_device_api):
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers=common.MISSING_JWT_HEADER_FOR_UNREGISTERED,
        json=REQUEST_JSON_OK,
    )
    assert response.status_code == 400, response.text
    assert response.json() == common.response_400_not_registered(DEVICE_ID)


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_dead_device(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID, False,
    )
    json_body = REQUEST_JSON_OK
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={
            common.JWT_HEADER_NAME: common.generate_jwt(
                private_key, ENDPOINT, {}, json_body,
            ),
        },
        json=json_body,
    )
    assert response.status_code == 400, response.text
    assert response.json() == common.response_400_not_alive(DEVICE_ID)


@pytest.mark.pgsql('signal_device_api_meta_db')
async def test_403(taxi_signal_device_api, pgsql):
    private_key = common.add_device_return_private_key(
        pgsql, DEVICE_PRIMARY_KEY, DEVICE_ID,
    )
    json_body = REQUEST_JSON_OK
    jwt = common.generate_jwt(private_key, ENDPOINT, {}, json_body)
    mutated_jwt = jwt[:-8] + 'AAAAAAAA'
    response = await taxi_signal_device_api.post(
        ENDPOINT,
        headers={common.JWT_HEADER_NAME: mutated_jwt},
        json=json_body,
    )
    assert response.status_code == 403, response.text
    assert response.json() == common.RESPONSE_403_INVALID_SIGNATURE
