import pytest


from taxi_billing_tlog.monrun_checks import tlog_lag


@pytest.mark.pgsql('billing_tlog@0', files=('journal.sql',))
async def test_tlog_lag(cron_context):
    lag = await tlog_lag.calc_lag_in_seconds(cron_context)
    assert lag
