"""
WARNING
Do not set waybill resolution 'complete' in this job
"""

import pytest

# pylint: disable=invalid-name
pytestmark = [pytest.mark.usefixtures('set_up_alive_batch_exp')]


async def test_counters(state_cancelled_resolved, taxi_cargo_dispatch_monitor):
    result = state_cancelled_resolved
    result['stats'].pop('oldest-waybill-lag-ms')
    assert result['stats'] == {
        'waybills-for-handling': 1,
        'resolved-notified': 1,
        'updated-entries': 1,
        'unresolved-fail': 0,
        'stq-fail': 0,
    }
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-orders',
    )
    assert stats['stats']['marked-as-resolved'] == 0


@pytest.mark.now('2020-04-01T10:35:01+0000')
async def test_oldest_waybill_lag(
        happy_path_state_orders_created,
        run_notify_orders,
        pgsql,
        trigger_need_to_notify_orders,
        mock_claims_bulk_info,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
):
    await trigger_need_to_notify_orders('waybill_fb_3')
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)

    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
    UPDATE cargo_dispatch.waybills
    SET updated_ts='2020-04-01T10:35:00+0000'
        """,
    )

    result = await run_notify_orders()
    assert result['stats'] == {
        'waybills-for-handling': 1,
        'resolved-notified': 0,
        'updated-entries': 1,
        'oldest-waybill-lag-ms': 1000,
        'unresolved-fail': 0,
        'stq-fail': 0,
    }
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-orders',
    )
    assert stats['stats']['marked-as-resolved'] == 0


@pytest.mark.config(
    CARGO_DISPATCH_NOTIFY_ORDERS_SETTINGS={
        'enabled': True,
        'limit': 1000,
        'rate_limit': {'limit': 10, 'interval': 1, 'burst': 20},
    },
)
@pytest.mark.parametrize(
    'quota, expected_waybills_count', [(10, 2), (2, 2), (1, 1)],
)
async def test_rate_limit(
        happy_path_state_orders_created,
        taxi_cargo_dispatch_monitor,
        run_notify_orders,
        rps_limiter,
        trigger_need_to_notify_orders,
        quota,
        expected_waybills_count,
):
    rps_limiter.set_budget('cargo-dispatch-notify-orders', quota)

    await trigger_need_to_notify_orders('waybill_smart_1')
    await trigger_need_to_notify_orders('waybill_fb_3')
    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == expected_waybills_count

    statistics = await taxi_cargo_dispatch_monitor.get_metric('rps-limiter')
    limiter = statistics['cargo-dispatch-distlocks-limiter']
    assert limiter['quota-requests-failed'] == 0

    resource = limiter['resource_stat']['cargo-dispatch-notify-orders']
    assert resource['decision']['rejected'] == 0
    assert resource['quota-assigned'] == quota
    assert resource['limit'] == 10
