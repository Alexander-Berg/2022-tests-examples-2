# pylint: disable=import-error
import datetime
import time

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

from tests_driver_trackstory.driver_trackstory_unit import fbs_convertation

RAW_TRACKS_CHANNEL = 'channel:yagr:position'


def _pos_are_eq(hist_pos, hist_pos_timestamp, resp_pos):
    return (
        (hist_pos['position'][0], hist_pos['position'][1])
        == (resp_pos['lon'], resp_pos['lat'])
        and resp_pos['timestamp'] == hist_pos_timestamp
        and resp_pos['direction'] == hist_pos['direction']
        and resp_pos['accuracy'] == hist_pos['accuracy']
        and resp_pos['speed'] == hist_pos['speed']
    )


def _generate_driver_one_message(driver_id, now):
    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55.0, 37.0],
            'direction': 45,
            'timestamp': timestamp,
            'speed': 12.5,
            'accuracy': 1,
            'source': 'Gps',
        },
    ]
    return drivers


def _serialize_driver_messages_for_redis(drivers, now):
    return geobus.serialize_positions_v2(drivers, now)


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


@pytest.mark.now('2019-03-09T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 150, 'max_points_count': 20},
        },
        'extended': {
            'enabled': True,
            'storage': {
                'max_age_seconds': 150,
                'max_points_count': 30,
                'max_alternatives_count': 15,
            },
        },
    },
)
async def test_found_driver(
        taxi_driver_trackstory, redis_store, now, taxi_config,
):
    prefix = 'raw_ext_'
    drivers_ids = [prefix + 'aadbid_uuid_0', prefix + 'bbdbid_uuid_1']

    for driver_id in drivers_ids:
        timestamp = now - datetime.timedelta(seconds=30)
        history_length = 40
        history_length = 10
        positions_interval_sec = 5
        now_time = None
        messages = []

        for i in range(0, history_length):
            now_time = timestamp + datetime.timedelta(
                seconds=positions_interval_sec * i,
            )
            message = _generate_driver_one_message(driver_id, now_time)
            messages += message

            message_pack = message
            await _send_and_wait_message_received(
                taxi_driver_trackstory,
                redis_store,
                driver_id,
                'raw',
                message_pack[-1]['timestamp'],
                max_tries=30,
                retry_channel=RAW_TRACKS_CHANNEL,
                retry_message=_serialize_driver_messages_for_redis(
                    message_pack, now_time,
                ),
            )

        raw_num_pos_cnt = 9
        response = await taxi_driver_trackstory.post(
            'shorttracks_extended',
            json={
                'driver_ids': drivers_ids,
                'raw_num_positions': raw_num_pos_cnt,
            },
        )
        assert response.status_code == 200
        data = response.json()

        driver_data = data[driver_id]

        # check that [-1] position is the most recent,
        # and [0] position is the most oldest"""
        most_recent_time = now_time
        oldest_time = now_time - datetime.timedelta(
            seconds=positions_interval_sec * (raw_num_pos_cnt - 1),
        )

        assert not driver_data['adjusted']
        assert not driver_data['alternatives']

        assert driver_data['raw'][0]['timestamp'] == int(
            utils.timestamp(oldest_time),
        )
        assert driver_data['raw'][-1]['timestamp'] == int(
            utils.timestamp(most_recent_time),
        )

        # check that smth_num_position is working
        assert len(driver_data['raw']) == raw_num_pos_cnt

        last_messages = messages[-raw_num_pos_cnt:]
        for i in range(raw_num_pos_cnt):
            driver_history_point = last_messages[i]
            assert _pos_are_eq(
                driver_history_point,
                driver_history_point['timestamp'],
                driver_data['raw'][i],
            )


@pytest.mark.now('2019-03-09T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 150, 'max_points_count': 20},
        },
        'extended': {
            'enabled': True,
            'storage': {
                'max_age_seconds': 150,
                'max_points_count': 30,
                'max_alternatives_count': 15,
            },
        },
    },
)
async def test_found_driver_fbs(
        taxi_driver_trackstory, redis_store, now, taxi_config,
):
    prefix = 'raw_ext_fbs_'
    drivers_ids = [prefix + 'aadbid_uuid_0', prefix + 'bbdbid_uuid_1']

    for driver_id in drivers_ids:
        timestamp = now - datetime.timedelta(seconds=30)
        history_length = 40
        history_length = 10
        positions_interval_sec = 5
        now_time = None
        messages = []

        for i in range(0, history_length):
            now_time = timestamp + datetime.timedelta(
                seconds=positions_interval_sec * i,
            )
            message = _generate_driver_one_message(driver_id, now_time)
            messages += message

            message_pack = message
            await _send_and_wait_message_received(
                taxi_driver_trackstory,
                redis_store,
                driver_id,
                'raw',
                message_pack[-1]['timestamp'],
                max_tries=30,
                retry_channel=RAW_TRACKS_CHANNEL,
                retry_message=_serialize_driver_messages_for_redis(
                    message_pack, now_time,
                ),
            )

        raw_num_pos_cnt = 9
        response = await taxi_driver_trackstory.post(
            'v2/shorttracks_extended',
            json={
                'driver_ids': drivers_ids,
                'raw_num_positions': raw_num_pos_cnt,
            },
        )

        assert response.status_code == 200

        drivers_data = fbs_convertation.convert_fbs_to_local_repr(
            response.content,
        )
        driver_data = drivers_data[driver_id]

        # check that [-1] position is the most recent,
        # and [0] position is the most oldest"""
        most_recent_time = now_time
        oldest_time = now_time - datetime.timedelta(
            seconds=positions_interval_sec * (raw_num_pos_cnt - 1),
        )

        assert not driver_data['adjusted']
        assert not driver_data['alternatives']

        assert driver_data['raw'][0]['timestamp'] == int(
            utils.timestamp(oldest_time),
        )
        assert driver_data['raw'][-1]['timestamp'] == int(
            utils.timestamp(most_recent_time),
        )

        # check that smth_num_position is working
        assert len(driver_data['raw']) == raw_num_pos_cnt

        last_messages = messages[-raw_num_pos_cnt:]
        for i in range(raw_num_pos_cnt):
            driver_history_point = last_messages[i]
            assert _pos_are_eq(
                driver_history_point,
                driver_history_point['timestamp'],
                driver_data['raw'][i],
            )


_RAW_LIMITER_MAX_POINTS_COUNT = 23


@pytest.mark.now('2019-03-09T00:00:00Z')
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {
                'max_age_seconds': 150,
                'max_points_count': _RAW_LIMITER_MAX_POINTS_COUNT,
            },
        },
        'extended': {
            'enabled': True,
            'storage': {
                'max_age_seconds': 150,
                'max_points_count': 30,
                'max_alternatives_count': 15,
            },
        },
    },
)
async def test_limiters(taxi_driver_trackstory, redis_store, now, taxi_config):
    prefix = 'raw_ext_limiters_'
    drivers_ids = [prefix + 'addbid_uuid_0', prefix + 'bbdbid_uuid_1']

    for driver_id in drivers_ids:
        timestamp = now - datetime.timedelta(seconds=30)
        history_length = 50
        positions_interval_sec = 1
        now_time = None
        messages = []

        for i in range(0, history_length):
            now_time = timestamp + datetime.timedelta(
                seconds=positions_interval_sec * i,
            )
            message = _generate_driver_one_message(driver_id, now_time)
            messages += message
            message_pack = message

            await _send_and_wait_message_received(
                taxi_driver_trackstory,
                redis_store,
                driver_id,
                'raw',
                message_pack[-1]['timestamp'],
                max_tries=30,
                retry_channel=RAW_TRACKS_CHANNEL,
                retry_message=_serialize_driver_messages_for_redis(
                    message_pack, now_time,
                ),
            )

        # try to overcome config values
        # ensuring stripping
        check_values = [
            i
            for i in range(1, _RAW_LIMITER_MAX_POINTS_COUNT * 3)
            if i % 7 == 0
        ]
        for value in check_values:
            response = await taxi_driver_trackstory.post(
                'shorttracks_extended',
                json={'driver_ids': drivers_ids, 'raw_num_positions': value},
            )

            assert response.status_code == 200
            data = response.json()

            driver_data = data[driver_id]
            should_be = min(value, _RAW_LIMITER_MAX_POINTS_COUNT)

            assert len(driver_data['raw']) == should_be
