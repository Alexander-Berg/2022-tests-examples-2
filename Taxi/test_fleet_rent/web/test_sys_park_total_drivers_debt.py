import decimal
import typing as tp

import pytest

from fleet_rent.use_cases import park_total_drivers_debt


@pytest.mark.parametrize(
    'use_case_response, expected_response',
    [
        (
            park_total_drivers_debt.Debt(
                currency='RUB', debt=decimal.Decimal(10),
            ),
            {'debt_lower_bound': {'amount': '10', 'currency': 'RUB'}},
        ),
        (None, {}),
    ],
)
async def test_ok(patch, web_app_client, use_case_response, expected_response):
    @patch(
        'fleet_rent.use_cases.park_total_drivers_debt'
        '.ParkTotalDriversDebt.__call__',
    )
    async def _call(park_id: str, driver_profile_id: tp.Optional[str]):
        assert park_id == 'park_id'
        assert driver_profile_id == 'did'
        return use_case_response

    response = await web_app_client.get(
        '/fleet-rent/v1/sys/park/rent/drivers/debt',
        params={'park_id': 'park_id', 'driver_profile_id': 'did'},
    )

    assert response.status == 200, await response.text()
    assert await response.json() == expected_response


async def test_independent_park(patch, web_app_client):
    @patch(
        'fleet_rent.use_cases.park_total_drivers_debt'
        '.ParkTotalDriversDebt.__call__',
    )
    async def _call(park_id: str, driver_profile_id: str):
        raise park_total_drivers_debt.NoBillingContractError()

    response = await web_app_client.get(
        '/fleet-rent/v1/sys/park/rent/drivers/debt',
        params={'park_id': 'park_id', 'driver_profile_id': 'did'},
    )

    assert response.status == 200, await response.text()
    assert await response.json() == {}
