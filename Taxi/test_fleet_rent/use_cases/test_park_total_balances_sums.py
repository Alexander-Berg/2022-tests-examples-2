import datetime
import decimal
import typing

import pytest

from fleet_rent.entities import billing as billing_entities
from fleet_rent.entities import rent as rent_entities
from fleet_rent.generated.web import web_context as context_module
from fleet_rent.services import billing_reports as billing_reports_access
from fleet_rent.use_cases import park_total_balances_sums


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
async def test_ok(
        web_context: context_module.Context,
        patch,
        park_stub_factory,
        park_billing_data_stub_factory,
):
    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.get_balances_by_rent',
    )
    async def _get_balances_by_rent(
            currency: str,
            rents: typing.Collection[rent_entities.Rent],
            now: datetime.datetime,
    ):
        assert currency == 'RUB'
        assert {x.record_id for x in rents} == {
            'record_id4',
            'record_id2',
            'record_id5',
        }
        return {
            'record_id4': billing_reports_access.BalancesBySubaccount(
                withhold=decimal.Decimal(110),
                withdraw=decimal.Decimal(120),
                cancel=decimal.Decimal(130),
            ),
            'record_id2': billing_reports_access.BalancesBySubaccount(
                withhold=decimal.Decimal(330),
                withdraw=decimal.Decimal(200),
                cancel=decimal.Decimal(130),
            ),
            'record_id5': billing_reports_access.BalancesBySubaccount(
                withhold=decimal.Decimal(500),
                withdraw=decimal.Decimal(0),
                cancel=decimal.Decimal(0),
            ),
        }

    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park_info(*args):
        return park_stub_factory('park_id')

    @patch(
        'fleet_rent.services.park_info.ParkInfoService.get_park_billing_data',
    )
    async def _get_park_billing_data(*args):
        return park_billing_data_stub_factory(clid=args[0])

    @patch(
        'fleet_rent.services.billing_replication'
        '.BillingReplicationService.get_park_contract',
    )
    async def _get_park_contract(client_data, *args):
        assert client_data.clid == '100500'
        return billing_entities.Contract(id=0, currency='RUB')

    result = await web_context.use_cases.park_total_balances_sums(
        'park_id', None, None,
    )
    assert result == park_total_balances_sums.Result(
        currency='RUB',
        withhold=decimal.Decimal(940),
        withdraw=decimal.Decimal(820),
        cancel=decimal.Decimal(260),
    )


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
async def test_no_park_billing_contract(
        web_context: context_module.Context,
        patch,
        park_stub_factory,
        park_billing_data_stub_factory,
):
    @patch(
        'fleet_rent.services.park_info.ParkInfoService.get_park_billing_data',
    )
    async def _get_park_billing_data(*args):
        assert args == ('100500',)
        return park_billing_data_stub_factory(clid=None)

    @patch(
        'fleet_rent.services.billing_replication'
        '.BillingReplicationService.get_park_contract',
    )
    async def _get_park_contract(client_data, *args):
        return None

    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park_info(*args):
        return park_stub_factory('park_id')

    @patch(
        'fleet_rent.components.currency_provider'
        '.CurrencyProvider.get_park_internal_currency',
    )
    async def _get_internal_currency(*args):
        return 'RUB'

    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.get_balances_by_rent',
    )
    async def _get_balances_by_rent(
            currency: str,
            rents: typing.Collection[rent_entities.Rent],
            now: datetime.datetime,
    ):
        assert currency == 'RUB'
        assert {x.record_id for x in rents} == {
            'record_id4',
            'record_id2',
            'record_id5',
        }
        return {
            'record_id4': billing_reports_access.BalancesBySubaccount(
                withhold=decimal.Decimal(110),
                withdraw=decimal.Decimal(120),
                cancel=decimal.Decimal(130),
            ),
            'record_id2': billing_reports_access.BalancesBySubaccount(
                withhold=decimal.Decimal(330),
                withdraw=decimal.Decimal(200),
                cancel=decimal.Decimal(130),
            ),
            'record_id5': billing_reports_access.BalancesBySubaccount(
                withhold=decimal.Decimal(500),
                withdraw=decimal.Decimal(0),
                cancel=decimal.Decimal(0),
            ),
        }

    result = await web_context.use_cases.park_total_balances_sums(
        'park_id', None, None,
    )
    assert result == park_total_balances_sums.Result(
        currency='RUB',
        withhold=decimal.Decimal(940),
        withdraw=decimal.Decimal(820),
        cancel=decimal.Decimal(260),
    )
