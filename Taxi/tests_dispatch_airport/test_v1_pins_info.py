import pytest

from tests_dispatch_airport import common
import tests_dispatch_airport.utils as utils


@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
async def test_v1_pins_info(taxi_dispatch_airport):
    url = '/v1/pins_info'
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER
    response = await taxi_dispatch_airport.get(url, headers=headers)
    r_json = response.json()
    for value in r_json.values():
        value.sort(key=lambda info: info['allowed_class'])

    assert r_json == {
        'ekb': [
            {
                'allowed_class': 'comfortplus',
                'expected_wait_time': 1500,
                'demand': 19,
            },
            {
                'allowed_class': 'econom',
                'expected_wait_time': 1320,
                'demand': 19,
            },
            {'allowed_class': 'vip', 'demand': 20},
        ],
        'svo': [
            {'allowed_class': 'comfortplus', 'demand': 20},
            {'allowed_class': 'vip', 'demand': 20},
        ],
    }


@pytest.mark.parametrize(
    'config_bits, pins_count',
    [
        ({'pin_info_enabled': True}, 1),
        ({'pin_info_enabled': False}, 0),
        ({}, 1),
    ],
)
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
async def test_v1_pins_info_enabled(
        taxi_dispatch_airport, taxi_config, config_bits, pins_count,
):
    config = utils.custom_config(True)
    config['DISPATCH_AIRPORT_ZONES']['ekb'].update(config_bits)
    taxi_config.set_values(config)
    headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER
    response = await taxi_dispatch_airport.get(
        '/v1/pins_info', headers=headers,
    )
    assert len(response.json()) == pins_count
