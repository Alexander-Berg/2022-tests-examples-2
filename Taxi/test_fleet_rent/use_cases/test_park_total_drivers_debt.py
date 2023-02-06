import datetime
import decimal
import typing

import pytest

from fleet_rent.entities import billing as billing_entities
from fleet_rent.entities import rent as rent_entities
from fleet_rent.generated.web import web_context as context_module
from fleet_rent.use_cases import park_total_drivers_debt


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'driver_id, get_debt_lower_bound_call, expected_response',
    [
        (
            'local_driver_id4',
            True,
            park_total_drivers_debt.Debt(
                currency='RUB', debt=decimal.Decimal(50),
            ),
        ),
        ('no_rents', False, None),
    ],
)
async def test_ok(
        web_context: context_module.Context,
        patch,
        park_stub_factory,
        park_billing_data_stub_factory,
        driver_id,
        get_debt_lower_bound_call,
        expected_response,
):
    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.get_debt_lower_bound',
    )
    async def get_debt_lower_bound(
            currency: str,
            rents: typing.Collection[rent_entities.Rent],
            now: datetime.datetime,
    ):
        assert currency == 'RUB'
        assert {x.record_id for x in rents} == {'record_id4', 'record_id2'}
        return decimal.Decimal(50)

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

    result = await web_context.use_cases.park_total_drivers_debt(
        'park_id', driver_id,
    )
    if get_debt_lower_bound_call:
        assert get_debt_lower_bound.calls
    assert result == expected_response


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
async def test_no_park_billing_contract(
        web_context: context_module.Context,
        patch,
        park_stub_factory,
        park_billing_data_stub_factory,
):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park_info(*args):
        return park_stub_factory('park_id', driver_partner_source='yandex')

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

    with pytest.raises(park_total_drivers_debt.NoBillingContractError):
        await web_context.use_cases.park_total_drivers_debt(
            'park_id', 'local_driver_id4',
        )
