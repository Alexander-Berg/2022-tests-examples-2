import decimal

import pytest

from fleet_rent.entities import balance
from fleet_rent.entities import park
from fleet_rent.use_cases import driver_balance_in_park


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_get_balances(web_context, patch):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_internal_currency',
    )
    async def _get_internal_currency(park_id: str, now):
        assert park_id == 'park_id'
        return 'RUB'

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_external_currency(park_id: str, now):
        assert park_id == 'park_id'
        return 'RUB'

    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _park_info(park_id: str):
        assert park_id == 'park_id'
        return park.Park(id=park_id, name='Агент 666')

    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.driver_balance_by_rent',
    )
    async def _get_balance_by_rent(currency, affiliation, rents):
        assert currency == 'RUB'
        assert affiliation.record_id == 'affiliation_id'
        return [
            balance.RentBalance(
                rent=rent, balance=decimal.Decimal(rent.owner_serial_id * 100),
            )
            for rent in rents
        ]

    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.driver_internal_park_balance',
    )
    async def _internal_balance(currency, affiliation):
        assert currency == 'RUB'
        assert affiliation.record_id == 'affiliation_id'
        return decimal.Decimal(100)

    data = await driver_balance_in_park.get_data(
        web_context, 'park_id', 'driver_id', 'driver_park_id',
    )
    assert data.currency == 'RUB'
    assert data.park_info.name == 'Агент 666'
    assert data.balance_internal == decimal.Decimal(100)
    assert [b.balance for b in data.balance_by_rent] == [
        decimal.Decimal(100),
        decimal.Decimal(200),
    ]
