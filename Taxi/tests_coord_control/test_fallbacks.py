# pylint: disable=import-error
import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521

STRATEGY_CALCULATED_NAME = 'strategy-calculated'
CHANNEL_NAME = 'channel:yagr:signal_v2'
PERFORMERS_TO_CALCULATE_NAME = 'performers-to-calculate'


def _sample_message_with_unix_time(unix_time, messages):
    for item in messages:
        item['unix_time'] = unix_time
    return messages


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:17:50.123456+0000')
async def test_fallback_bad_source(
        taxi_coord_control, redis_store, load_json, testpoint, statistics,
):
    @testpoint(STRATEGY_CALCULATED_NAME)
    def strategy_calculated(data):
        return data

    messages = load_json('geobus_messages.json')
    driver_id = messages[0]['driver_id']

    async with statistics.capture(taxi_coord_control) as capture:
        fbs_message = geobus.serialize_signal_v2(
            messages[0:3], datetime.datetime.now(),
        )
        redis_store.publish(CHANNEL_NAME, fbs_message)

        assert (await strategy_calculated.wait_call())['data'][
            'performer_id'
        ] == driver_id

    assert (
        capture.statistics[
            'coord-control.fallback_by_bad_source.undefined.realtime.error'
        ]
        == 1
    )
    assert (
        capture.statistics.get(
            'coord-control.fallback_by_bad_source.undefined.realtime.success',
            0,
        )
        == 0
    )

    async with statistics.capture(taxi_coord_control) as capture:
        fbs_message = geobus.serialize_signal_v2(
            messages[3:6], datetime.datetime.now(),
        )
        redis_store.publish(CHANNEL_NAME, fbs_message)

        performer_id = (await strategy_calculated.wait_call())['data'][
            'performer_id'
        ]
        assert performer_id == driver_id

    assert (
        capture.statistics[
            'coord-control.fallback_by_bad_source.undefined.realtime.success'
        ]
        == 1
    )
    assert (
        capture.statistics.get(
            'coord-control.fallback_by_bad_source.undefined.realtime.error', 0,
        )
        == 0
    )


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3_fallback.json')
async def test_fallback_by_zone(
        taxi_coord_control, redis_store, load_json, testpoint, mocked_time,
):
    @testpoint(PERFORMERS_TO_CALCULATE_NAME)
    def performers_to_calculate(data):
        return data

    mocked_time.set(datetime.datetime.now())
    messages = load_json('geobus_messages_by_zone.json')
    unix_times = [1587471462786, 1587471492786, 1587471522786, 1587471524786]
    driver_id = messages[0]['driver_id']
    dbid, uuid = driver_id.split('_')

    # fill taximeter_version and agent info
    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': uuid,
            'park_db_id': dbid,
            'taximeter_agent_info': 'Taximeter-BETA 9.33 (1234)',
        },
        headers={'location_settings_etag': 'etag'},
    )

    assert response.status_code == 404
    await taxi_coord_control.invalidate_caches()

    for i in range(3):
        mocked_time.set(
            datetime.datetime.utcnow() + datetime.timedelta(minutes=i),
        )

        fbs_message = geobus.serialize_signal_v2(
            _sample_message_with_unix_time(unix_times[i], messages),
            mocked_time.now() + datetime.timedelta(hours=3),
        )
        # publish to coord-control input channel
        redis_store.publish(CHANNEL_NAME, fbs_message)

        assert (await performers_to_calculate.wait_call())['data']

        await taxi_coord_control.run_periodic_task('calculate_fallback')

    fbs_message = geobus.serialize_signal_v2(
        _sample_message_with_unix_time(unix_times[3], messages),
        mocked_time.now() + datetime.timedelta(hours=3),
    )
    # publish to coord-control input channel
    redis_store.publish(CHANNEL_NAME, fbs_message)
    assert (await performers_to_calculate.wait_call())['data']
