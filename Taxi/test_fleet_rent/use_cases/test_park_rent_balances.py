import dataclasses
import datetime as dt
import decimal
import typing as tp

import pytest

from fleet_rent.generated.web import web_context as context_module
from fleet_rent.services import billing_reports as brs
from fleet_rent.use_cases import park_rent_balances as prb


async def test_get_rent_list_no_park(web_context: context_module.Context):
    use_case: prb.ParkRentBalances = web_context.use_cases.park_rent_balances

    with pytest.raises(prb.NotAllRentsFound):
        _ = await use_case.get_rent_balances(
            park_id='non_existing',
            rent_ids={'rent1', 'rent2'},
            now=dt.datetime.now(dt.timezone.utc),
        )


@pytest.fixture(name='get_rent_fixtures')
def _get_rent_fixtures(patch, park_stub_factory):
    @dataclasses.dataclass
    class Settings:
        park_id: str
        smz_driver_ids: tp.List[str]
        local_driver_ids: tp.List[str]
        smz_rent_ids: tp.List[str]
        local_rent_ids: tp.List[str]
        contract_currency: tp.Optional[str]
        country_currency: str

    settings = Settings(
        park_id='park_id',
        smz_driver_ids=['driver_id1'],
        local_driver_ids=[
            'driver_id2',
            'driver_id3',
            'driver_id4',
            'driver_id5',
            'driver_id6',
        ],
        smz_rent_ids=['record_id1'],
        local_rent_ids=[
            'record_id2',
            'record_id3',
            'record_id4',
            'record_id5',
            'record_id6',
        ],
        contract_currency='RUB',
        country_currency='RUB',
    )

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, _now):
        assert park_id == settings.park_id
        return settings.contract_currency

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_internal_currency',
    )
    async def _get_internal_currency(park_id: str, _now):
        assert park_id == settings.park_id
        return settings.country_currency

    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.get_balances_by_rent',
    )
    async def _get_balances_by_rent(currency, rents, _now):
        rent_ids = {x.record_id for x in rents}
        assert len(rent_ids) == len(rents)

        if rent_ids == set(settings.local_rent_ids):
            exp_curr = settings.country_currency
            exp_drivers = settings.local_driver_ids
            is_local = True
        elif rent_ids == set(settings.smz_rent_ids):
            exp_curr = settings.country_currency
            exp_drivers = settings.smz_driver_ids
            is_local = False
        else:
            assert False, f'Rent ids mismatch {rent_ids}'

        assert currency == exp_curr
        driver_ids = {x.driver_id for x in rents}
        park_ids = {x.owner_park_id for x in rents}
        assert driver_ids == set(exp_drivers)
        assert park_ids == {'park_id'}
        if is_local:
            return {
                rent_id: brs.BalancesBySubaccount(
                    withdraw=decimal.Decimal(0),
                    cancel=decimal.Decimal(0),
                    withhold=decimal.Decimal(i + 1),
                )
                for i, rent_id in enumerate(sorted(rent_ids))
            }
        # Only selfemployed has nonzero cancel and withdraw
        return {
            'record_id1': brs.BalancesBySubaccount(
                withdraw=decimal.Decimal(111),
                cancel=decimal.Decimal(666),
                withhold=decimal.Decimal(777),
            ),
        }

    return settings


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_get_rent_list_basic(
        web_context: context_module.Context, get_rent_fixtures,
):
    use_case: prb.ParkRentBalances = web_context.use_cases.park_rent_balances

    result = await use_case.get_rent_balances(
        park_id='park_id',
        rent_ids={
            'record_id7',
            'record_id6',
            'record_id5',
            'record_id4',
            'record_id3',
            'record_id2',
            'record_id1',
        },
        now=dt.datetime.now(dt.timezone.utc),
    )
    assert result == {
        'record_id7': prb.BalancesSummary(
            withhold=None, withdraw=None, cancel=decimal.Decimal(0),
        ),
        'record_id6': prb.BalancesSummary(
            withhold=decimal.Decimal(5),
            withdraw=decimal.Decimal(5),
            cancel=decimal.Decimal(0),
        ),
        'record_id5': prb.BalancesSummary(
            withhold=decimal.Decimal(4),
            withdraw=decimal.Decimal(4),
            cancel=decimal.Decimal(0),
        ),
        'record_id4': prb.BalancesSummary(
            withhold=decimal.Decimal(3),
            withdraw=decimal.Decimal(3),
            cancel=decimal.Decimal(0),
        ),
        'record_id3': prb.BalancesSummary(
            withhold=decimal.Decimal(2),
            withdraw=decimal.Decimal(2),
            cancel=decimal.Decimal(0),
        ),
        'record_id2': prb.BalancesSummary(
            withhold=decimal.Decimal(1),
            withdraw=decimal.Decimal(1),
            cancel=decimal.Decimal(0),
        ),
        'record_id1': prb.BalancesSummary(
            withdraw=decimal.Decimal(111),
            cancel=decimal.Decimal(666),
            withhold=decimal.Decimal(777),
        ),
    }


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_get_rent_substitutes(
        web_context: context_module.Context, get_rent_fixtures,
):
    get_rent_fixtures.rent_ids = ['record_id1', 'record_id2', 'record_id3']

    use_case: prb.ParkRentBalances = web_context.use_cases.park_rent_balances

    result = await use_case.get_rent_balances(
        park_id='park_id',
        rent_ids={
            'record_id7',
            'record_id6',
            'record_id5',
            'record_id4',
            'record_id3',
            'record_id2',
            'record_id1',
        },
        now=dt.datetime.now(dt.timezone.utc),
    )
    assert result == {
        'record_id7': prb.BalancesSummary(
            withhold=None, withdraw=None, cancel=decimal.Decimal(0),
        ),
        'record_id6': prb.BalancesSummary(
            withhold=decimal.Decimal(5),
            withdraw=decimal.Decimal(5),
            cancel=decimal.Decimal(0),
        ),
        'record_id5': prb.BalancesSummary(
            withhold=decimal.Decimal(4),
            withdraw=decimal.Decimal(4),
            cancel=decimal.Decimal(0),
        ),
        'record_id4': prb.BalancesSummary(
            withhold=decimal.Decimal(3),
            withdraw=decimal.Decimal(3),
            cancel=decimal.Decimal(0),
        ),
        'record_id3': prb.BalancesSummary(
            withhold=decimal.Decimal(2),
            withdraw=decimal.Decimal(2),
            cancel=decimal.Decimal(0),
        ),
        'record_id2': prb.BalancesSummary(
            withhold=decimal.Decimal(1),
            withdraw=decimal.Decimal(1),
            cancel=decimal.Decimal(0),
        ),
        'record_id1': prb.BalancesSummary(
            withdraw=decimal.Decimal(111),
            cancel=decimal.Decimal(666),
            withhold=decimal.Decimal(777),
        ),
    }


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_get_rent_balances_unexisting(
        web_context: context_module.Context, get_rent_fixtures,
):
    get_rent_fixtures.driver_ids = ['driver_id1', 'driver_id2', 'driver_id3']
    get_rent_fixtures.rent_ids = ['record_id1', 'record_id2', 'record_id3']

    use_case: prb.ParkRentBalances = web_context.use_cases.park_rent_balances

    with pytest.raises(prb.NotAllRentsFound):
        _ = await use_case.get_rent_balances(
            park_id='park_id',
            rent_ids={'ddd', 'record_id3', 'record_id2', 'record_id1'},
            now=dt.datetime.now(dt.timezone.utc),
        )


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_park_rent_correct_substitute_for_park_driver(
        web_context: context_module.Context, patch, park_stub_factory,
):
    use_case: prb.ParkRentBalances = web_context.use_cases.park_rent_balances

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, _now):
        assert park_id == 'park_id'
        return 'RUB'

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_internal_currency',
    )
    async def _get_internal_currency(park_id: str, _now):
        assert park_id == 'park_id'
        return 'RUB'

    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.get_balances_by_rent',
    )
    async def _get_balances_by_rent(currency, rents, _now):
        return {
            'record_id3': brs.BalancesBySubaccount(
                withdraw=decimal.Decimal(111),
                cancel=decimal.Decimal(666),
                withhold=decimal.Decimal(777),
            ),
        }

    result = await use_case.get_rent_balances(
        park_id='park_id',
        rent_ids={'record_id3'},
        now=dt.datetime.now(dt.timezone.utc),
    )
    assert result == {
        'record_id3': prb.BalancesSummary(
            withdraw=decimal.Decimal(777),
            cancel=decimal.Decimal(666),
            withhold=decimal.Decimal(777),
        ),
    }
