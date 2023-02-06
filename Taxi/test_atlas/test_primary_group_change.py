# pylint: disable=import-error

import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521

PERFORMER_FROM_PUBSUB_NAME = 'performer-from-pubsub-received'
CHANNEL_NAME = 'channel:yagr:signal_v2'


async def _publish_message(
        message,
        taxi_coord_control,
        redis_store,
        performer_from_pubsub_received,
):
    fbs_message = geobus.serialize_signal_v2(message, datetime.datetime.now())
    redis_store.publish(CHANNEL_NAME, fbs_message)
    assert (await performer_from_pubsub_received.wait_call())[
        'data'
    ] == message[0]['driver_id']

    await taxi_coord_control.tests_control(invalidate_caches=False)


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_primary_group_change(
        taxi_coord_control, redis_store, load_json, testpoint, mocked_time,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages.json')

    mocked_time.set(datetime.datetime(2020, 4, 21, 12, 16, 50))
    await taxi_coord_control.tests_control(invalidate_caches=False)
    await _publish_message(
        messages[:4],
        taxi_coord_control,
        redis_store,
        performer_from_pubsub_received,
    )
    mocked_time.set(datetime.datetime(2020, 4, 21, 12, 16, 55))
    await taxi_coord_control.tests_control(invalidate_caches=False)

    await _publish_message(
        messages[4:],
        taxi_coord_control,
        redis_store,
        performer_from_pubsub_received,
    )
    response = await taxi_coord_control.post(
        '/atlas/primary_group_change', json={'dbid_uuid': 'dead_b0d4'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'realtime': [
            {
                'primary_group': ['android_gps'],
                'start_timestamp': '2020-04-21T12:16:50+00:00',
            },
            {
                'primary_group': ['yandex_lbs_gsm'],
                'start_timestamp': '2020-04-21T12:16:55+00:00',
            },
        ],
        'verified': [
            {
                'primary_group': ['android_gps'],
                'start_timestamp': '2020-04-21T12:16:50+00:00',
            },
            {
                'primary_group': ['yandex_lbs_gsm'],
                'start_timestamp': '2020-04-21T12:16:55+00:00',
            },
        ],
    }
