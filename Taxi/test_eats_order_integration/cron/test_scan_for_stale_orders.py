import pytest

from eats_order_integration.generated.cron import run_cron

CRON_SETTINGS = [
    'eats_order_integration.crontasks.scan_for_stale_orders',
    '-t',
    '0',
]

ENABLED_AND_ONE_ACTION_SCHEDULE = {
    'enabled': True,
    'stale_timeout': 20,
    'cron_interval': 60,
    'action_interval': 60,
}


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_SCAN_FOR_STALE_ORDERS_SETTINGS={'enabled': False},
)
async def test_should_not_start_if_disabled(stq):
    await run_cron.main(CRON_SETTINGS)
    assert not stq.eats_order_integration_fallback_to_core.has_calls


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_SCAN_FOR_STALE_ORDERS_SETTINGS={
        **ENABLED_AND_ONE_ACTION_SCHEDULE,
    },
)
@pytest.mark.pgsql('eats_order_integration', files=['stale_orders.sql'])
async def test_should_send_stale_orders_to_support(stq):
    await run_cron.main(CRON_SETTINGS)
    assert stq.eats_order_integration_fallback_to_core.times_called == 2


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_SCAN_FOR_STALE_ORDERS_SETTINGS={
        **ENABLED_AND_ONE_ACTION_SCHEDULE,
    },
)
@pytest.mark.pgsql('eats_order_integration', files=['processed_orders.sql'])
async def test_should_skip_processed_orders(stq):
    await run_cron.main(CRON_SETTINGS)
    assert stq.eats_order_integration_fallback_to_core.times_called == 0


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_SCAN_FOR_STALE_ORDERS_SETTINGS={
        **ENABLED_AND_ONE_ACTION_SCHEDULE,
        'stale_timeout': 86400 * 365 * 50,  # 50 years in seconds
    },
)
@pytest.mark.pgsql('eats_order_integration', files=['orders_in_progress.sql'])
async def test_should_skip_orders_in_progress(stq):
    await run_cron.main(CRON_SETTINGS)
    assert stq.eats_order_integration_fallback_to_core.times_called == 0


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_SCAN_FOR_STALE_ORDERS_SETTINGS={
        **ENABLED_AND_ONE_ACTION_SCHEDULE,
        'stale_timeout': 1,
    },
)
@pytest.mark.pgsql('eats_order_integration', files=['orders_in_progress.sql'])
async def test_should_send_stale_orders_if_they_updated_long_ago(
        stq, load_json,
):
    stq_test = stq.eats_order_integration_fallback_to_core
    new_json = load_json('stale_orders.json')

    await run_cron.main(CRON_SETTINGS)
    assert stq_test.times_called == 2

    for i in range(2):
        call = stq_test.next_call()
        assert call['kwargs'] == new_json[i]


@pytest.mark.config(
    EATS_ORDER_INTEGRATION_SCAN_FOR_STALE_ORDERS_SETTINGS={
        **ENABLED_AND_ONE_ACTION_SCHEDULE,
    },
)
@pytest.mark.pgsql(
    'eats_order_integration',
    files=['created_long_ago_but_updated_recently.sql'],
)
async def test_should_skip_created_long_ago_but_updated_recently(stq):
    await run_cron.main(CRON_SETTINGS)
    assert stq.eats_order_integration_fallback_to_core.times_called == 0
