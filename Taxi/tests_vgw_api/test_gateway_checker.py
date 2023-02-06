import asyncio
import datetime

import psycopg2.tz
import pytest

MOSCOW_TZ = psycopg2.tz.FixedOffsetTimezone(offset=180)


@pytest.mark.config(
    VGW_API_CLIENT_TIMEOUT=2000,
    VGW_API_USE_NEW_VGW_ENABLE_SETTINGS=True,
    VGW_API_GATEWAY_CHECKER_SETTINGS={
        'enabled': True,
        'period_ms': 100000,
        'success_period_mins': 30,
        'settings_by_disable_reason': {
            '__default__': {
                'retry_delays_mins': [1, 5, 20, 60, 120],
                'retry_forever': True,
            },
        },
    },
    VGW_API_DISABLING_HISTORY_SETTINGS={
        'db_requests': {
            'read_history': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
            'status_change': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
        },
        'history_enabled': True,
        'history_entries_limit': 100,
    },
)
@pytest.mark.parametrize(
    ['fallbacks', 'expected_gateway_disabled', 'expected_disabled_count'],
    [
        ([], {'id_1': (False, None), 'id_2': (True, None)}, 0),
        (
            [
                'gateway.id_1.handle.redirections.post.fallback',
                'gateway.id_2.handle.redirections.post.fallback',
            ],
            {'id_1': (True, 'too many errors'), 'id_2': (True, None)},
            1,
        ),
        (
            [
                'talks.total.gateway.id_1.fallback',
                'talks.total.gateway.id_2.fallback',
            ],
            {'id_1': (True, 'no talks'), 'id_2': (True, None)},
            1,
        ),
        (
            [
                'talks.fail.gateway.id_1.fallback',
                'talks.fail.gateway.id_2.fallback',
            ],
            {'id_1': (True, 'too many failed talks'), 'id_2': (True, None)},
            1,
        ),
        (
            [
                'talks.short.gateway.id_1.fallback',
                'talks.short.gateway.id_2.fallback',
            ],
            {'id_1': (True, 'too many short talks'), 'id_2': (True, None)},
            1,
        ),
        (
            [
                'gateway.id_1.handle.redirections.post.fallback',
                'talks.total.gateway.id_1.fallback',
                'talks.fail.gateway.id_1.fallback',
                'talks.short.gateway.id_1.fallback',
            ],
            {'id_1': (True, 'too many errors'), 'id_2': (True, None)},
            1,
        ),
    ],
)
@pytest.mark.suspend_periodic_tasks('gateway-checker')
async def test_gateway_statistics_checks(
        taxi_vgw_api,
        testpoint,
        statistics,
        pgsql,
        fallbacks,
        expected_gateway_disabled,
        expected_disabled_count,
):
    @testpoint('gateway-checker/gateway-disabled')
    def gateway_disabled(data):
        pass

    statistics.fallbacks = fallbacks
    await taxi_vgw_api.invalidate_caches()

    # Run task several times
    for _ in range(5):
        await taxi_vgw_api.run_periodic_task('gateway-checker')
    await taxi_vgw_api.invalidate_caches()
    for _ in range(5):
        await taxi_vgw_api.run_periodic_task('gateway-checker')

    assert gateway_disabled.times_called == expected_disabled_count

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT id, (settings).disabled, disable_reason '
        'FROM voice_gateways.voice_gateways',
    )
    gateways = cursor.fetchall()
    cursor.close()
    assert len(gateways) == len(expected_gateway_disabled)
    for gateway_id, disabled, disable_reason in gateways:
        assert disabled == expected_gateway_disabled[gateway_id][0]
        assert disable_reason == expected_gateway_disabled[gateway_id][1]


@pytest.mark.now('2021-09-11T12:00:00+03:00')
@pytest.mark.parametrize(
    ['expected_enable_after', 'expected_relapse_count'],
    [
        pytest.param(
            datetime.datetime(2021, 9, 11, 13, 0, 0, tzinfo=MOSCOW_TZ),
            3,
            id='relapse',
            marks=[
                pytest.mark.pgsql('vgw_api', files=['pg_vgw_api_relapse.sql']),
            ],
        ),
        pytest.param(
            datetime.datetime(2021, 9, 11, 14, 0, 0, tzinfo=MOSCOW_TZ),
            70,
            id='relapse retry forever',
            marks=[
                pytest.mark.pgsql(
                    'vgw_api', files=['pg_vgw_api_relapse_many_retries.sql'],
                ),
            ],
        ),
        pytest.param(
            datetime.datetime(2021, 9, 11, 13, 0, 0, tzinfo=MOSCOW_TZ),
            3,
            id='relapse finite retries',
            marks=[
                pytest.mark.pgsql('vgw_api', files=['pg_vgw_api_relapse.sql']),
                pytest.mark.config(
                    VGW_API_GATEWAY_CHECKER_SETTINGS={
                        'enabled': True,
                        'period_ms': 1000,
                        'success_period_mins': 30,
                        'settings_by_disable_reason': {
                            '__default__': {
                                'retry_delays_mins': [1, 5, 20, 60, 120],
                                'retry_forever': False,
                            },
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            None,
            70,
            id='relapse stop retrying',
            marks=[
                pytest.mark.pgsql(
                    'vgw_api', files=['pg_vgw_api_relapse_many_retries.sql'],
                ),
                pytest.mark.config(
                    VGW_API_GATEWAY_CHECKER_SETTINGS={
                        'enabled': True,
                        'period_ms': 1000,
                        'success_period_mins': 30,
                        'settings_by_disable_reason': {
                            '__default__': {
                                'retry_delays_mins': [1, 5, 20, 60, 120],
                                'retry_forever': False,
                            },
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            datetime.datetime(2021, 9, 11, 12, 1, 0, tzinfo=MOSCOW_TZ),
            0,
            id='new error',
            marks=[
                pytest.mark.pgsql(
                    'vgw_api', files=['pg_vgw_api_new_error.sql'],
                ),
            ],
        ),
        pytest.param(
            datetime.datetime(2021, 9, 11, 12, 1, 0, tzinfo=MOSCOW_TZ),
            0,
            id='no relapse info',
            marks=[
                pytest.mark.pgsql(
                    'vgw_api', files=['pg_vgw_api_no_relapse_info.sql'],
                ),
            ],
        ),
        pytest.param(
            datetime.datetime(2021, 9, 11, 12, 1, 0, tzinfo=MOSCOW_TZ),
            0,
            id='no enabled_at',
            marks=[
                pytest.mark.pgsql(
                    'vgw_api', files=['pg_vgw_api_no_enabled_at.sql'],
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    VGW_API_CLIENT_TIMEOUT=2000,
    VGW_API_USE_NEW_VGW_ENABLE_SETTINGS=True,
    VGW_API_GATEWAY_CHECKER_SETTINGS={
        'enabled': True,
        'period_ms': 100000,
        'success_period_mins': 30,
        'settings_by_disable_reason': {
            '__default__': {'retry_delays_mins': [1], 'retry_forever': False},
            'too many errors': {
                'retry_delays_mins': [1, 5, 20, 60, 120],
                'retry_forever': True,
            },
        },
    },
    VGW_API_DISABLING_HISTORY_SETTINGS={
        'db_requests': {
            'read_history': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
            'status_change': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
        },
        'history_enabled': True,
        'history_entries_limit': 100,
    },
)
@pytest.mark.suspend_periodic_tasks('gateway-checker')
async def test_relapses(
        taxi_vgw_api,
        testpoint,
        statistics,
        pgsql,
        expected_enable_after,
        expected_relapse_count,
):
    @testpoint('gateway-checker/gateway-disabled')
    def gateway_disabled(data):
        pass

    statistics.fallbacks = ['gateway.id_1.handle.redirections.post.fallback']
    await taxi_vgw_api.invalidate_caches()

    # Run task several times
    for _ in range(5):
        await taxi_vgw_api.run_periodic_task('gateway-checker')
    await taxi_vgw_api.invalidate_caches()
    for _ in range(5):
        await taxi_vgw_api.run_periodic_task('gateway-checker')

    assert gateway_disabled.times_called == 1

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT id, (settings).disabled, enable_after, relapse_count '
        'FROM voice_gateways.voice_gateways',
    )
    gateways = cursor.fetchall()
    cursor.close()

    assert len(gateways) == 1
    gateway_id, disabled, enable_after, relapse_count = gateways[0]
    assert gateway_id == 'id_1'
    assert disabled
    assert relapse_count == expected_relapse_count
    assert enable_after == expected_enable_after


@pytest.mark.config(
    VGW_API_CLIENT_TIMEOUT=2000, VGW_API_USE_NEW_VGW_ENABLE_SETTINGS=True,
)
@pytest.mark.suspend_periodic_tasks('gateway-checker')
async def test_gateway_checker_disabled(taxi_vgw_api, testpoint, statistics):
    @testpoint('gateway-checker/gateway-disabled')
    def gateway_disabled(data):
        pass

    statistics.fallbacks = ['gateway.id_1.handle.redirections.post.fallback']
    await taxi_vgw_api.invalidate_caches()

    # Run task several times
    for _ in range(5):
        await taxi_vgw_api.run_periodic_task('gateway-checker')

    assert gateway_disabled.times_called == 0


@pytest.mark.config(
    VGW_API_CLIENT_TIMEOUT=2000,
    VGW_API_USE_NEW_VGW_ENABLE_SETTINGS=True,
    VGW_API_GATEWAY_CHECKER_SETTINGS={
        'enabled': True,
        'period_ms': 100000,
        'success_period_mins': 30,
        'settings_by_disable_reason': {
            '__default__': {
                'retry_delays_mins': [1, 5, 20, 60, 120],
                'retry_forever': True,
            },
        },
    },
    VGW_API_DISABLING_HISTORY_SETTINGS={
        'db_requests': {
            'read_history': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
            'status_change': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
        },
        'history_enabled': True,
        'history_entries_limit': 100,
    },
)
@pytest.mark.suspend_periodic_tasks('gateway-checker')
async def test_async(taxi_vgw_api, testpoint, statistics):
    @testpoint('gateway-checker/gateway-disabled')
    def gateway_disabled(data):
        pass

    statistics.fallbacks = ['gateway.id_1.handle.redirections.post.fallback']
    await taxi_vgw_api.invalidate_caches()

    await asyncio.gather(
        *[
            taxi_vgw_api.run_periodic_task('gateway-checker')
            for _ in range(100)
        ],
    )

    # Gateway id_1 disabled exactly once
    assert gateway_disabled.times_called == 1


def _mark_records_checker_settings(
        check_enabled=True,
        after_enable_delay_s=None,
        after_check_delay_s=None,
        disable_provider=True,
        alarm_enabled=True,
        gateway_check_enabled=True,
        min_len_s=10,
        offset_s=900,
        interval_s=890,
        talks_count=10,
        threshold=1,
):
    return pytest.mark.config(
        VGW_API_GATEWAY_CHECKER_SETTINGS={
            'enabled': True,
            'period_ms': 100000,
            'success_period_mins': 30,
            'settings_by_disable_reason': {
                '__default__': {
                    'retry_delays_mins': [1],
                    'retry_forever': True,
                    'check_enabled': False,
                },
                'no records': {
                    'retry_delays_mins': [1, 5, 20, 60, 120],
                    'retry_forever': True,
                    'check_enabled': check_enabled,
                    'after_enable_delay_s': after_enable_delay_s,
                    'after_check_delay_s': after_check_delay_s,
                    'disable_provider': disable_provider,
                    'alarm_enabled': alarm_enabled,
                },
            },
        },
        VGW_API_GATEWAY_NO_RECORDS_CHECK_SETTINGS={
            '__default__': {
                'check_enabled': False,
                'min_len_s': 0,
                'offset_s': 0,
                'interval_s': 1,
                'talks_count': 1,
                'threshold': 0,
            },
            'id_1': {
                'check_enabled': gateway_check_enabled,
                'min_len_s': min_len_s,
                'offset_s': offset_s,
                'interval_s': interval_s,
                'talks_count': talks_count,
                'threshold': threshold,
            },
        },
    )


@pytest.mark.parametrize(
    [
        'expected_gateway_disabled',
        'expected_checked_count',
        'expected_broken_count',
        'expected_alert_count',
        'expected_disabled_count',
    ],
    [
        pytest.param(True, 5, 5, 5, 1, id='ordinary check'),
        pytest.param(
            False,
            0,
            0,
            0,
            0,
            marks=_mark_records_checker_settings(check_enabled=False),
            id='check disabled',
        ),
        pytest.param(
            False,
            10,
            10,
            10,
            0,
            marks=_mark_records_checker_settings(disable_provider=False),
            id='only alert',
        ),
        pytest.param(
            True,
            5,
            5,
            0,
            1,
            marks=_mark_records_checker_settings(alarm_enabled=False),
            id='only disable',
        ),
        pytest.param(
            False,
            10,
            0,
            0,
            0,
            marks=_mark_records_checker_settings(gateway_check_enabled=False),
            id='gateway check disabled',
        ),
        pytest.param(
            True,
            5,
            5,
            5,
            1,
            marks=_mark_records_checker_settings(after_enable_delay_s=600),
            id='after enable delay short',
        ),
        pytest.param(
            False,
            0,
            0,
            0,
            0,
            marks=_mark_records_checker_settings(after_enable_delay_s=3600),
            id='after enable delay long',
        ),
        pytest.param(
            True,
            1,
            1,
            1,
            1,
            marks=_mark_records_checker_settings(after_check_delay_s=60),
            id='after check delay',
        ),
        pytest.param(
            True,
            5,
            5,
            5,
            1,
            # talks 5, 7
            marks=_mark_records_checker_settings(
                min_len_s=0,
                offset_s=1793,
                interval_s=2,
                talks_count=5,
                threshold=50,
            ),
            id='talks: with short len',
        ),
        pytest.param(
            False,
            10,
            0,
            0,
            0,
            # talk 5
            marks=_mark_records_checker_settings(
                min_len_s=10,
                offset_s=1793,
                interval_s=2,
                talks_count=5,
                threshold=50,
            ),
            id='talks: without short len',
        ),
        pytest.param(
            True,
            5,
            5,
            5,
            1,
            # 3 talks 6...12
            marks=_mark_records_checker_settings(
                offset_s=1788, interval_s=6, talks_count=3, threshold=100,
            ),
            id='talks: random talks',
        ),
        pytest.param(
            True,
            5,
            5,
            5,
            1,
            marks=_mark_records_checker_settings(
                offset_s=1788, interval_s=12, talks_count=20, threshold=50,
            ),
            id='talks: all, small threshold',
        ),
        pytest.param(
            False,
            10,
            0,
            0,
            0,
            marks=_mark_records_checker_settings(
                offset_s=1788, interval_s=12, talks_count=20, threshold=51,
            ),
            id='talks: all, big threshold',
        ),
        pytest.param(
            False,
            10,
            0,
            0,
            0,
            marks=_mark_records_checker_settings(offset_s=1800, interval_s=30),
            id='talks: none',
        ),
    ],
)
@pytest.mark.config(
    VGW_API_CLIENT_TIMEOUT=2000,
    VGW_API_USE_NEW_VGW_ENABLE_SETTINGS=True,
    VGW_API_DISABLING_HISTORY_SETTINGS={
        'db_requests': {
            'read_history': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
            'status_change': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
        },
        'history_enabled': True,
        'history_entries_limit': 100,
    },
)
@_mark_records_checker_settings()
@pytest.mark.pgsql('vgw_api', files=['pg_vgw_api_with_talks.sql'])
@pytest.mark.now('2018-02-26T20:00:00+0300')
@pytest.mark.suspend_periodic_tasks('gateway-checker')
async def test_no_records_check(
        taxi_vgw_api,
        testpoint,
        pgsql,
        taxi_vgw_api_monitor,
        mockserver,
        expected_gateway_disabled,
        expected_checked_count,
        expected_broken_count,
        expected_alert_count,
        expected_disabled_count,
):
    @mockserver.json_handler(r'/talks/(?P<talk_id>\w+/record)', regex=True)
    def _mock_talk(request, talk_id):
        if int(talk_id.split('/')[0].split('_')[-1]) <= 5:
            return 'binary_data'
        return mockserver.make_response(status=404)

    @testpoint('gateway-checker/gateway-checked')
    def gateway_checked(data):
        pass

    @testpoint('gateway-checker/gateway-broken')
    def gateway_broken(data):
        pass

    @testpoint('gateway-checker/gateway-disabled')
    def gateway_disabled(data):
        pass

    await taxi_vgw_api.tests_control(reset_metrics=True)
    await taxi_vgw_api.invalidate_caches()

    # Run task several times
    for _ in range(5):
        await taxi_vgw_api.run_periodic_task('gateway-checker')
    await taxi_vgw_api.invalidate_caches()
    for _ in range(5):
        await taxi_vgw_api.run_periodic_task('gateway-checker')

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT (settings).disabled, disable_reason '
        'FROM voice_gateways.voice_gateways '
        'WHERE id = \'id_1\'',
    )
    gateways = cursor.fetchall()
    cursor.close()
    assert gateways[0][0] == expected_gateway_disabled
    assert gateways[0][1] == (
        'no records' if expected_gateway_disabled else None
    )

    assert gateway_checked.times_called == expected_checked_count
    assert gateway_broken.times_called == expected_broken_count
    assert gateway_disabled.times_called == expected_disabled_count

    stats = await taxi_vgw_api_monitor.get_metrics('vgw')
    if expected_alert_count:
        assert stats['vgw']['gateway_broken'] == {
            'id_1': {
                'no records': expected_alert_count,
                '$meta': {'solomon_children_labels': 'disable_reason'},
            },
            '$meta': {'solomon_children_labels': 'gateway_id'},
        }
    else:
        assert stats['vgw']['gateway_broken'] == {
            '$meta': {'solomon_children_labels': 'gateway_id'},
        }


@pytest.mark.config(
    VGW_API_CLIENT_TIMEOUT=2000,
    VGW_API_USE_NEW_VGW_ENABLE_SETTINGS=True,
    VGW_API_DISABLING_HISTORY_SETTINGS={
        'db_requests': {
            'read_history': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
            'status_change': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
        },
        'history_enabled': True,
        'history_entries_limit': 100,
    },
)
@_mark_records_checker_settings(offset_s=1788, interval_s=12, talks_count=1)
@pytest.mark.pgsql('vgw_api', files=['pg_vgw_api_with_talks.sql'])
@pytest.mark.now('2018-02-26T20:00:00+0300')
@pytest.mark.suspend_periodic_tasks('gateway-checker')
async def test_no_records_random(taxi_vgw_api, mockserver):
    checked_talks = set()

    @mockserver.json_handler(r'/talks/(?P<talk_id>\w+/record)', regex=True)
    def _mock_talk(request, talk_id):
        nonlocal checked_talks
        checked_talks.add(talk_id)
        return 'binary_data'

    # all talks should be checked eventually
    # of 10 talks 3 have s3_key and not downloaded from gateway
    while len(checked_talks) < 7:
        await taxi_vgw_api.run_periodic_task('gateway-checker')
