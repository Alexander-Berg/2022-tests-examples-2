# pylint: disable=import-error,no-name-in-module
import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521

PERFORMER_FROM_PUBSUB_NAME = 'performer-from-pubsub-received'
CHANNEL_NAME = 'channel:yagr:signal_v2'


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
async def test_track(taxi_coord_control, redis_store, load_json, testpoint):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    await taxi_coord_control.enable_testpoints()
    messages = load_json('geobus_messages.json')

    fbs_message = geobus.serialize_signal_v2(
        messages[:2], datetime.datetime.now(),
    )
    redis_store.publish(CHANNEL_NAME, fbs_message)
    await performer_from_pubsub_received.wait_call()

    response = await taxi_coord_control.post(
        'atlas/track', json={'dbid_uuid': 'dbid_uuid_0'},
    )

    assert response.status_code == 200
    assert response.json() == load_json('response.json')
