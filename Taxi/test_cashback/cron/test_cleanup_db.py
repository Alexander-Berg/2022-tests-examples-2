import pytest


@pytest.mark.skip('fix in TAXIBACKEND-38321')
@pytest.mark.pgsql('cashback', files=['cashback.sql'])
@pytest.mark.now('2019-11-10T01:10:00+0300')
async def test_db_cleanup(cron_runner, pg_cashback):
    events = await pg_cashback.events.all()
    assert len(events) == 3
    order_clears = await pg_cashback.order_clears.all()
    assert len(order_clears) == 2
    order_rates = await pg_cashback.order_rates.all()
    assert len(order_rates) == 2

    await cron_runner.clear_db()

    events = await pg_cashback.events.all()
    assert len(events) == 1
    order_clears = await pg_cashback.order_clears.all()
    assert len(order_clears) == 1
    order_rates = await pg_cashback.order_rates.all()
    assert not order_rates
