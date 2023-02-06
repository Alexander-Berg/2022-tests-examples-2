import pytest

from tests_fleet_payouts.utils import pg
from tests_fleet_payouts.utils import xcmp


EVERY_SAT_14_00 = {
    'condition': {'clid': ['CLID00']},
    'definition': {'enable_schedule': {'days': ['sat'], 'time': '14:00'}},
}

EVERY_3_DAYS_14_00 = {
    'condition': {'clid': ['CLID00']},
    'definition': {'enable_schedule': {'period': 3, 'time': '14:00'}},
}

CREATED_PAYMENT_ID = 'CLID00_75054400'

CREATED_PAYMENT = {
    'payment_id': CREATED_PAYMENT_ID,
    'clid': 'CLID00',
    'balance_id': '75054400',
    'created_at': None,
    'updated_at': None,
    'origin': 'scheduled',
    'status': 'created',
    'doc_id': None,
}

CREATED_PAYMENT_ENTRIES = {
    (CREATED_PAYMENT_ID, '278761'): {
        'payment_id': CREATED_PAYMENT_ID,
        'contract_id': '278761',
        'bcid': '32511442',
        'amount': xcmp.Decimal('4232.21'),
        'currency': 'RUB',
        'status_code': None,
        'status_message': None,
        'reject_code': None,
        'reject_message': None,
    },
    (CREATED_PAYMENT_ID, '656839'): {
        'payment_id': CREATED_PAYMENT_ID,
        'contract_id': '656839',
        'bcid': '55966500',
        'amount': xcmp.Decimal('423.21'),
        'currency': 'EUR',
        'status_code': None,
        'status_message': None,
        'reject_code': None,
        'reject_message': None,
    },
    (CREATED_PAYMENT_ID, '679178'): {
        'payment_id': CREATED_PAYMENT_ID,
        'contract_id': '679178',
        'bcid': '32511442',
        'amount': xcmp.Decimal('703.0'),
        'currency': 'EUR',
        'status_code': None,
        'status_message': None,
        'reject_code': None,
        'reject_message': None,
    },
    (CREATED_PAYMENT_ID, '844463'): {
        'payment_id': CREATED_PAYMENT_ID,
        'contract_id': '844463',
        'bcid': '30429664',
        'amount': xcmp.Decimal('19660.8'),
        'currency': 'RUB',
        'status_code': None,
        'status_message': None,
        'reject_code': None,
        'reject_message': None,
    },
}


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'inactive_timers.sql'],
)
@pytest.mark.now('2020-03-21T13:59:59.999999+03:00')
@pytest.mark.config(FLEET_PAYOUTS_WITHDRAWAL_RULES=[EVERY_SAT_14_00])
async def test_weekly_lt(taxi_fleet_payouts, mock_parks_by_clids, pgsql):
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == {
        **initial_payment_timers,
        'CLID00': {
            **initial_payment_timers['CLID00'],
            'expires_at': xcmp.Date('2020-03-21T14:00:00+03:00'),
        },
    }
    assert pg.dump_payments(pgsql) == {}
    assert pg.dump_payment_entries(pgsql) == {}


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'inactive_timers.sql'],
)
@pytest.mark.now('2020-03-21T14:00:00.000000+03:00')
@pytest.mark.config(FLEET_PAYOUTS_WITHDRAWAL_RULES=[EVERY_SAT_14_00])
async def test_weekly_ge(taxi_fleet_payouts, mock_parks_by_clids, pgsql):
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == {
        **initial_payment_timers,
        'CLID00': {
            **initial_payment_timers['CLID00'],
            'expires_at': xcmp.Date('2020-03-28T14:00:00+03:00'),
        },
    }
    assert pg.dump_payments(pgsql) == {}
    assert pg.dump_payment_entries(pgsql) == {}


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'inactive_timers.sql'],
)
@pytest.mark.now('2020-03-21T13:59:59.999999+03:00')
@pytest.mark.config(FLEET_PAYOUTS_WITHDRAWAL_RULES=[EVERY_3_DAYS_14_00])
async def test_periodically_lt(taxi_fleet_payouts, mock_parks_by_clids, pgsql):
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == {
        **initial_payment_timers,
        'CLID00': {
            **initial_payment_timers['CLID00'],
            'expires_at': xcmp.Date('2020-03-21T14:00:00+03:00'),
        },
    }
    assert pg.dump_payments(pgsql) == {}
    assert pg.dump_payment_entries(pgsql) == {}


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'inactive_timers.sql'],
)
@pytest.mark.now('2020-03-21T14:00:00.000000+03:00')
@pytest.mark.config(FLEET_PAYOUTS_WITHDRAWAL_RULES=[EVERY_3_DAYS_14_00])
async def test_periodically_ge(taxi_fleet_payouts, mock_parks_by_clids, pgsql):
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == {
        **initial_payment_timers,
        'CLID00': {
            **initial_payment_timers['CLID00'],
            'expires_at': xcmp.Date('2020-03-22T14:00:00+03:00'),
        },
    }
    assert pg.dump_payments(pgsql) == {}
    assert pg.dump_payment_entries(pgsql) == {}


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'active_timers.sql'],
)
@pytest.mark.now('2020-03-21T13:59:59.999999+03:00')
@pytest.mark.config(FLEET_PAYOUTS_WITHDRAWAL_RULES=[EVERY_SAT_14_00])
async def test_expired_lt(taxi_fleet_payouts, mock_parks_by_clids, pgsql):
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == initial_payment_timers
    assert pg.dump_payments(pgsql) == {}
    assert pg.dump_payment_entries(pgsql) == {}


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'active_timers.sql'],
)
@pytest.mark.now('2020-03-21T14:00:00.000000+03:00')
@pytest.mark.config(FLEET_PAYOUTS_WITHDRAWAL_RULES=[EVERY_SAT_14_00])
async def test_expired_ge(taxi_fleet_payouts, mock_parks_by_clids, pgsql):
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == {
        **initial_payment_timers,
        'CLID00': {
            # Schedule at next time, i.e. next saturday 14:00.
            **initial_payment_timers['CLID00'],
            'expires_at': xcmp.Date('2020-03-28T14:00:00+03:00'),
        },
        'CLID01': {
            # Schedule is disabled for this clid.
            **initial_payment_timers['CLID01'],
            'expires_at': None,
        },
    }
    assert pg.dump_payments(pgsql) == {
        CREATED_PAYMENT_ID: {
            **CREATED_PAYMENT,
            'created_at': xcmp.Date('2020-03-21T14:00:00.000000+03:00'),
            'updated_at': xcmp.Date('2020-03-21T14:00:00.000000+03:00'),
        },
    }
    assert pg.dump_payment_entries(pgsql) == CREATED_PAYMENT_ENTRIES


@pytest.mark.pgsql(
    'fleet_payouts', files=['zero_balance.sql', 'active_timers.sql'],
)
@pytest.mark.now('2020-03-21T14:00:00.000000+03:00')
@pytest.mark.config(FLEET_PAYOUTS_WITHDRAWAL_RULES=[EVERY_SAT_14_00])
async def test_defer_due_zero_balance(
        taxi_fleet_payouts, mock_parks_by_clids, pgsql,
):
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == {
        **initial_payment_timers,
        'CLID00': {
            # Schedule at next time, i.e. next saturday 14:00.
            **initial_payment_timers['CLID00'],
            'expires_at': xcmp.Date('2020-03-28T14:00:00+03:00'),
        },
        'CLID01': {
            # Schedule is disabled for this clid.
            **initial_payment_timers['CLID01'],
            'expires_at': None,
        },
    }
    assert pg.dump_payments(pgsql) == {}
    assert pg.dump_payment_entries(pgsql) == {}


@pytest.mark.pgsql('fleet_payouts', files=['active_timers.sql'])
@pytest.mark.now('2020-03-21T14:00:00.000000+03:00')
@pytest.mark.config(FLEET_PAYOUTS_WITHDRAWAL_RULES=[EVERY_SAT_14_00])
async def test_defer_due_outdated_balance(
        taxi_fleet_payouts, mock_parks_by_clids, pgsql,
):
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == {
        **initial_payment_timers,
        'CLID00': {
            # Schedule at 1 hour ahead.
            **initial_payment_timers['CLID00'],
            'expires_at': xcmp.Date('2020-03-21T15:00:00+03:00'),
        },
        'CLID01': {
            # Schedule is disabled for this clid.
            **initial_payment_timers['CLID01'],
            'expires_at': None,
        },
    }
    assert pg.dump_payments(pgsql) == {}
    assert pg.dump_payment_entries(pgsql) == {}


@pytest.mark.pgsql(
    'fleet_payouts',
    files=['balances.sql', 'conflicting_payment_00.sql', 'active_timers.sql'],
)
@pytest.mark.now('2020-03-21T14:00:00.000000+03:00')
@pytest.mark.config(FLEET_PAYOUTS_WITHDRAWAL_RULES=[EVERY_SAT_14_00])
async def test_defer_due_to_conflict_00(
        taxi_fleet_payouts, mock_parks_by_clids, pgsql,
):
    initial_payment_timers = pg.dump_payment_timers(pgsql)
    initial_payments = pg.dump_payments(pgsql)
    initial_payment_entries = pg.dump_payment_entries(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == {
        **initial_payment_timers,
        'CLID00': {
            # Another payment with same balance id exists.
            # Schedule at next time.
            **initial_payment_timers['CLID00'],
            'expires_at': xcmp.Date('2020-03-28T14:00:00+03:00'),
        },
        'CLID01': {
            # Schedule is disabled for this clid.
            **initial_payment_timers['CLID01'],
            'expires_at': None,
        },
    }
    assert pg.dump_payments(pgsql) == initial_payments
    assert pg.dump_payment_entries(pgsql) == initial_payment_entries


@pytest.mark.pgsql(
    'fleet_payouts',
    files=['balances.sql', 'conflicting_payment_01.sql', 'active_timers.sql'],
)
@pytest.mark.now('2020-03-21T14:00:00.000000+03:00')
@pytest.mark.config(FLEET_PAYOUTS_WITHDRAWAL_RULES=[EVERY_SAT_14_00])
async def test_defer_due_to_conflict_01(
        taxi_fleet_payouts, mock_parks_by_clids, pgsql,
):
    initial_payment_timers = pg.dump_payment_timers(pgsql)
    initial_payments = pg.dump_payments(pgsql)
    initial_payment_entries = pg.dump_payment_entries(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == {
        **initial_payment_timers,
        'CLID00': {
            # Another scheduled pending payment exists.
            # Schedule at tomorrow.
            **initial_payment_timers['CLID00'],
            'expires_at': xcmp.Date('2020-03-22T14:00:00+03:00'),
        },
        'CLID01': {
            # Schedule is disabled for this clid.
            **initial_payment_timers['CLID01'],
            'expires_at': None,
        },
    }
    assert pg.dump_payments(pgsql) == initial_payments
    assert pg.dump_payment_entries(pgsql) == initial_payment_entries


@pytest.mark.pgsql(
    'fleet_payouts',
    files=['balances.sql', 'conflicting_payment_02.sql', 'active_timers.sql'],
)
@pytest.mark.now('2020-03-21T14:00:00.000000+03:00')
@pytest.mark.config(FLEET_PAYOUTS_WITHDRAWAL_RULES=[EVERY_SAT_14_00])
async def test_defer_due_to_conflict_02(
        taxi_fleet_payouts, mock_parks_by_clids, pgsql,
):
    initial_payment_timers = pg.dump_payment_timers(pgsql)
    initial_payments = pg.dump_payments(pgsql)
    initial_payment_entries = pg.dump_payment_entries(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == {
        **initial_payment_timers,
        'CLID00': {
            # Another requested pending payment exists.
            # Schedule at tomorrow.
            **initial_payment_timers['CLID00'],
            'expires_at': xcmp.Date('2020-03-22T14:00:00+03:00'),
        },
        'CLID01': {
            # Schedule is disabled for this clid.
            **initial_payment_timers['CLID01'],
            'expires_at': None,
        },
    }
    assert pg.dump_payments(pgsql) == initial_payments
    assert pg.dump_payment_entries(pgsql) == initial_payment_entries


@pytest.mark.pgsql('fleet_payouts', files=['multiple_active_timers.sql'])
@pytest.mark.now('2020-03-21T14:00:00.000000+03:00')
@pytest.mark.config(
    FLEET_PAYOUTS_PERIODIC_PAYMENT_CRON={
        'enable': False,
        'max_payments': 10,
        'period': 1,
    },
    FLEET_PAYOUTS_WITHDRAWAL_RULES=[
        {
            'condition': {
                'clid': ['CLID00', 'CLID01', 'CLID02', 'CLID03', 'CLID04'],
            },
            'definition': {'enable_schedule': {'period': 1, 'time': '14:00'}},
        },
        {
            'condition': {
                'partner_type': ['self_employed'],
                'payout_mode': 'on_demand',
            },
            'definition': {'enable_schedule': {'period': 14, 'time': '03:00'}},
        },
        {
            'condition': {'partner_type': ['self_employed']},
            'definition': {'enable_schedule': {'period': 1, 'time': '03:00'}},
        },
    ],
)
async def test_multiple_active_timers(
        taxi_fleet_payouts, mock_parks_by_clids, pgsql,
):
    await taxi_fleet_payouts.run_task('periodic-payment-cron')

    assert pg.dump_payment_timers(pgsql) == {
        'CLID00': {
            'clid': 'CLID00',
            'expires_at': xcmp.Date('2020-03-22T14:00:00+03:00'),
        },
        'CLID01': {
            'clid': 'CLID01',
            'expires_at': xcmp.Date('2020-03-22T14:00:00+03:00'),
        },
        'CLID02': {
            'clid': 'CLID02',
            'expires_at': xcmp.Date('2020-03-22T14:00:00+03:00'),
        },
        'CLID03': {
            'clid': 'CLID03',
            'expires_at': xcmp.Date('2020-03-22T14:00:00+03:00'),
        },
        'CLID04': {
            'clid': 'CLID04',
            'expires_at': xcmp.Date('2020-03-22T14:00:00+03:00'),
        },
        'CLID05': {
            'clid': 'CLID05',
            'expires_at': xcmp.Date('2020-04-04T03:00:00+03:00'),
        },
        'CLID06': {
            'clid': 'CLID06',
            'expires_at': xcmp.Date('2020-03-22T03:00:00+03:00'),
        },
    }
    assert pg.dump_payments(pgsql) == {
        'CLID00_75054400': {
            'payment_id': 'CLID00_75054400',
            'clid': 'CLID00',
            'balance_id': '75054400',
            'created_at': xcmp.Date('2020-03-21T14:00:00.000000+03:00'),
            'updated_at': xcmp.Date('2020-03-21T14:00:00.000000+03:00'),
            'origin': 'scheduled',
            'status': 'created',
            'doc_id': None,
        },
        'CLID02_75054400': {
            'payment_id': 'CLID02_75054400',
            'clid': 'CLID02',
            'balance_id': '75054400',
            'created_at': xcmp.Date('2020-03-21T14:00:00.000000+03:00'),
            'updated_at': xcmp.Date('2020-03-21T14:00:00.000000+03:00'),
            'origin': 'scheduled',
            'status': 'created',
            'doc_id': None,
        },
        'CLID04_75054400': {
            'payment_id': 'CLID04_75054400',
            'clid': 'CLID04',
            'balance_id': '75054400',
            'created_at': xcmp.Date('2020-03-21T14:00:00.000000+03:00'),
            'updated_at': xcmp.Date('2020-03-21T14:00:00.000000+03:00'),
            'origin': 'scheduled',
            'status': 'created',
            'doc_id': None,
        },
    }
    assert pg.dump_payment_entries(pgsql) == {
        ('CLID00_75054400', '293599'): {
            'payment_id': 'CLID00_75054400',
            'contract_id': '293599',
            'bcid': '34501203',
            'amount': xcmp.Decimal('10000.0'),
            'currency': 'RUB',
            'status_code': None,
            'status_message': None,
            'reject_code': None,
            'reject_message': None,
        },
        ('CLID02_75054400', '293599'): {
            'payment_id': 'CLID02_75054400',
            'contract_id': '293599',
            'bcid': '34501203',
            'amount': xcmp.Decimal('30000.0'),
            'currency': 'RUB',
            'status_code': None,
            'status_message': None,
            'reject_code': None,
            'reject_message': None,
        },
        ('CLID04_75054400', '293599'): {
            'payment_id': 'CLID04_75054400',
            'contract_id': '293599',
            'bcid': '34501203',
            'amount': xcmp.Decimal('50000.0'),
            'currency': 'RUB',
            'status_code': None,
            'status_message': None,
            'reject_code': None,
            'reject_message': None,
        },
    }
