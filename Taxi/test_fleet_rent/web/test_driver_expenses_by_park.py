import datetime as dt
import decimal

import pytest

from fleet_rent.entities import park as park_entities
from fleet_rent.use_cases.driver_expenses import by_park


@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'Park "{park_name}"': {'ru': 'Парк "{park_name}"'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'Москва'}},
)
async def test_ok(patch, web_app_client, driver_auth_headers, load_json):
    @patch(
        'fleet_rent.use_cases.driver_expenses.by_park.'
        'DriverExpensesByPark.__call__',
    )
    async def _impl(driver_park_id, driver_id, begin_time, end_time):
        assert begin_time == dt.datetime.fromisoformat(
            '2020-01-01T00:00+00:00',
        )
        assert end_time == dt.datetime.fromisoformat('2020-01-01T06:00+00:00')
        assert driver_park_id == 'driver_park_id'
        assert driver_id == 'driver_id'
        res = [
            by_park.ParkExpense(
                park_entities.Park(id='park_id1', name='Name1'),
                amount=decimal.Decimal('333'),
            ),
            by_park.ParkExpense(
                park_entities.Park(id='park_id2', name='Name2'),
                amount=decimal.Decimal('444'),
            ),
        ]
        return by_park.Result(currency='RUB', expenses=res)

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/by-park',
        params={
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-01T06:00+00:00',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body == load_json('ok.json')


@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'Park "{park_name}"': {'ru': 'Парк "{park_name}"'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'Москва'}},
)
async def test_empty(patch, web_app_client, driver_auth_headers):
    @patch(
        'fleet_rent.use_cases.driver_expenses.by_park.'
        'DriverExpensesByPark.__call__',
    )
    async def _impl(driver_park_id, driver_id, begin_time, end_time):
        assert begin_time == dt.datetime.fromisoformat(
            '2020-01-01T00:00+00:00',
        )
        assert end_time == dt.datetime.fromisoformat('2020-01-01T06:00+00:00')
        assert driver_park_id == 'driver_park_id'
        assert driver_id == 'driver_id'
        return by_park.Result(currency='RUB', expenses=[])

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/by-park',
        params={
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-01T06:00+00:00',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body == {
        'ui': {
            'items': [
                {
                    'type': 'header',
                    'html': True,
                    'horizontal_divider_type': 'none',
                    'subtitle': '0,<small>00</small> <small>₽</small>',
                },
            ],
        },
        'begin_time': '2020-01-01T03:00:00+03:00',
        'end_time': '2020-01-01T09:00:00+03:00',
    }


async def test_no_smz(patch, web_app_client, driver_auth_headers):
    @patch(
        'fleet_rent.use_cases.driver_expenses.by_park.'
        'DriverExpensesByPark.__call__',
    )
    async def _impl(driver_park_id, driver_id, begin_time, end_time):
        raise by_park.errors.NonSingleDriverPark()

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/by-park',
        params={
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-01T06:00+00:00',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 400, await response.text()
    body = await response.json()
    assert body['code'] == 'NOT_SINGLE_DRIVER_PARK'


async def test_invalid_times(patch, web_app_client, driver_auth_headers):
    @patch(
        'fleet_rent.use_cases.driver_expenses.by_park.'
        'DriverExpensesByPark.__call__',
    )
    async def _impl(driver_park_id, driver_id, begin_time, end_time):
        raise by_park.errors.InvalidTimePrecision()

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/by-park',
        params={
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-01T06:00+00:00',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 400, await response.text()
    body = await response.json()
    assert body['code'] == 'INVALID_TIME_PRECISION'


async def test_invalid_ranges(patch, web_app_client, driver_auth_headers):
    @patch(
        'fleet_rent.use_cases.driver_expenses.by_park.'
        'DriverExpensesByPark.__call__',
    )
    async def _impl(driver_park_id, driver_id, begin_time, end_time):
        raise by_park.errors.InvalidTimeRange()

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/by-park',
        params={
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-01T06:00+00:00',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 400, await response.text()
    body = await response.json()
    assert body['code'] == 'INVALID_TIME_RANGE'


async def test_non_handleable(patch, web_app_client, driver_auth_headers):
    @patch(
        'fleet_rent.use_cases.driver_expenses.by_park.'
        'DriverExpensesByPark.__call__',
    )
    async def _impl(driver_park_id, driver_id, begin_time, end_time):
        raise by_park.errors.NonHandleableError()

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/by-park',
        params={
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-01T06:00+00:00',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 500, await response.text()
