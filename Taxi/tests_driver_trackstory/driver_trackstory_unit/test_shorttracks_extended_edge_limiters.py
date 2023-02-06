# pylint: disable=import-error

import datetime

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

_EDGE_LIMITS = {}
_EDGE_LIMITS['max_alternatives_track_length'] = 20
_EDGE_LIMITS['max_alternatives_for_position_count'] = 15
_EDGE_LIMITS['max_points_count'] = 40

EDGE_TRACKS_CHANNEL = 'channel:yaga:edge_positions'


def _to_timestamp(time_point):
    return int(utils.timestamp(time_point))


def _generate_driver_one_message(
        driver_id, now, add_value, alternatives_count=10,
):
    drivers = []

    timestamp = _to_timestamp(now)
    alternatives = []
    for j in range(alternatives_count):
        alternative = {
            'position': [timestamp % 1000, j + add_value],
            'probability': (
                1.0
            ),  # probability is not used, likelihood is used instead
            'position_on_edge': (1.0 * add_value) / 100.0,
            'edge_id': j + add_value,
            'speed': j + add_value,
            'log_likelihood': -add_value + j,
        }
        alternatives.append(alternative)

    drivers.append(
        {
            'driver_id': driver_id,
            'positions': alternatives,
            'timestamp': timestamp * 1000,
        },
    )

    return drivers


@pytest.mark.now('2019-03-09T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {
                'max_age_seconds': 1500,
                'max_points_count': _EDGE_LIMITS['max_points_count'],
            },
        },
        'extended': {
            'enabled': True,
            'storage': {
                'max_age_seconds': 1500,
                'max_points_count': _EDGE_LIMITS[
                    'max_alternatives_track_length'
                ],
                'max_alternatives_count': _EDGE_LIMITS[
                    'max_alternatives_for_position_count'
                ],
            },
        },
    },
)
async def test_limiters(
        taxi_driver_trackstory_adv, redis_store, now, taxi_config,
):
    prefix = 'edge_ext_limiters_'
    drivers_ids = [prefix + 'aadbid_uuid_9', prefix + 'bbdbid_uuid_10']

    for driver_id in drivers_ids:
        timestamp = now - datetime.timedelta(seconds=30)
        history_length = _EDGE_LIMITS['max_alternatives_track_length'] * 3
        alternatives_count = (
            _EDGE_LIMITS['max_alternatives_for_position_count'] * 3
        )
        driver_add_value = hash(driver_id) % 100
        positions_interval_sec = 2
        now_time = None
        messages = []
        # send adjusted and raw messages
        for i in range(0, history_length):
            now_time = timestamp + datetime.timedelta(
                seconds=positions_interval_sec * i,
            )
            message = _generate_driver_one_message(
                driver_id, now_time, driver_add_value, alternatives_count,
            )
            messages += message

            await taxi_driver_trackstory_adv.sync_send_to_channel(
                EDGE_TRACKS_CHANNEL,
                geobus.serialize_edge_positions_v2(messages, now_time),
            )

        check_alt_outer = [
            i
            for i in range(
                1, _EDGE_LIMITS['max_alternatives_track_length'] * 2,
            )
            if i % 7 == 0
        ]
        check_alt_inner = [
            i
            for i in range(
                1, _EDGE_LIMITS['max_alternatives_for_position_count'] * 2,
            )
            if i % 7 == 0
        ]

        for value_alt_outer in check_alt_outer:
            for value_alt_inner in check_alt_inner:
                response = await taxi_driver_trackstory_adv.post(
                    'shorttracks_extended',
                    json={
                        'driver_ids': drivers_ids,
                        'alternatives_outer_num_positions': value_alt_outer,
                        'alternatives_inner_num_positions': value_alt_inner,
                    },
                )

                assert response.status_code == 200
                data = response.json()

                driver_data = data[driver_id]

                outer_should_be = min(
                    value_alt_outer,
                    _EDGE_LIMITS['max_alternatives_track_length'],
                )
                inner_should_be = min(
                    value_alt_inner,
                    _EDGE_LIMITS['max_alternatives_for_position_count'],
                )
                assert len(driver_data['alternatives']) == outer_should_be
                for alternatives_array in driver_data['alternatives']:
                    assert len(alternatives_array) == inner_should_be

        # try to overcome config values
        # ensuring stripping
        check_adjusted = [
            i
            for i in range(1, _EDGE_LIMITS['max_points_count'] * 2)
            if i % 7 == 0
        ]
        for value in check_adjusted:
            response = await taxi_driver_trackstory_adv.post(
                'shorttracks_extended',
                json={
                    'driver_ids': drivers_ids,
                    'adjusted_num_positions': value,
                },
            )

            assert response.status_code == 200
            data = response.json()

            driver_data = data[driver_id]
            should_be = min(value, _EDGE_LIMITS['max_points_count'])

            assert len(driver_data['adjusted']) == should_be
