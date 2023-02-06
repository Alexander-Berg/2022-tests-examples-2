import datetime

import pytest


from billing_fin_payouts.monrun_checks import cleanup_lag


@pytest.mark.config(
    BILLING_FIN_PAYOUTS_FETCH_STATS_ENABLED=True,
    BILLING_FIN_PAYOUTS_TABLE_SETTINGS={
        'interface.revenues': {
            'primary_key_field': 'id',
            'created_at_field': 'created_at_utc',
        },
    },
)
@pytest.mark.pgsql('billing_fin_payouts', files=['interface_revenues.sql'])
async def test_cleanup_lag(cron_context):
    lags = await cleanup_lag.load_stats(cron_context)
    assert lags == [
        cleanup_lag.Lag(
            table='interface.revenues', value=datetime.timedelta(days=358),
        ),
    ]

    out = await cleanup_lag.run_check(cron_context)
    assert out == '0; table=interface.revenues lag=358 days, 0:00:00'
