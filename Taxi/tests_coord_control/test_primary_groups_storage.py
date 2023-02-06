# pylint: disable=import-error

import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521

PERFORMER_FROM_PUBSUB_NAME = 'performer-from-pubsub-received'
CHANNEL_NAME = 'channel:yagr:signal_v2'
CHECK_VERIFIED_PRIMARY_GROUP = 'check-verified-primary-group'


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
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
async def test_primary_groups_storage(
        taxi_coord_control, redis_store, load_json, testpoint,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    @testpoint(CHECK_VERIFIED_PRIMARY_GROUP)
    def check_verified_primary_group(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages.json')

    await _publish_message(
        messages[:4],
        taxi_coord_control,
        redis_store,
        performer_from_pubsub_received,
    )
    assert (await check_verified_primary_group.wait_call())['data'] == [
        ['android_gps'],
    ]

    await _publish_message(
        messages[4:],
        taxi_coord_control,
        redis_store,
        performer_from_pubsub_received,
    )
    assert (await check_verified_primary_group.wait_call())['data'] == [
        ['android_gps'],
        ['yandex_lbs_gsm'],
    ]
