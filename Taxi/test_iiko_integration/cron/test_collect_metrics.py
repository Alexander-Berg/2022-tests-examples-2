import pytest

from iiko_integration.generated.cron import run_cron
from test_iiko_integration import stubs


@pytest.mark.now('2020-06-11T09:05:10+00:00')
@pytest.mark.config(
    IIKO_INTEGRATION_RESTAURANT_INFO=stubs.CONFIG_RESTAURANT_INFO,
    QR_PAY_ORDER_EXPIRATION={
        'expiration_conditions': [
            {'restaurant_status': 'PENDING', 'expiration_time': 5},
            {
                'restaurant_status': 'PENDING',
                'expiration_time': 11,
                'state_name': 'pending_11s',
            },
            {
                'invoice_status': 'HOLDING',
                'restaurant_status': 'PENDING',
                'expiration_time': 5,
            },
            {
                'invoice_status': 'HOLDING',
                'restaurant_status': 'PENDING',
                'expiration_time': 11,
                'state_name': 'pending_holding_11s',
            },
            {
                'invoice_status': 'INIT',
                'restaurant_status': 'CLOSED',
                'expiration_time': 5,
            },
        ],
        'time_window': 36000,
    },
)
async def test_collect_metrics(check_metrics, load_json):
    check_metrics(expected_metrics=load_json('expected_metrics.json'))
    await run_cron.main(
        ['iiko_integration.crontasks.collect_metrics', '-t', '0'],
    )
