import datetime

import pytest


from billing_fin_payouts.monrun_checks import interface_delay


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
async def test_interface_delay(cron_context):
    lags = await interface_delay.load_stats(cron_context)
    assert lags == [
        interface_delay.Lag(
            table='interface.revenues', value=datetime.timedelta(days=377),
        ),
    ]

    out = await interface_delay.run_check(cron_context)
    assert out == '0; table=interface.revenues lag=377 days, 0:00:00'
