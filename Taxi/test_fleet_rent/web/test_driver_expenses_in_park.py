import datetime
import datetime as dt
import decimal

import pytest

from fleet_rent.entities import rent as rent_entities
from fleet_rent.use_cases.driver_expenses import errors
from fleet_rent.use_cases.driver_expenses import in_park


@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'Park "{park_name}"': {'ru': 'Парк "{park_name}"'},
        'driver_expenses_in_park_details_description': {
            'ru': (
                'Оплата за {rent_details}. '
                'Эта сумма будет удержана с баланса.'
            ),
        },
        'rent_name': {'ru': 'Списание №{id}'},
        'Services payment': {'ru': 'Оплата услуг'},
        'Vehicle': {'ru': 'Автомобиль'},
        'rent_asset_car': {'ru': '{model} {brand} {number}'},
        'rent_asset_other_phone': {'ru': 'Телефон'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'Москва'}},
)
async def test_multi_date(
        patch,
        web_app_client,
        driver_auth_headers,
        load_json,
        park_stub_factory,
        rent_stub_factory,
        car_stub_factory,
):
    @patch(
        'fleet_rent.use_cases.driver_expenses.in_park.'
        'DriverExpensesInPark.__call__',
    )
    async def _impl(park_id, driver_park_id, driver_id, begin_time, end_time):
        assert park_id == 'park_id'
        assert begin_time == dt.datetime.fromisoformat(
            '2020-01-01T00:00+00:00',
        )
        assert end_time == dt.datetime.fromisoformat('2020-01-06T00:00+00:00')
        assert driver_park_id == 'driver_park_id'
        assert driver_id == 'driver_id'
        periodicity = rent_entities.charging.daily_periodicity
        res = [
            in_park.RentExpenses(
                in_park.CarRentData(
                    rent=rent_stub_factory(
                        'record1',
                        owner_serial_id=1,
                        asset=rent_entities.asset.AssetCar(
                            car_id='car_id', car_copy_id='car_copy',
                        ),
                        charging=rent_entities.charging.ChargingDaily(
                            starts_at=datetime.datetime(
                                2020, 1, 1, tzinfo=datetime.timezone.utc,
                            ),
                            finishes_at=None,
                            total_withhold_limit=None,
                            daily_price=decimal.Decimal(10),
                            periodicity=periodicity.DailyPeriodicityFraction(
                                1, 3,
                            ),
                            time=datetime.time(0, 0),
                        ),
                    ),
                    car_info=car_stub_factory(),
                ),
                [
                    in_park.Expense(
                        timestamp=datetime.datetime(
                            2020, 1, 1, 10, 30, tzinfo=datetime.timezone.utc,
                        ),
                        amount=decimal.Decimal(10),
                    ),
                    in_park.Expense(
                        timestamp=datetime.datetime(
                            2020, 1, 5, 10, 30, tzinfo=datetime.timezone.utc,
                        ),
                        amount=decimal.Decimal(10),
                    ),
                ],
            ),
            in_park.RentExpenses(
                in_park.OtherRentData(
                    rent=rent_stub_factory(
                        'record1',
                        owner_serial_id=1,
                        asset=rent_entities.asset.AssetOther(
                            subtype='phone', description='Описание',
                        ),
                        charging=rent_entities.charging.ChargingDaily(
                            starts_at=datetime.datetime(
                                2020, 1, 1, tzinfo=datetime.timezone.utc,
                            ),
                            finishes_at=None,
                            total_withhold_limit=None,
                            daily_price=decimal.Decimal(10),
                            periodicity=periodicity.DailyPeriodicityFraction(
                                1, 3,
                            ),
                            time=datetime.time(0, 0),
                        ),
                    ),
                ),
                [
                    in_park.Expense(
                        timestamp=datetime.datetime(
                            2020, 1, 1, 12, 10, tzinfo=datetime.timezone.utc,
                        ),
                        amount=decimal.Decimal(10),
                    ),
                    in_park.Expense(
                        timestamp=datetime.datetime(
                            2020, 1, 5, 12, 10, tzinfo=datetime.timezone.utc,
                        ),
                        amount=decimal.Decimal(10),
                    ),
                ],
            ),
        ]
        return in_park.Result(
            currency='RUB',
            owner_park=park_stub_factory(id=park_id),
            driver_park=park_stub_factory(
                id=driver_id, driver_partner_source='selfemployed',
            ),
            expenses=res,
        )

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/in-park',
        params={
            'rent_park_id': 'park_id',
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-06T00:00+00:00',
            'tz': 'Europe/Moscow',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 200
    body = await response.json()
    assert body == load_json('multi-date.json')


@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'Park "{park_name}"': {'ru': 'Парк "{park_name}"'},
        'driver_expenses_in_park_details_description': {
            'ru': (
                'Оплата за {rent_details}. '
                'Эта сумма будет удержана с баланса.'
            ),
        },
        'rent_name': {'ru': 'Списание №{id}'},
        'Services payment': {'ru': 'Оплата услуг'},
        'Vehicle': {'ru': 'Автомобиль'},
        'rent_asset_car': {'ru': '{model} {brand} {number}'},
        'rent_asset_other_phone': {'ru': 'Телефон'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'Москва'}},
)
async def test_single_date(
        patch,
        web_app_client,
        driver_auth_headers,
        load_json,
        park_stub_factory,
        rent_stub_factory,
        car_stub_factory,
):
    @patch(
        'fleet_rent.use_cases.driver_expenses.in_park.'
        'DriverExpensesInPark.__call__',
    )
    async def _impl(park_id, driver_park_id, driver_id, begin_time, end_time):
        assert park_id == 'park_id'
        assert begin_time == dt.datetime.fromisoformat(
            '2020-01-01T00:00+00:00',
        )
        assert end_time == dt.datetime.fromisoformat('2020-01-01T20:00+00:00')
        assert driver_park_id == 'driver_park_id'
        assert driver_id == 'driver_id'
        periodicity = rent_entities.charging.daily_periodicity
        res = [
            in_park.RentExpenses(
                in_park.CarRentData(
                    rent=rent_stub_factory(
                        'record1',
                        owner_serial_id=1,
                        asset=rent_entities.asset.AssetCar(
                            car_id='car_id', car_copy_id='car_copy',
                        ),
                        charging=rent_entities.charging.ChargingDaily(
                            starts_at=datetime.datetime(
                                2020, 1, 1, tzinfo=datetime.timezone.utc,
                            ),
                            finishes_at=None,
                            total_withhold_limit=None,
                            daily_price=decimal.Decimal(10),
                            periodicity=periodicity.DailyPeriodicityFraction(
                                1, 3,
                            ),
                            time=datetime.time(0, 0),
                        ),
                    ),
                    car_info=car_stub_factory(),
                ),
                [
                    in_park.Expense(
                        timestamp=datetime.datetime(
                            2020, 1, 1, 10, 30, tzinfo=datetime.timezone.utc,
                        ),
                        amount=decimal.Decimal(10),
                    ),
                ],
            ),
            in_park.RentExpenses(
                in_park.OtherRentData(
                    rent=rent_stub_factory(
                        'record1',
                        owner_serial_id=1,
                        asset=rent_entities.asset.AssetOther(
                            subtype='phone', description='Описание',
                        ),
                        charging=rent_entities.charging.ChargingDaily(
                            starts_at=datetime.datetime(
                                2020, 1, 1, tzinfo=datetime.timezone.utc,
                            ),
                            finishes_at=None,
                            total_withhold_limit=None,
                            daily_price=decimal.Decimal(10),
                            periodicity=periodicity.DailyPeriodicityFraction(
                                1, 3,
                            ),
                            time=datetime.time(0, 0),
                        ),
                    ),
                ),
                [
                    in_park.Expense(
                        timestamp=datetime.datetime(
                            2020, 1, 1, 12, 10, tzinfo=datetime.timezone.utc,
                        ),
                        amount=decimal.Decimal(10),
                    ),
                ],
            ),
        ]
        return in_park.Result(
            currency='RUB',
            owner_park=park_stub_factory(id=park_id),
            driver_park=park_stub_factory(
                id=driver_id, driver_partner_source='selfemployed',
            ),
            expenses=res,
        )

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/in-park',
        params={
            'rent_park_id': 'park_id',
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-01T20:00+00:00',
            'tz': 'Europe/Moscow',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 200
    body = await response.json()
    assert body == load_json('single-date.json')


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
async def test_empty_md(
        patch, web_app_client, driver_auth_headers, park_stub_factory,
):
    @patch(
        'fleet_rent.use_cases.driver_expenses.in_park.'
        'DriverExpensesInPark.__call__',
    )
    async def _impl(park_id, driver_park_id, driver_id, begin_time, end_time):
        assert park_id == 'park_id'
        assert begin_time == dt.datetime.fromisoformat(
            '2020-01-01T00:00+00:00',
        )
        assert end_time == dt.datetime.fromisoformat('2020-01-06T00:00+00:00')
        assert driver_park_id == 'driver_park_id'
        assert driver_id == 'driver_id'
        return in_park.Result(
            currency='RUB',
            owner_park=park_stub_factory(id=park_id),
            driver_park=park_stub_factory(
                id=driver_id, driver_partner_source='selfemployed',
            ),
            expenses=[],
        )

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/in-park',
        params={
            'rent_park_id': 'park_id',
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-06T00:00+00:00',
            'tz': 'Europe/Moscow',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 200
    body = await response.json()
    assert body == {
        'ui': {
            'title': 'Парк \"ИмяПарка\"',
            'items': [
                {
                    'type': 'header',
                    'html': True,
                    'horizontal_divider_type': 'none',
                    'subtitle': '0,<small>00</small> <small>₽</small>',
                    'title': '1 янв. - 6 янв.',
                },
            ],
        },
        'begin_time': '2020-01-01T03:00:00+03:00',
        'end_time': '2020-01-06T03:00:00+03:00',
    }


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
async def test_empty_sd(
        patch, web_app_client, driver_auth_headers, park_stub_factory,
):
    @patch(
        'fleet_rent.use_cases.driver_expenses.in_park.'
        'DriverExpensesInPark.__call__',
    )
    async def _impl(park_id, driver_park_id, driver_id, begin_time, end_time):
        assert park_id == 'park_id'
        assert begin_time == dt.datetime.fromisoformat(
            '2020-01-01T00:00+00:00',
        )
        assert end_time == dt.datetime.fromisoformat('2020-01-01T20:00+00:00')
        assert driver_park_id == 'driver_park_id'
        assert driver_id == 'driver_id'
        return in_park.Result(
            currency='RUB',
            owner_park=park_stub_factory(id=park_id),
            driver_park=park_stub_factory(
                id=driver_id, driver_partner_source='selfemployed',
            ),
            expenses=[],
        )

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/in-park',
        params={
            'rent_park_id': 'park_id',
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-01T20:00+00:00',
            'tz': 'Europe/Moscow',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 200
    body = await response.json()
    assert body == {
        'ui': {
            'title': 'Парк \"ИмяПарка\"',
            'items': [
                {
                    'type': 'header',
                    'html': True,
                    'horizontal_divider_type': 'none',
                    'subtitle': '0,<small>00</small> <small>₽</small>',
                    'title': '1 января',
                },
            ],
        },
        'begin_time': '2020-01-01T03:00:00+03:00',
        'end_time': '2020-01-01T23:00:00+03:00',
    }


async def test_not_single_driver(patch, web_app_client, driver_auth_headers):
    @patch(
        'fleet_rent.use_cases.driver_expenses.in_park.'
        'DriverExpensesInPark.__call__',
    )
    async def _impl(park_id, driver_park_id, driver_id, begin_time, end_time):
        raise errors.NonSingleDriverPark()

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/in-park',
        params={
            'rent_park_id': 'park_id',
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-06T00:00+00:00',
            'tz': 'Europe/Moscow',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 400
    body = await response.json()
    assert body['code'] == 'NOT_SINGLE_DRIVER_PARK'


async def test_invalid_times(patch, web_app_client, driver_auth_headers):
    @patch(
        'fleet_rent.use_cases.driver_expenses.in_park.'
        'DriverExpensesInPark.__call__',
    )
    async def _impl(park_id, driver_park_id, driver_id, begin_time, end_time):
        raise errors.InvalidTimePrecision()

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/in-park',
        params={
            'rent_park_id': 'park_id',
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-06T00:00+00:00',
            'tz': 'Europe/Moscow',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 400
    body = await response.json()
    assert body['code'] == 'INVALID_TIME_PRECISION'


async def test_invalid_ranges(patch, web_app_client, driver_auth_headers):
    @patch(
        'fleet_rent.use_cases.driver_expenses.in_park.'
        'DriverExpensesInPark.__call__',
    )
    async def _impl(park_id, driver_park_id, driver_id, begin_time, end_time):
        raise errors.InvalidTimeRange()

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/in-park',
        params={
            'rent_park_id': 'park_id',
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-06T00:00+00:00',
            'tz': 'Europe/Moscow',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 400
    body = await response.json()
    assert body['code'] == 'INVALID_TIME_RANGE'


async def test_non_handleable(patch, web_app_client, driver_auth_headers):
    @patch(
        'fleet_rent.use_cases.driver_expenses.in_park.'
        'DriverExpensesInPark.__call__',
    )
    async def _impl(park_id, driver_park_id, driver_id, begin_time, end_time):
        raise errors.NonHandleableError()

    response = await web_app_client.post(
        '/driver/v1/periodic-payments/expenses/in-park',
        params={
            'rent_park_id': 'park_id',
            'begin_time': '2020-01-01T00:00+00:00',
            'end_time': '2020-01-06T00:00+00:00',
            'tz': 'Europe/Moscow',
        },
        headers={**driver_auth_headers, 'Accept-Language': 'ru'},
    )
    assert response.status == 500
