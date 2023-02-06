# pylint: disable=import-error

import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521


PERFORMER_FROM_PUBSUB_NAME = 'performer-from-pubsub-received'
MESSAGE_HANDLED = 'message-handled'
GIVEN_STRATEGY_STATS = 'given-strategy-stats'
PERFORMERS_TO_CALCULATE_NAME = 'performers-to-calculate'

ETAG = 'COORD_CONTROL_ETAG_636355968000000000'
NEW_ETAG = 'COORD_CONTROL_ETAG_636355968000000289'


def check_response(settings, response):
    sample = settings['test_location_settings']
    assert sample['location_settings'] == response['location_settings']
    assert (
        sample['location_settings_etag'] == response['location_settings_etag']
    )


def dt_from_ts(ts_ms: int) -> datetime.datetime:
    timestamp = int(str(ts_ms)[:-3])
    return datetime.datetime.utcfromtimestamp(timestamp)


async def _publish_message(message, redis_store, message_handled):
    fbs_message = geobus.serialize_signal_v2(message, datetime.datetime.now())
    redis_store.publish('channel:yagr:signal_v2', fbs_message)

    assert await message_handled.wait_call()


async def test_location_settings(taxi_coord_control, load_json, testpoint):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    test_settings = load_json('test_location_settings_response.json')
    test_handler_response = await taxi_coord_control.post(
        'test_coord_control', json=test_settings,
    )
    assert test_handler_response.status_code == 200
    await performer_from_pubsub_received.wait_call()

    # stored taximeter_version == requested taximeter_version
    # stored etag != requested etag
    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': 'test_driver_id',
            'park_db_id': 'dbid',
            'taximeter_agent_info': 'Taximeter-BETA 9.33',
        },
        headers={'location_settings_etag': 'unknown'},
    )
    assert response.status_code == 200
    assert (
        response.headers['Content-Type'] == 'application/json; charset=utf-8'
    )
    check_response(test_settings, response.json())

    # stored taximeter_version != requested taximeter_version
    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': 'test_driver_id',
            'park_db_id': 'dbid',
            'taximeter_agent_info': 'Taximeter-BETA 9.48 (1234)',
        },
        headers={'location_settings_etag': 'unknown'},
    )
    assert response.status_code == 404
    assert (
        response.headers['Content-Type'] == 'application/json; charset=utf-8'
    )

    await performer_from_pubsub_received.wait_call()

    # stored taximeter_version == requested taximeter_version
    # stored etag == requested etag
    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': 'test_driver_id',
            'park_db_id': 'dbid',
            'taximeter_agent_info': 'Taximeter-BETA 9.48 (1234)',
        },
        headers={'location_settings_etag': ETAG},
    )
    assert response.status_code == 200
    assert response.json() == {'location_settings_etag': ETAG}

    # request for nonexistent driver_profile_id and etag
    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': 'new_driver_id',
            'park_db_id': 'dbid',
            'taximeter_agent_info': 'Taximeter-BETA 9.33',
        },
        headers={'location_settings_etag': NEW_ETAG},
    )
    assert response.status_code == 404

    # add new driver_profile_id and etag to redis
    new_test_settings = load_json('test_location_settings_new_response.json')
    test_handler_response = await taxi_coord_control.post(
        'test_coord_control', json=new_test_settings,
    )
    assert test_handler_response.status_code == 200
    await performer_from_pubsub_received.wait_call()

    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': 'new_driver_id',
            'park_db_id': 'dbid',
            'taximeter_agent_info': 'Taximeter-BETA 9.33',
        },
        headers={'location_settings_etag': NEW_ETAG},
    )
    assert response.status_code == 200
    assert response.json() == {'location_settings_etag': NEW_ETAG}


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.suspend_periodic_tasks('bad_areas_detector', 'Cleaner')
@pytest.mark.parametrize(
    'test_case_idx,expected_primary_source',
    [(0, 'none'), (1, 'yandex_lbs_gsm')],
)
async def test_strategy_stats_on_handle(
        taxi_coord_control,
        redis_store,
        load_json,
        testpoint,
        mocked_time,
        statistics,
        test_case_idx,
        expected_primary_source,
):
    # Reset service state
    await taxi_coord_control.invalidate_caches()

    @testpoint(MESSAGE_HANDLED)
    def message_handled(data):
        return data

    @testpoint(GIVEN_STRATEGY_STATS)
    def given_strategy_stats(data):
        return data

    await taxi_coord_control.enable_testpoints()

    async with statistics.capture(taxi_coord_control) as capture:
        signals = load_json(f'signals_{test_case_idx}.json')
        signals = sorted(signals, key=lambda s: s['unix_time'])
        start = 0
        while start < len(signals):
            now = dt_from_ts(signals[start]['unix_time'])
            now += datetime.timedelta(seconds=1)
            mocked_time.set(now)
            await taxi_coord_control.tests_control(invalidate_caches=False)

            end = start + 1
            while (
                    end < len(signals)
                    and dt_from_ts(signals[end]['unix_time']) < now
            ):
                end += 1

            await _publish_message(
                signals[start:end], redis_store, message_handled,
            )
            await taxi_coord_control.run_periodic_task('bad_areas_detector')
            await taxi_coord_control.run_periodic_task('Cleaner')
            start = end

        # first time no answer -- saved metainfo
        response = await taxi_coord_control.get(
            'location_settings',
            params={
                'driver_profile_id': 'b0d4',
                'park_db_id': 'dead',
                'taximeter_agent_info': 'Taximeter-BETA 9.33',
            },
            headers={'location_settings_etag': '2195045530425317625'},
        )
        assert response.json() == {
            'code': 'not_found',
            'message': 'saved_metainfo',
        }
        # Now use another etag to trigger a response
        response = await taxi_coord_control.get(
            'location_settings',
            params={
                'driver_profile_id': 'b0d4',
                'park_db_id': 'dead',
                'taximeter_agent_info': 'Taximeter-BETA 9.33',
            },
            headers={'location_settings_etag': ''},
        )
        location_settings = response.json()['location_settings']
        expected_primary_groups = (
            [expected_primary_source]
            if expected_primary_source != 'none'
            else []
        )
        assert (
            location_settings['realtime_strategy']['primaryGroup']
            == expected_primary_groups
        )
        assert (
            location_settings['verified_strategy']['primaryGroup']
            == expected_primary_groups
        )
        assert (await given_strategy_stats.wait_call())['data'] == {
            'primary_source': expected_primary_source,
        }
    for strategy_name in ['verified', 'realtime']:
        key = f'coord-control.moscow_metric_zone.{strategy_name}.'
        if expected_primary_groups:
            key += 'non_empty_strategies_given'
        else:
            key += 'empty_strategies_given'
        assert capture.statistics[key] == 1


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.suspend_periodic_tasks('bad_areas_detector', 'Cleaner')
async def test_fallback(
        taxi_coord_control,
        redis_store,
        load_json,
        testpoint,
        mocked_time,
        statistics,
):
    statistics.fallbacks = [
        'coord-control.fallback_empty_strategies_given.moscow_metric_zone.verified',  # noqa: E501
    ]
    # Reset service state
    await taxi_coord_control.invalidate_caches()

    performers_proceeded = []

    # pylint: disable=unused-variable
    @testpoint(PERFORMERS_TO_CALCULATE_NAME)
    def performers_to_calculate(data):
        nonlocal performers_proceeded
        performers_proceeded += data

    @testpoint(MESSAGE_HANDLED)
    def message_handled(data):
        return data

    await taxi_coord_control.enable_testpoints()

    signals = load_json(f'signals_0.json')
    signals = sorted(signals, key=lambda s: s['unix_time'])
    start = 0
    while start < len(signals):
        now = dt_from_ts(signals[start]['unix_time'])
        now += datetime.timedelta(seconds=1)
        mocked_time.set(now)
        await taxi_coord_control.tests_control(invalidate_caches=False)

        end = start + 1
        while (
                end < len(signals)
                and dt_from_ts(signals[end]['unix_time']) < now
        ):
            end += 1

        await _publish_message(
            signals[start:end], redis_store, message_handled,
        )
        await taxi_coord_control.run_periodic_task('bad_areas_detector')
        await taxi_coord_control.run_periodic_task('Cleaner')
        start = end
    # OK not to wait, message_handled happens after
    assert performers_proceeded == []


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
async def test_location_settings_metrics(
        taxi_coord_control,
        taxi_coord_control_monitor,
        load_json,
        testpoint,
        mocked_time,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    now = mocked_time.now()
    test_settings = load_json('test_location_settings_response.json')
    test_handler_response = await taxi_coord_control.post(
        'test_coord_control', json=test_settings,
    )
    assert test_handler_response.status_code == 200
    await performer_from_pubsub_received.wait_call()

    # stored taximeter_version == requested taximeter_version
    # stored etag != requested etag
    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': 'test_driver_id',
            'park_db_id': 'dbid',
            'taximeter_agent_info': 'Taximeter-BETA 9.33',
        },
        headers={'location_settings_etag': 'unknown'},
    )
    assert response.status_code == 200

    mocked_time.set(now + datetime.timedelta(seconds=6))
    await taxi_coord_control.tests_control(invalidate_caches=False)

    metrics = await taxi_coord_control_monitor.get_metric(
        'coord_control_metrics',
    )
    for strategy_name in ['verified', 'realtime']:
        assert (
            metrics['given_primary']['undefined']['none'][strategy_name] == 1
        )
        assert (
            metrics['given_different_primary']['undefined'][strategy_name] == 1
        )
