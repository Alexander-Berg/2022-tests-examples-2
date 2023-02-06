# pylint: disable=import-error
import asyncio  # noqa: F401 C5521

from geobus_tools import geobus  # noqa: F401 C5521
from geobus_tools.channels import universal_signals
import pytest


class YagaNextDriverId:
    yaga_next_driver_id = 1

    @staticmethod
    def get_next_id():
        YagaNextDriverId.yaga_next_driver_id += 1
        return YagaNextDriverId.yaga_next_driver_id - 1


# @pytest.mark.skip(reason='fix after moving to geopipelines')
@pytest.mark.asyncio
async def test_driver_position_reader(taxi_yaga_simple, redis_store, now):
    track = _make_track()
    universal_message = _make_universal_message_from_track(track)

    # publish to yaga-dispatcher input channel
    input_universal_message = universal_signals.serialize_message(
        universal_message, now,
    )
    taxi_yaga_simple.send_message(input_universal_message)

    # test edge positions channel
    message = taxi_yaga_simple.get_adjust_message()
    # Failed to get message in max_tries tries
    assert message is not None
    assert message['data']
    await _check_service_is_alive(taxi_yaga_simple)


# async def test_camera_position_reader(taxi_yaga, redis_store, now):
#     # create subscriber
#     edge_positions_listener = redis_store.pubsub()
#     _subscribe(edge_positions_listener, YAGA_CAMERA_OUTPUT_CHANNEL)
#     await _read_all(edge_positions_listener)

#     track = _make_track()
#     message_data = _make_message_from_track(track)

#     # publish to yaga-dispatcher input channel
#     input_message = geobus.serialize_positions_v2(message_data, now)
#     redis_store.publish(YAGA_CAMERA_INPUT_CHANNEL, input_message)

#     # test edge positions channel
#     message = _get_message(
#         edge_positions_listener,
#         redis_store,
#         retry_channel=YAGA_CAMERA_INPUT_CHANNEL,
#         retry_message=input_message,
#     )
#     # Failed to get message in max_tries tries
#     assert message is not None
#     assert message['data']
#     await _check_service_is_alive(taxi_yaga)


@pytest.mark.asyncio
@pytest.mark.experiments3(filename='yaga_adjust_type.json')
async def test_driver_predicted_position_reader(taxi_yaga_simple, now):
    track = _make_track()
    universal_message = _make_universal_message_from_track(track)

    # publish to yaga-dispatcher input channel
    input_universal_message = universal_signals.serialize_message(
        universal_message, now,
    )
    taxi_yaga_simple.send_message(input_universal_message)

    message = taxi_yaga_simple.get_predicted_message()
    # Successfully read message
    assert message is not None
    assert message['data']
    await _check_service_is_alive(taxi_yaga_simple)


@pytest.mark.experiments3(filename='yaga_adjust_type.json')
@pytest.mark.asyncio
async def test_driver_predicted_position_with_bbox_reader(
        taxi_yaga_simple, now,
):
    track = _make_track()
    universal_message = _make_universal_message_from_track(track)

    # publish to yaga-dispatcher input channel
    input_universal_message = universal_signals.serialize_message(
        universal_message, now,
    )
    taxi_yaga_simple.send_message(input_universal_message)

    # test predicted edge positions channel
    message = taxi_yaga_simple.get_predicted_message()

    # Successfully read message
    assert message is not None
    assert message['data']
    await _check_service_is_alive(taxi_yaga_simple)


@pytest.mark.experiments3(filename='yaga_adjust_type.json')
@pytest.mark.asyncio
async def test_driver_predicted_position_disabled_reader(
        taxi_yaga_simple, now,
):
    track = _make_track()
    universal_message = _make_universal_message_from_track(track)

    # publish to yaga-dispatcher input channel
    input_universal_message = universal_signals.serialize_message(
        universal_message, now,
    )
    taxi_yaga_simple.send_message(input_universal_message)

    # test predicted edge positions channel
    message = taxi_yaga_simple.get_predicted_message()
    # should receive adjusted positions instead of predicted
    assert message is not None
    assert message['data']
    await _check_service_is_alive(taxi_yaga_simple)


@pytest.mark.asyncio
async def test_position_reader_garbage_message(taxi_yaga_simple):
    # Clean channel
    await taxi_yaga_simple.clear_adjusted_channel()

    # create garbage message
    input_message = b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'

    taxi_yaga_simple.send_message(input_message)

    message = taxi_yaga_simple.get_adjust_message()
    # Must fail to get message in max_tries tries
    assert message is None
    await _check_service_is_alive(taxi_yaga_simple)


async def _check_service_is_alive(taxi_yaga):
    response = await taxi_yaga.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''


def _make_track():
    track = [
        {
            'speed': 16.6,
            'lon': 37.698035,
            'lat': 55.721591,
            'timestamp': 1514764800,
        },
        {
            'speed': 16.6,
            'lon': 37.699561,
            'timestamp': 1514764807,
            'lat': 55.720928,
        },
        {
            'lon': 37.69938,
            'speed': 16.6,
            'lat': 55.720603,
            'timestamp': 1514764809,
        },
        {
            'lon': 37.69782,
            'speed': 16.6,
            'lat': 55.720206,
            'timestamp': 1514764815,
        },
        {
            'lon': 37.695893,
            'speed': 16.6,
            'timestamp': 1514764823,
            'lat': 55.719651,
        },
        {
            'speed': 16.6,
            'lon': 37.694498,
            'timestamp': 1514764828,
            'lat': 55.71923,
        },
        {
            'lat': 55.718765,
            'timestamp': 1514764831,
            'speed': 16.6,
            'lon': 37.694135,
        },
        {
            'speed': 16.6,
            'lon': 37.694035,
            'lat': 55.718316,
            'timestamp': 1514764834,
        },
        {
            'speed': 16.6,
            'lon': 37.692801,
            'timestamp': 1514764839,
            'lat': 55.717985,
        },
        {
            'speed': 16.6,
            'lon': 37.690895,
            'lat': 55.71754,
            'timestamp': 1514764846,
        },
    ]
    return [(x['timestamp'], [x['lon'], x['lat']]) for x in track]


def _make_message_from_track(track):
    yaga_next_driver_id = YagaNextDriverId()
    driver_id = 'dbid_uuid{}'.format(yaga_next_driver_id.get_next_id())
    return [
        {
            'driver_id': driver_id,
            'direction': 0,
            'speed': int(16.6 * 3.6),
            'accuracy': 0,
            'timestamp': timestamp,
            'position': position,
            'source': 'Gps',
        }
        for timestamp, position in track
    ]


def _make_universal_message_from_track(track):
    yaga_next_driver_id = YagaNextDriverId()
    driver_id = 'dbid_uuid{}'.format(yaga_next_driver_id.get_next_id())
    message = {'payload': []}
    message['payload'] = [
        {
            'contractor_id': driver_id,
            'client_timestamp': timestamp,
            'source': 'Verified',
            'signals': [{'geo_position': {'position': position}}],
        }
        for timestamp, position in track
    ]
    return message
