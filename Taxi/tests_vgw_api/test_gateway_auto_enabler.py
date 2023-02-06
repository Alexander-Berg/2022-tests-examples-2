import asyncio
import datetime

import psycopg2.tz
import pytest

from tests_vgw_api import db_voice_gateways as vg


MOSCOW_TZ = psycopg2.tz.FixedOffsetTimezone(offset=180)


@pytest.mark.now('2021-09-11T12:30:00+03:00')
@pytest.mark.config(
    VGW_API_GATEWAY_ENABLER_SETTINGS={'enabled': True, 'period_ms': 60000},
    VGW_API_GATEWAY_NO_RECORDS_CHECK_SETTINGS={
        '__default__': {
            'check_enabled': True,
            'min_len_s': 0,
            'offset_s': 900,
            'interval_s': 1800,
            'talks_count': 3,
            'threshold': 1,
        },
    },
)
@pytest.mark.suspend_periodic_tasks('gateway-auto-enabler')
async def test_auto_enabler(taxi_vgw_api, mockserver, pgsql, testpoint):
    @mockserver.json_handler(r'/talks/(?P<name>\w+/record)', regex=True)
    def mock_talk(request, name):
        return 'binary_data'

    @testpoint('gateway-auto-enabler/gateway-action')
    def gateway_action(data):
        pass

    # Run task several times
    for _ in range(5):
        await taxi_vgw_api.run_periodic_task('gateway-auto-enabler')

    assert mock_talk.times_called == 3

    assert gateway_action.times_called == 5
    gateways = []
    while gateway_action.times_called > 0:
        gateways.append(gateway_action.next_call()['data'])
    gateways.sort(key=lambda x: x['gateway_id'])

    expected_enabled_gateways = [
        {
            'gateway_id': 'gateway_id_1',
            'action': 'enable',
            'enabler_name': 'no-records-enabler',
        },
        {
            'gateway_id': 'gateway_id_2',
            'action': 'enable',
            'enabler_name': 'no-talks-enabler',
        },
        {
            'gateway_id': 'gateway_id_6',
            'action': 'enable',
            'enabler_name': 'error-enabler',
        },
        {
            'gateway_id': 'gateway_id_7',
            'action': 'enable',
            'enabler_name': 'failed-talks-enabler',
        },
        {
            'gateway_id': 'gateway_id_8',
            'action': 'enable',
            'enabler_name': 'short-talks-enabler',
        },
    ]
    assert gateways == expected_enabled_gateways

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT id '
        'FROM voice_gateways.voice_gateways '
        'WHERE NOT (settings).disabled '
        'ORDER BY id',
    )
    db_gateways = cursor.fetchall()
    cursor.close()

    assert {gateway[0] for gateway in db_gateways} == {
        gateway['gateway_id'] for gateway in expected_enabled_gateways
    }


@pytest.mark.now('2021-09-11T12:30:00+03:00')
@pytest.mark.suspend_periodic_tasks('gateway-auto-enabler')
async def test_auto_enabler_disabled(
        taxi_vgw_api, mockserver, pgsql, testpoint,
):
    @mockserver.json_handler(r'/talks/(?P<name>\w+/record)', regex=True)
    def mock_talk(request, name):
        return 'binary_data'

    @testpoint('gateway-auto-enabler/gateway-action')
    def gateway_action(data):
        pass

    # Run task several times
    for _ in range(5):
        await taxi_vgw_api.run_periodic_task('gateway-auto-enabler')

    assert mock_talk.times_called == 0
    assert gateway_action.times_called == 0
    assert all(
        gateway.settings.disabled for gateway in vg.select_gateways(pgsql)
    )


@pytest.mark.now('2021-09-11T12:30:00+03:00')
@pytest.mark.config(
    VGW_API_GATEWAY_ENABLER_SETTINGS={'enabled': True, 'period_ms': 60000},
    VGW_API_GATEWAY_CHECKER_SETTINGS={
        'enabled': False,
        'period_ms': 1000,
        'success_period_mins': 1,
        'settings_by_disable_reason': {
            '__default__': {
                'retry_delays_mins': [1, 5, 20, 60, 120],
                'retry_forever': True,
            },
        },
    },
    VGW_API_GATEWAY_NO_RECORDS_CHECK_SETTINGS={
        '__default__': {
            'check_enabled': True,
            'min_len_s': 0,
            'offset_s': 900,
            'interval_s': 1800,
            'talks_count': 3,
            'threshold': 1,
        },
    },
)
@pytest.mark.suspend_periodic_tasks('gateway-auto-enabler')
async def test_auto_enabler_prolong_inactivity(
        taxi_vgw_api, mockserver, pgsql, testpoint, statistics,
):
    @mockserver.json_handler(r'/talks/(?P<name>\w+/record)', regex=True)
    def mock_talk(request, name):
        return mockserver.make_response(status=500)

    @testpoint('gateway-auto-enabler/gateway-action')
    def gateway_action(data):
        pass

    statistics.fallbacks = [
        'talks.total.gateway.gateway_id_2.fallback',
        'gateway.gateway_id_6.handle.redirections.post.fallback',
        'talks.fail.gateway.gateway_id_7.fallback',
        'talks.short.gateway.gateway_id_8.fallback',
    ]
    await taxi_vgw_api.invalidate_caches()

    # Run task several times
    for _ in range(5):
        await taxi_vgw_api.run_periodic_task('gateway-auto-enabler')
    await taxi_vgw_api.invalidate_caches()
    for _ in range(5):
        await taxi_vgw_api.run_periodic_task('gateway-auto-enabler')

    assert mock_talk.times_called == 3

    gateway_ids = [
        'gateway_id_1',
        'gateway_id_2',
        'gateway_id_6',
        'gateway_id_7',
        'gateway_id_8',
    ]
    enablers = [
        'no-records-enabler',
        'no-talks-enabler',
        'error-enabler',
        'failed-talks-enabler',
        'short-talks-enabler',
    ]

    actions_count = [0] * len(gateway_ids)
    while gateway_action.times_called > 0:
        data = gateway_action.next_call()['data']
        for i, gateway_id in enumerate(gateway_ids):
            expected_data = {
                'gateway_id': gateway_id,
                'action': 'prolong-inactivity',
                'enabler_name': enablers[i],
            }
            if data == expected_data:
                actions_count[i] += 1
    assert actions_count == [1] * len(gateway_ids)

    for gateway_id, enabler_name in zip(gateway_ids, enablers):
        history = vg.select_disabling_history(pgsql, gateway_id)
        assert len(history) == 2
        assert history[1].additional_enable_data == {
            'message': (
                'unsuccessful gateway check, will disable gateway again'
            ),
        }
        assert history[1].enabled_by == enabler_name
        assert (
            history[0].additional_disable_data
            == history[1].additional_disable_data
        )
        assert history[0].disable_reason == history[1].disable_reason
        assert history[0].disabled_by == enabler_name
        assert history[0].relapse_count == 4
        assert history[0].enable_after == datetime.datetime(
            2021, 9, 11, 14, 30, 0, tzinfo=MOSCOW_TZ,
        )

    assert all(
        gateway.settings.disabled for gateway in vg.select_gateways(pgsql)
    )


@pytest.mark.now('2021-09-11T12:10:00+03:00')
@pytest.mark.config(
    VGW_API_GATEWAY_ENABLER_SETTINGS={'enabled': True, 'period_ms': 60000},
    VGW_API_GATEWAY_CHECKER_SETTINGS={
        'enabled': True,
        'period_ms': 1000,
        'success_period_mins': 1,
        'settings_by_disable_reason': {
            '__default__': {'retry_delays_mins': [1], 'retry_forever': True},
        },
    },
    VGW_API_GATEWAY_NO_RECORDS_CHECK_SETTINGS={
        '__default__': {
            'check_enabled': True,
            'min_len_s': 0,
            'offset_s': 900,
            'interval_s': 1800,
            'talks_count': 3,
            'threshold': 1,
        },
    },
)
@pytest.mark.suspend_periodic_tasks('gateway-auto-enabler', 'gateway-checker')
async def test_auto_enabler_with_checker(
        taxi_vgw_api, mockserver, testpoint, mocked_time, statistics,
):
    @mockserver.json_handler(r'/talks/(?P<name>\w+/record)', regex=True)
    def _mock_talk(request, name):
        return 'binary_data'

    @testpoint('gateway-auto-enabler/gateway-action')
    def gateway_enable_action(data):
        pass

    @testpoint('gateway-checker/gateway-disabled')
    def gateway_disabled(data):
        pass

    # turning on and off gateway_id_2, gateway_id_6, gateway_id_7, gateway_id_8
    run_count = 10
    for _ in range(run_count):
        await taxi_vgw_api.run_periodic_task('gateway-auto-enabler')
        statistics.fallbacks = [
            'talks.total.gateway.gateway_id_2.fallback',
            'gateway.gateway_id_6.handle.redirections.post.fallback',
            'talks.fail.gateway.gateway_id_7.fallback',
            'talks.short.gateway.gateway_id_8.fallback',
        ]
        await taxi_vgw_api.invalidate_caches()
        await taxi_vgw_api.run_periodic_task('gateway-checker')
        mocked_time.sleep(61)
        statistics.fallbacks = []
        await taxi_vgw_api.invalidate_caches()

    # 1 time enabled gateway_id_1
    assert gateway_enable_action.times_called == 4 * run_count + 1
    assert gateway_disabled.times_called == 4 * run_count


@pytest.mark.now('2021-09-11T12:30:00+03:00')
@pytest.mark.config(
    VGW_API_GATEWAY_ENABLER_SETTINGS={'enabled': True, 'period_ms': 60000},
    VGW_API_GATEWAY_NO_RECORDS_CHECK_SETTINGS={
        '__default__': {
            'check_enabled': True,
            'min_len_s': 0,
            'offset_s': 900,
            'interval_s': 1800,
            'talks_count': 3,
            'threshold': 1,
        },
    },
)
@pytest.mark.suspend_periodic_tasks('gateway-auto-enabler')
async def test_async(taxi_vgw_api, mockserver, testpoint):
    @mockserver.json_handler(r'/talks/(?P<name>\w+/record)', regex=True)
    def _mock_talk(request, name):
        return 'binary_data'

    @testpoint('gateway-auto-enabler/gateway-action')
    def gateway_action(data):
        pass

    run_count = 100
    await asyncio.gather(
        *[
            taxi_vgw_api.run_periodic_task('gateway-auto-enabler')
            for _ in range(run_count)
        ],
    )

    # gateways enabled exactly once
    assert gateway_action.times_called == 5
