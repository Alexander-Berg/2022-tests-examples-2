# pylint: disable=import-error,invalid-name

import datetime
import math
import time

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

from tests_driver_trackstory.driver_trackstory_unit import fbs_convertation

EDGE_TRACKS_CHANNEL = 'channel:yaga:edge_positions'

# Enable shorttracks config globaly
pytestmark = pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 1500, 'max_points_count': 20},
        },
        'extended': {
            'enabled': True,
            'storage': {
                'max_age_seconds': 1500,
                'max_points_count': 30,
                'max_alternatives_count': 7,
            },
        },
    },
)


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


def _serialize_drivers_messages_for_redis(messages, now):
    return geobus.serialize_edge_positions_v2(messages, now)


async def _send_and_wait_message_received(
        taxi_driver_trackstory,
        redis_store,
        driver_id,
        point_type,
        timestamp,
        max_tries=30,
        retry_channel=None,
        retry_message=None,
):
    # send
    if retry_channel is not None and retry_message is not None:
        redis_store.publish(retry_channel, retry_message)

    # wait while track-geobus-saver component receives message
    for _ in range(max_tries):
        response = await taxi_driver_trackstory.post(
            'shorttracks_extended',
            json={
                'driver_ids': [driver_id],
                'adjusted_num_positions': 5,
                'raw_num_positions': 5,
            },
        )
        data = response.json()
        if (
                driver_id in data
                and point_type in data[driver_id]
                and data[driver_id][point_type]
                and data[driver_id][point_type][-1]['timestamp'] == timestamp
        ):
            return

        # resend
        if retry_channel is not None and retry_message is not None:
            redis_store.publish(retry_channel, retry_message)

        time.sleep(0.5)

    # if failed to receive message
    assert False


def _pos_are_eq(hist_pos, hist_pos_timestamp, resp_pos):
    return (
        (hist_pos['position'][0], hist_pos['position'][1])
        == (resp_pos['lon'], resp_pos['lat'])
        and resp_pos['speed'] == hist_pos['speed']
        and resp_pos['timestamp'] == hist_pos_timestamp
        and resp_pos['direction'] == hist_pos['direction']
        and resp_pos['accuracy'] == hist_pos['accuracy']
    )


@pytest.mark.now('2019-03-09T00:00:00Z')
@pytest.mark.config(
    SHORTTRACKS_SETTINGS={
        'max_age_seconds': 1500,
        'max_points_count': 20,
        'low_distance_filter_enable': False,
        'low_distance_filter_time_seconds': 60,
        'low_distance_filter_distance_meters': 10,
    },
)
@pytest.mark.config(
    SHORTTRACKS_EXTENDED_SETTINGS={
        'max_alternatives_track_length': 30,
        'max_alternatives_for_position_count': 7,
    },
)
async def test_not_found(taxi_driver_trackstory):
    request_body = {
        'driver_ids': ['123', '456'],
        'raw_num_positions': 20,
        'adjusted_num_positions': 20,
        'alternatives_outer_num_positions': 30,
        'alternatives_inner_num_positions': 20,
    }
    response = await taxi_driver_trackstory.post(
        'shorttracks_extended', json=request_body,
    )

    assert response.status_code == 200
    data = response.json()
    assert data['123'] == {'raw': [], 'adjusted': [], 'alternatives': []}
    assert data['456'] == {'raw': [], 'adjusted': [], 'alternatives': []}


_EDGE_MAX_ALTERNATIVES_TRACK_LENGTH = 20


@pytest.mark.now('2019-03-09T00:00:00Z')
@pytest.mark.config(
    SHORTTRACKS_SETTINGS={
        'max_age_seconds': 1500,
        'max_points_count': 20,
        'low_distance_filter_enable': False,
        'low_distance_filter_time_seconds': 60,
        'low_distance_filter_distance_meters': 10,
    },
)
@pytest.mark.config(
    SHORTTRACKS_EXTENDED_SETTINGS={
        'max_alternatives_track_length': _EDGE_MAX_ALTERNATIVES_TRACK_LENGTH,
        'max_alternatives_for_position_count': 7,
    },
)
async def test_found_driver(
        taxi_driver_trackstory, redis_store, now, taxi_config,
):
    prefix = 'edge_ext_fbs_'
    drivers_ids = [prefix + 'aadbid_uuid_0', prefix + 'bbdbid_uuid_1']

    for driver_id in drivers_ids:
        timestamp = now - datetime.timedelta(seconds=30)
        history_length = _EDGE_MAX_ALTERNATIVES_TRACK_LENGTH * 2
        alternatives_count = 10
        driver_add_value = hash(driver_id) % 100
        positions_interval_sec = 5
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

            message_pack = message
            await _send_and_wait_message_received(
                taxi_driver_trackstory,
                redis_store,
                driver_id,
                'adjusted',
                _to_timestamp(now_time),
                max_tries=30,
                retry_channel=EDGE_TRACKS_CHANNEL,
                retry_message=_serialize_drivers_messages_for_redis(
                    message_pack, now_time,
                ),
            )

        adj_num_pos_cnt = 9
        alt_outer_num_pos_cnt = 4
        alt_inner_num_pos_cnt = 7
        response = await taxi_driver_trackstory.post(
            'shorttracks_extended',
            json={
                'driver_ids': drivers_ids,
                'adjusted_num_positions': adj_num_pos_cnt,
                'alternatives_outer_num_positions': alt_outer_num_pos_cnt,
                'alternatives_inner_num_positions': alt_inner_num_pos_cnt,
            },
        )
        assert response.status_code == 200
        data = response.json()

        driver_data = data[driver_id]

        assert not driver_data['raw']

        # check that [-1] position is the most recent, and [0] position
        # is the most oldest
        most_recent_time = now_time
        oldest_time_for_alternatives = now_time - datetime.timedelta(
            seconds=positions_interval_sec * (alt_outer_num_pos_cnt - 1),
        )
        oldest_time_for_adjusted = now_time - datetime.timedelta(
            seconds=positions_interval_sec * (adj_num_pos_cnt - 1),
        )

        assert driver_data['adjusted'][0]['timestamp'] == _to_timestamp(
            oldest_time_for_adjusted,
        )
        assert driver_data['adjusted'][-1]['timestamp'] == _to_timestamp(
            most_recent_time,
        )

        assert driver_data['alternatives'][0][0]['timestamp'] == _to_timestamp(
            oldest_time_for_alternatives,
        )
        assert driver_data['alternatives'][-1][0][
            'timestamp'
        ] == _to_timestamp(most_recent_time)

        # check that smth_num_position is working
        assert len(driver_data['adjusted']) == adj_num_pos_cnt
        assert len(driver_data['alternatives']) == alt_outer_num_pos_cnt
        for alternatives_array in driver_data['alternatives']:
            assert len(alternatives_array) == alt_inner_num_pos_cnt

        last_messages = messages[-alt_outer_num_pos_cnt:]
        for i in range(alt_outer_num_pos_cnt):
            driver_history_point = last_messages[i]
            for j in range(alt_inner_num_pos_cnt):
                pos_in_hist = driver_history_point['positions'][j]
                time_in_hist = driver_history_point['timestamp']
                pos_in_response = driver_data['alternatives'][i][j]
                _pos_are_eq(pos_in_hist, time_in_hist, pos_in_response)


@pytest.mark.now('2019-03-09T00:00:00Z')
@pytest.mark.config(
    SHORTTRACKS_SETTINGS={
        'max_age_seconds': 1500,
        'max_points_count': 20,
        'low_distance_filter_enable': False,
        'low_distance_filter_time_seconds': 60,
        'low_distance_filter_distance_meters': 10,
    },
)
@pytest.mark.config(
    SHORTTRACKS_EXTENDED_SETTINGS={
        'max_alternatives_track_length': _EDGE_MAX_ALTERNATIVES_TRACK_LENGTH,
        'max_alternatives_for_position_count': 7,
    },
)
async def test_found_driver_fbs(
        taxi_driver_trackstory, redis_store, now, taxi_config,
):
    prefix = 'edge_ext_fbs_'
    drivers_ids = [prefix + 'aadbid_uuid_0', prefix + 'bbdbid_uuid_1']

    for driver_id in drivers_ids:
        timestamp = now - datetime.timedelta(seconds=30)
        history_length = _EDGE_MAX_ALTERNATIVES_TRACK_LENGTH * 2
        alternatives_count = 10
        driver_add_value = hash(driver_id) % 100
        positions_interval_sec = 5
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

            message_pack = message
            await _send_and_wait_message_received(
                taxi_driver_trackstory,
                redis_store,
                driver_id,
                'adjusted',
                _to_timestamp(now_time),
                max_tries=30,
                retry_channel=EDGE_TRACKS_CHANNEL,
                retry_message=_serialize_drivers_messages_for_redis(
                    message_pack, now_time,
                ),
            )

        adj_num_pos_cnt = 9
        alt_outer_num_pos_cnt = 4
        alt_inner_num_pos_cnt = 7
        response = await taxi_driver_trackstory.post(
            'v2/shorttracks_extended',
            json={
                'driver_ids': drivers_ids,
                'response_content_type': 'fbs',
                'adjusted_num_positions': adj_num_pos_cnt,
                'alternatives_outer_num_positions': alt_outer_num_pos_cnt,
                'alternatives_inner_num_positions': alt_inner_num_pos_cnt,
            },
        )
        assert response.status_code == 200

        drivers_data = fbs_convertation.convert_fbs_to_local_repr(
            response.content,
        )
        driver_data = drivers_data[driver_id]

        # check that [-1] position is the most recent, and [0] position
        # is the most oldest
        most_recent_time = now_time
        oldest_time_for_alternatives = now_time - datetime.timedelta(
            seconds=positions_interval_sec * (alt_outer_num_pos_cnt - 1),
        )
        oldest_time_for_adjusted = now_time - datetime.timedelta(
            seconds=positions_interval_sec * (adj_num_pos_cnt - 1),
        )

        assert driver_data['adjusted'][0]['timestamp'] == _to_timestamp(
            oldest_time_for_adjusted,
        )
        assert driver_data['adjusted'][-1]['timestamp'] == _to_timestamp(
            most_recent_time,
        )

        assert driver_data['alternatives'][0][0]['timestamp'] == _to_timestamp(
            oldest_time_for_alternatives,
        )
        assert driver_data['alternatives'][-1][0][
            'timestamp'
        ] == _to_timestamp(most_recent_time)

        # check that smth_num_position is working
        assert len(driver_data['adjusted']) == adj_num_pos_cnt
        assert len(driver_data['alternatives']) == alt_outer_num_pos_cnt
        for alternatives_array in driver_data['alternatives']:
            assert len(alternatives_array) == alt_inner_num_pos_cnt

        last_messages = messages[-alt_outer_num_pos_cnt:]
        for i in range(alt_outer_num_pos_cnt):
            driver_history_point = last_messages[i]
            # check adjusted
            _pos_are_eq(
                driver_history_point['positions'][0],
                driver_history_point['timestamp'],
                driver_data['adjusted'][i],
            )

            for j in range(alt_inner_num_pos_cnt):
                pos_in_hist = driver_history_point['positions'][j]
                time_in_hist = driver_history_point['timestamp']
                pos_in_response = driver_data['alternatives'][i][j]
                _pos_are_eq(pos_in_hist, time_in_hist, pos_in_response)
