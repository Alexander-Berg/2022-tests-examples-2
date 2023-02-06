import pytest

from tests_fleet_payouts.utils import pg


@pytest.mark.now('2020-01-01T01:00:00+03:00')
@pytest.mark.pgsql('fleet_payouts', files=['payments.sql'])
async def test_reschedule(taxi_fleet_payouts, pgsql):
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-park-reschedule')

    pg_dump = pg.dump_payment_timers(pgsql)

    assert initial_payment_timers['CLID00'] != pg_dump['CLID00']
    assert initial_payment_timers['CLID01'] == pg_dump['CLID01']


@pytest.mark.now('2020-01-01T03:00:00+03:00')
@pytest.mark.pgsql('fleet_payouts', files=['payments.sql'])
async def test_no_reschedule(taxi_fleet_payouts, pgsql):
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-park-reschedule')

    assert initial_payment_timers == pg.dump_payment_timers(pgsql)


@pytest.mark.now('2020-01-01T23:59:59+03:00')
@pytest.mark.pgsql('fleet_payouts', files=['payments.sql'])
async def test_no_reschedule2(taxi_fleet_payouts, pgsql):
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-park-reschedule')

    assert initial_payment_timers == pg.dump_payment_timers(pgsql)
