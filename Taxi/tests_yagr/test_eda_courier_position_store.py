import pytest


YAGR_OUTPUT_CHANNEL = 'channel:eda:courier_position_v2'


@pytest.mark.config(YAGR_ENABLE_EDA_COURIER_POSITIONS_PUBLISH=True)
async def test_eda_courier_position_store(taxi_yagr_adv, redis_store):
    redis_listener = redis_store.pubsub()
    _subscribe(redis_listener, YAGR_OUTPUT_CHANNEL)
    _read_all(redis_listener)

    headers = {
        'X-YaEda-CourierId': 'Courier1',
        'Content-Type': 'application/json; charset=UTF-8',
    }
    body = {
        'coordinates': [
            {
                'date': '2004-02-12T15:19:21+03:00',
                'location': {'latitude': 55.740404, 'longitude': 37.513276},
            },
            {
                'date': '2004-02-12T15:19:21+03:00',
                'location': {
                    'latitude': 55.740404,
                    'longitude': 37.513276,
                    'fakeGPS': True,
                },
            },
        ],
    }
    response = await taxi_yagr_adv.post(
        '/eda/courier/positions/store', json=body, headers=headers,
    )
    assert response.status_code == 200

    redis_message = _get_message(redis_listener, redis_store)
    assert redis_message is not None


def _subscribe(listener, channel, try_count=30):
    for _ in range(try_count):
        listener.subscribe(channel)
        message = listener.get_message(timeout=0.2)
        if message is not None and message['type'] == 'subscribe':
            return
    # failed to subscribe
    assert False


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
