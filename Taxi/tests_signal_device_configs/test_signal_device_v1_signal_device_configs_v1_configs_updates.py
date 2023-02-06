import pytest

from tests_signal_device_configs import common_patches as cp

ENDPOINT = '/signal-device/v1/signal-device-configs/v1/configs/updates'


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
@pytest.mark.parametrize(
    'park_id, serial_number, software_version, if_modified_since, '
    'expected_code, expected_response',
    [
        (
            None,
            'AAA2TT00LL22FF',
            '0.6-3',
            '2019-09-12T00:00:59+03:00',
            200,
            {'config_updates': [cp.DEFAULT_JSON_PATCH]},
        ),
        (
            None,
            'AAA2TT00LL22FF',
            '0.6-3',
            '2019-09-12T00:01:00+03:00',
            304,
            None,
        ),
        (
            'p1',
            'AAA2TT00LL22FF',
            '0.5-2',
            '2019-12-11T20:00:00+03:00',
            304,
            None,
        ),
        (
            'p1',
            'AAA2TT00LL22FF',
            '0.6-3',
            '2019-12-11T20:00:00+03:00',
            200,
            {
                'config_updates': [
                    cp.P1_FEATURES_JSON_PATCH,
                    cp.OTHER_JSON_PATCH,
                    cp.DEFAULT_JSON_PATCH,
                ],
            },
        ),
        (
            'p1',
            'BBB2TT00LL22FF',
            '0.5-3',
            '2019-12-11T20:00:00+03:00',
            200,
            {
                'config_updates': [
                    cp.P1_FEATURES_JSON_PATCH,
                    cp.SYSTEM_JSON_PATCH1,
                    cp.DEFAULT_JSON_PATCH,
                ],
            },
        ),
        (
            'p1',
            'BBB2TT00LL22FF',
            '0.6-3',
            '2019-12-11T20:00:00+03:00',
            200,
            {
                'config_updates': [
                    cp.P1_FEATURES_JSON_PATCH,
                    cp.OTHER_JSON_PATCH,
                    cp.SYSTEM_JSON_PATCH2,
                    cp.DEFAULT_JSON_PATCH,
                ],
            },
        ),
        (
            'p2',
            'BBB2TT00LL22FF',
            '0.0.7-3',
            '2019-12-11T20:00:00+03:00',
            200,
            {
                'config_updates': [
                    cp.P2_FEATURES_JSON_PATCH,
                    cp.DEFAULT_JSON_PATCH,
                ],
            },
        ),
        (
            'p2',
            'AAA2TT00LL22FF',
            '0.0.7-3',
            '2019-12-11T20:00:00+03:00',
            200,
            {
                'config_updates': [
                    cp.P2_FEATURES_JSON_PATCH,
                    cp.SYSTEM_JSON_PATCH2,
                    cp.DEFAULT_JSON_PATCH,
                ],
            },
        ),
        (
            'p2',
            'AAA2TT00LL22FF',
            '0.0.7-3',
            '2019-12-16T00:10:00+03:00',
            304,
            None,
        ),
    ],
)
async def test_updates(
        taxi_signal_device_configs,
        park_id,
        serial_number,
        software_version,
        if_modified_since,
        expected_code,
        expected_response,
):
    headers = {'If-Modified-Since': if_modified_since}
    body = {
        'serial_number': serial_number,
        'software_version': software_version,
        'park_id': park_id,
    }
    response = await taxi_signal_device_configs.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == expected_code
    if expected_response is not None:
        assert (
            sorted(response.json()['config_updates'], key=lambda x: x['name'])
            == sorted(
                expected_response['config_updates'], key=lambda x: x['name'],
            )
        )
