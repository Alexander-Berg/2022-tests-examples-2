import datetime as dt
import decimal
import typing as tp

import pytest

from fleet_rent.use_cases import park_rent_balances


@pytest.mark.now('2020-12-12T12:45+00:00')
async def test_ok(patch, web_app_client):
    @patch(
        'fleet_rent.use_cases.park_rent_balances.'
        'ParkRentBalances.get_rent_balances',
    )
    async def _get_rent_balances(
            park_id: str,
            rent_ids: tp.Union[tp.FrozenSet[str], tp.Set[str]],
            now: dt.datetime,
    ):
        assert park_id == 'park_id_sample'
        assert rent_ids == {'record1', 'record2'}
        assert now == dt.datetime.fromisoformat('2020-12-12T12:45+00:00')
        return {
            'record1': park_rent_balances.BalancesSummary(
                cancel=decimal.Decimal(4),
                withhold=decimal.Decimal(6),
                withdraw=decimal.Decimal(7),
            ),
            'record2': park_rent_balances.BalancesSummary(
                cancel=decimal.Decimal(14),
                withhold=decimal.Decimal(26),
                withdraw=decimal.Decimal(37),
            ),
            'record3': park_rent_balances.BalancesSummary(
                cancel=None, withhold=None, withdraw=None,
            ),
            'record4': park_rent_balances.BalancesSummary(
                cancel=None, withhold=decimal.Decimal(26), withdraw=None,
            ),
        }

    response = await web_app_client.post(
        '/v1/park/rents/balances/retrieve',
        json={
            'park_id': 'park_id_sample',
            'record_ids': ['record1', 'record2'],
        },
    )
    assert response.status == 200, await response.text()
    assert (await response.json()) == {
        'balances': [
            {
                'record_id': 'record1',
                'values': {'cancel': '4', 'withdraw': '7', 'withhold': '6'},
            },
            {
                'record_id': 'record2',
                'values': {'cancel': '14', 'withdraw': '37', 'withhold': '26'},
            },
        ],
    }


@pytest.mark.now('2020-12-12T12:45+00:00')
async def test_400(patch, web_app_client):
    @patch(
        'fleet_rent.use_cases.park_rent_balances.'
        'ParkRentBalances.get_rent_balances',
    )
    async def _get_rent_balances(
            park_id: str,
            rent_ids: tp.Union[tp.FrozenSet[str], tp.Set[str]],
            now: dt.datetime,
    ):
        assert park_id == 'park_id_sample'
        assert rent_ids == {'record1', 'record2'}
        assert now == dt.datetime.fromisoformat('2020-12-12T12:45+00:00')
        raise park_rent_balances.NotAllRentsFound()

    response = await web_app_client.post(
        '/v1/park/rents/balances/retrieve',
        json={
            'park_id': 'park_id_sample',
            'record_ids': ['record1', 'record2'],
        },
    )
    assert response.status == 400, await response.text()
