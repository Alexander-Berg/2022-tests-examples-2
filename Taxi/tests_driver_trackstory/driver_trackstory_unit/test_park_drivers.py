# pylint: disable=import-error
import datetime
import math

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

TRACKS_CHANNEL = 'channel:yagr:position'
EDGE_TRACKS_CHANNEL = 'channel:yaga:edge_positions'


def _get_raw_channel_message(driver_id, now):
    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55, 37],
            'direction': 45,
            'timestamp': timestamp,
            'speed': 16,
            'accuracy': 1,
        },
    ]
    return geobus.serialize_positions_v2(drivers, now)


def _get_edge_channel_message(driver_id, now):
    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55, 37],
            'direction': 45,
            'timestamp': timestamp * 1000,  # milliseconds
            'speed': 16,
        },
    ]
    return geobus.serialize_edge_positions_v2(drivers, now)


@pytest.mark.now('2020-09-02T12:30:00Z')
async def test_not_found(taxi_driver_trackstory):
    request_body = {'park_id': 'not_existed_park'}
    response = await taxi_driver_trackstory.post(
        'park_drivers', json=request_body,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['drivers'] == []


@pytest.mark.now('2020-09-02T12:30:00Z')
async def test_found_basic(taxi_driver_trackstory_adv, now):
    driver_mixed = 'driver_mixed'
    driver_edge = 'driver_only_edge'
    driver_raw = 'driver_only_raw'
    park = 'park1'
    for i in range(2, 10):
        baseline_time = now - datetime.timedelta(seconds=i * 5)
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            EDGE_TRACKS_CHANNEL,
            _get_edge_channel_message(
                park + '_' + driver_mixed, baseline_time,
            ),
        )
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            TRACKS_CHANNEL,
            _get_raw_channel_message(park + '_' + driver_mixed, baseline_time),
        )

        await taxi_driver_trackstory_adv.sync_send_to_channel(
            EDGE_TRACKS_CHANNEL,
            _get_edge_channel_message(
                park + '_' + driver_edge,
                baseline_time - datetime.timedelta(seconds=3),
            ),
        )
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            TRACKS_CHANNEL,
            _get_raw_channel_message(
                park + '_' + driver_raw,
                baseline_time - datetime.timedelta(seconds=2),
            ),
        )

    response = await taxi_driver_trackstory_adv.post(
        'park_drivers', json={'park_id': park},
    )
    assert response.status_code == 200
    data = response.json()

    should_be = {
        driver_mixed: {
            'ts': int(
                utils.timestamp(now - datetime.timedelta(seconds=2 * 5)),
            ),
            'position': [55.0, 37.0],
            'direction': 45,
        },
        driver_edge: {
            'ts': int(
                utils.timestamp(
                    now
                    - datetime.timedelta(seconds=2 * 5)
                    - datetime.timedelta(seconds=3),
                ),
            ),
            'position': [55.0, 37.0],
            'direction': 45,
        },
        driver_raw: {
            'ts': int(
                utils.timestamp(
                    now
                    - datetime.timedelta(seconds=2 * 5)
                    - datetime.timedelta(seconds=2),
                ),
            ),
            'position': [55.0, 37.0],
            'direction': 45,
        },
    }

    response_is = {}
    for driver in data['drivers']:
        response_is[driver['driver_id']] = {
            'ts': driver['position']['timestamp'],
            'position': [driver['position']['lon'], driver['position']['lat']],
            'direction': driver['position']['direction'],
        }
        assert math.isclose(driver['position']['speed'], 16.0, abs_tol=10e-2)
    assert should_be == response_is


@pytest.mark.now('2020-09-02T12:30:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 1, 'max_points_count': 10},
        },
    },
)
async def test_not_found_too_old(taxi_driver_trackstory_adv, now):
    driver_mixed = 'driver_mixed'
    driver_edge = 'driver_only_edge'
    driver_raw = 'driver_only_raw'
    park = 'park2'
    for i in range(5, 10):
        baseline_time = now - datetime.timedelta(seconds=i * 5)
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            EDGE_TRACKS_CHANNEL,
            _get_edge_channel_message(
                park + '_' + driver_mixed, baseline_time,
            ),
        )
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            TRACKS_CHANNEL,
            _get_raw_channel_message(park + '_' + driver_mixed, baseline_time),
        )

        await taxi_driver_trackstory_adv.sync_send_to_channel(
            EDGE_TRACKS_CHANNEL,
            _get_edge_channel_message(
                park + '_' + driver_edge,
                baseline_time - datetime.timedelta(seconds=3),
            ),
        )
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            TRACKS_CHANNEL,
            _get_raw_channel_message(
                park + '_' + driver_raw,
                baseline_time - datetime.timedelta(seconds=2),
            ),
        )

    response = await taxi_driver_trackstory_adv.post(
        'park_drivers', json={'park_id': park},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['drivers'] == []
