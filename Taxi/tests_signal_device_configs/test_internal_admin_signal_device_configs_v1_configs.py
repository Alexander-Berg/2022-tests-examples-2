import copy
import typing

import pytest

from tests_signal_device_configs import common_patches as cp

ENDPOINT = '/internal-admin/signal-device-configs/v1/configs'
DEVICE_ENDPOINT = '/signal-device-api-admin/internal-admin/signal-device-api-admin/v1/devices/list'  # noqa E501

DEVICE_LIST_RESPONSE = {
    'AAA2TT00LL22FF': [
        {
            'status': {
                'software_version': (
                    '0000000000.0000000000.0000000006-0000000003'
                ),
            },
            'park_device_profile': {'park_id': 'p1'},
        },
    ],
    'BBB2TT00LL22FF': [
        {
            'status': {
                'software_version': (
                    '0000000000.0000000000.0000000006-0000000003'
                ),
            },
            'park_device_profile': {'park_id': 'p2'},
        },
    ],
    'CCC2TT00LL22FF': [],
}


DEFAULT_JSON_PATCH: typing.Dict[str, typing.Any] = copy.deepcopy(
    cp.DEFAULT_JSON_PATCH,
)
P1_FEATURES_JSON_PATCH: typing.Dict[str, typing.Any] = copy.deepcopy(
    cp.P1_FEATURES_JSON_PATCH,
)
P2_FEATURES_JSON_PATCH: typing.Dict[str, typing.Any] = copy.deepcopy(
    cp.P2_FEATURES_JSON_PATCH,
)
OTHER_JSON_PATCH: typing.Dict[str, typing.Any] = copy.deepcopy(
    cp.OTHER_JSON_PATCH,
)
DEFAULT_JSON_PATCH['id'] = 6
P1_FEATURES_JSON_PATCH['id'] = 1
P2_FEATURES_JSON_PATCH['id'] = 5
OTHER_JSON_PATCH['id'] = 3


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
@pytest.mark.parametrize(
    'serial_number, expected_code, expected_response',
    [
        (
            'BBB2TT00LL22FF',
            200,
            {'config_updates': [P2_FEATURES_JSON_PATCH, DEFAULT_JSON_PATCH]},
        ),
        (
            'AAA2TT00LL22FF',
            200,
            {
                'config_updates': [
                    P1_FEATURES_JSON_PATCH,
                    OTHER_JSON_PATCH,
                    DEFAULT_JSON_PATCH,
                ],
            },
        ),
        ('CCC2TT00LL22FF', 200, {'config_updates': [DEFAULT_JSON_PATCH]}),
    ],
)
async def test_updates(
        taxi_signal_device_configs,
        mockserver,
        serial_number,
        expected_code,
        expected_response,
):
    @mockserver.json_handler(DEVICE_ENDPOINT)
    def devices_list(request):
        return {
            'items': DEVICE_LIST_RESPONSE[
                request.json['filter']['conditions'][0]['value']
            ],
        }

    response = await taxi_signal_device_configs.get(
        ENDPOINT, params={'serial_number': serial_number},
    )
    assert response.status_code == expected_code, response.text
    assert devices_list.times_called == 1
    if expected_response:
        assert (
            sorted(response.json()['config_updates'], key=lambda x: x['name'])
            == sorted(
                expected_response['config_updates'], key=lambda x: x['name'],
            )
        )


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs_no_patch.sql'],
)
async def test_no_patch(taxi_signal_device_configs, mockserver):
    @mockserver.json_handler(DEVICE_ENDPOINT)
    def devices_list(request):
        return {'items': [{'CCC2TT00LL22FF': []}]}

    response = await taxi_signal_device_configs.get(
        ENDPOINT, params={'serial_number': 'CCC2TT00LL22FF'},
    )
    assert devices_list.times_called == 1
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'no_patches',
        'message': 'no patch for device with serial number: CCC2TT00LL22FF',
    }
