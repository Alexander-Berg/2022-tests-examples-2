# pylint: disable=import-error,too-many-lines

import urllib.parse

import pytest

from geobus_tools import geobus  # noqa: F401
from geobus_tools.channels import universal_signals


YAGR_OUTPUT_V2_CHANNEL = 'channel:yagr:position'
YAGR_OUTPUT_UNIVERSAL_CHANNEL = 'channel:yagr:universal_position'


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(YAGR_ENABLE_POSITIONS_V2_CHANNEL=True)
@pytest.mark.config(YAGR_ENABLE_UNIVERSAL_POSITIONS_PUBLISH=True)
@pytest.mark.config(YAGR_PUBLISH_PERIOD=50)
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 30,
        'past_boundary': 30,
    },
)
@pytest.mark.parametrize(
    'headers,app_family',
    [
        ({'User-Agent': 'Taximeter 9.1 (1234)'}, 'taximeter'),
        ({'User-Agent': 'Taximeter-Uber 9.1 (1234)'}, 'uberdriver'),
    ],
)
async def test_positions_v2_channel(
        taxi_yagr_adv,
        driver_authorizer,
        redis_store,
        testpoint,
        headers,
        app_family,
        geobus_redis_getter,
):
    @testpoint('publish[{}]'.format(YAGR_OUTPUT_V2_CHANNEL))
    def on_publish(data):
        pass

    position_listener = await geobus_redis_getter.get_listener(
        YAGR_OUTPUT_V2_CHANNEL,
    )

    universal_position_listener = await geobus_redis_getter.get_listener(
        YAGR_OUTPUT_UNIVERSAL_CHANNEL,
    )

    driver_authorizer.set_client_session(
        app_family, 'zxcvb2', 'asdfg', 'qwerty',
    )
    params = {'session': 'asdfg', 'db': 'zxcvb2'}
    data_args = {
        'driverId': 'qwerty',
        'lat': 55.740404,
        'lon': 37.513276,
        'angel': 238.4,
        'speed': 58,
        'isBad': 'false',
        'status': 1,
        'orderStatus': 0,
        'accuracy': 2.0,
        'timeGpsOrig': 1568388595484,
        'timeSystemOrig': 1568388595484,
        'timeSystemSync': 1568388595484,
    }
    data = urllib.parse.urlencode(data_args)
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=data, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {}

    await on_publish.wait_call(2)

    # check after all processing is done
    redis_message = position_listener.get_message()
    assert redis_message is not None
    print(redis_message)

    # check after all processing is done
    redis_message_universal = universal_position_listener.get_message()
    assert redis_message_universal is not None
    print(redis_message_universal)

    # 58 km/h -> 16.stmh m/s
    geobus_res = geobus.deserialize_positions_v2(redis_message['data'])
    print(geobus_res)
    assert is_close(geobus_res['positions'][0]['speed'], 58 * 1000 / 3600)

    universal_result = universal_signals.deserialize_message(
        redis_message_universal['data'],
    )
    assert is_close(
        universal_result['payload'][0]['signals'][0]['geo_position']['speed'],
        58 * 1000 / 3600,
    )


def _subscribe(listener, channel, try_count=30):
    for _ in range(try_count):
        listener.subscribe(channel)
        message = listener.get_message(timeout=0.2)
        if message is not None and message['type'] == 'subscribe':
            return
    # failed to subscribe
    assert False


def is_close(first, second, allowed_absolute_error=0.0001):
    return abs(first - second) < allowed_absolute_error


def _get_message(
        listener,
        redis_store,
        retry_channel=None,
        max_tries=30,
        retry_message=None,
):
    # wait while yaga-dispatcher pass messages to output channel
    for _ in range(max_tries):
        message = listener.get_message(timeout=0.2)
        if message is not None and message['type'] == 'message':
            return message
        if retry_channel is not None and retry_message is not None:
            redis_store.publish(retry_channel, retry_message)
    return None


def _read_all(listener):
    # Get all messages from channel
    for _ in range(3):
        while listener.get_message(timeout=0.2) is not None:
            print('**********')
