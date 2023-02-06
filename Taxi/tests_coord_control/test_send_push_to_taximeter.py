# pylint: disable=import-error

import datetime
import json

import dateutil.parser
import pytest

from geobus_tools import geobus  # noqa: F401 C5521

STRATEGY_CALCULATED_NAME = 'strategy-calculated'
CHANNEL_NAME = 'channel:yagr:signal_v2'


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_send_push_to_taximeter(
        taxi_coord_control,
        redis_store,
        load_json,
        testpoint,
        mockserver,
        mocked_time,
):
    is_push_sended = False
    drop_bad_track_reason = {}

    @mockserver.json_handler('/client-notify/v2/push')
    def _v2_push(request):
        assert request.json['service'] == 'taximeter'
        assert request.json['intent'] == 'DropBadTrack'
        assert request.json['client_id'] == 'dbid-uuid'
        nonlocal drop_bad_track_reason
        drop_bad_track_reason = request.json['data']
        nonlocal is_push_sended
        is_push_sended = True

        return mockserver.make_response(
            json.dumps({'notification_id': '1488'}), status=200,
        )

    @testpoint(STRATEGY_CALCULATED_NAME)
    def strategy_calculated(data):
        return data

    @testpoint('consistent-hashing-finished')
    def consistent_hashing_finished(data):
        pass

    now = dateutil.parser.parse('2020-04-21T12:17:42+00:00')
    mocked_time.set(now)
    await taxi_coord_control.tests_control()
    await consistent_hashing_finished.wait_call()

    messages = load_json('geobus_one_driver_messages.json')
    fbs_message = geobus.serialize_signal_v2(messages, datetime.datetime.now())
    redis_store.publish(CHANNEL_NAME, fbs_message)

    assert (await strategy_calculated.wait_call())['data'][
        'performer_id'
    ] == 'dbid_uuid'
    assert is_push_sended
    assert drop_bad_track_reason.get('reason') == 'ignore_primary_group'

    is_push_sended = False
    now += datetime.timedelta(hours=0, minutes=3)
    mocked_time.set(now)
    await taxi_coord_control.tests_control()

    redis_store.publish(CHANNEL_NAME, fbs_message)
    await strategy_calculated.wait_call()
    assert not is_push_sended

    await taxi_coord_control.tests_control()

    # source: android_passive; route length: 10.6521
    messages[0]['position'][0] += 3e-4
    fbs_message = geobus.serialize_signal_v2(messages, datetime.datetime.now())
    redis_store.publish(CHANNEL_NAME, fbs_message)
    await strategy_calculated.wait_call()
    assert is_push_sended
    assert drop_bad_track_reason.get('reason') == 'long_jump'
