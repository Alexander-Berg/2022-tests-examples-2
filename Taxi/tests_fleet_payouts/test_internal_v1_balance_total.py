import pytest

from tests_fleet_payouts.utils import xcmp


@pytest.fixture(name='get_balance_total')
def get_balance_total_(taxi_fleet_payouts):
    async def get_balance_total(clid):
        return await taxi_fleet_payouts.get(
            'internal/payouts/v1/balance-total', params={'clid': clid},
        )

    return get_balance_total


@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_empty(get_balance_total):
    response = await get_balance_total('CLID00')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'accrued_at': xcmp.Date('2020-06-01T12:00:00+03:00'),
        'amount': xcmp.Decimal('0.00'),
    }


@pytest.mark.pgsql('fleet_payouts', files=['balances.sql'])
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_zero(get_balance_total):
    response = await get_balance_total('CLID99')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'accrued_at': xcmp.Date('2020-01-01T12:00:00+03:00'),
        'amount': xcmp.Decimal('0.00'),
    }


@pytest.mark.pgsql('fleet_payouts', files=['balances.sql'])
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_one_currency(get_balance_total):
    response = await get_balance_total('CLID00')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'accrued_at': xcmp.Date('2020-01-01T12:00:00+03:00'),
        'amount': xcmp.Decimal('200.00'),
    }


@pytest.mark.pgsql('fleet_payouts', files=['balances.sql'])
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_two_currencies(get_balance_total):
    response = await get_balance_total('CLID01')
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': 'Balance of requested park contains multiple currencies.',
    }
