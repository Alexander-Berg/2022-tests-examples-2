import decimal

import pytest

from fleet_rent.generated.web import web_context as wc
from fleet_rent.use_cases import driver_balance_by_park


@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'Will be withheld automatically': {
            'ru': 'Будет удержано автоматически',
        },
        'Park services': {'ru': 'Услуги парков'},
        'driver_internal_park_balance_negative': {
            'ru': 'Вы должны парку наличными',
        },
        'driver_internal_park_balance_positive': {
            'ru': 'Парк должен вам наличными',
        },
        'Park "{park_name}"': {'ru': 'Парк "{park_name}"'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'Москва'}},
)
@pytest.mark.now('2020-02-01T12:00:00')
async def test_balance_by_park(
        web_app_client, web_context: wc.Context, driver_auth_headers, patch,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_independent_driver_currency',
    )
    async def _get_external_currency(park_id: str, now):
        assert park_id == 'driver_park_id'
        return 'RUB'

    @patch('fleet_rent.use_cases.driver_balance_by_park.get_balances')
    async def _get_balances(
            context, driver_id: str, driver_park_id: str, currency: str,
    ):
        assert driver_id == 'driver_id'
        assert driver_park_id == 'driver_park_id'
        assert currency == 'RUB'
        return [
            driver_balance_by_park.ParkBalances(
                park_id='park_id1',
                park_name='Рога и Копыта',
                rent_balance=decimal.Decimal(-600),
                internal_balance=decimal.Decimal(-200),
            ),
            driver_balance_by_park.ParkBalances(
                park_id='park_id2',
                park_name='Лещ',
                rent_balance=decimal.Decimal(-300),
                internal_balance=decimal.Decimal(100),
            ),
        ]

    response = await web_app_client.get(
        '/driver/v1/periodic-payments/balance/by-park',
        headers=driver_auth_headers,
    )
    assert response.status == 200

    data = await response.json()

    assert data == {
        'title': 'Услуги парков',
        'items': [
            {
                'type': 'header',
                'horizontal_divider_type': 'none',
                'title': 'Будет удержано автоматически',
                'subtitle': '-900,<small>00</small> <small>₽</small>',
                'html': True,
            },
            {'type': 'title'},
            {
                'type': 'detail',
                'payload': {
                    'type': 'navigate_rent_balance_by_park',
                    'rent_park_id': 'park_id1',
                },
                'horizontal_divider_type': 'bottom_gap',
                'title': 'Парк "Рога и Копыта"',
                'right_icon': 'navigate',
                'accent': True,
                'primary_text_size': 'title_small',
            },
            {
                'type': 'detail',
                'horizontal_divider_type': 'bottom_gap',
                'title': 'Будет удержано автоматически',
                'detail': '-600,<small>00</small> <small>₽</small>',
                'html': True,
            },
            {
                'type': 'detail',
                'horizontal_divider_type': 'none',
                'title': 'Вы должны парку наличными',
                'detail': '-200,<small>00</small> <small>₽</small>',
                'html': True,
            },
            {'type': 'title'},
            {
                'type': 'detail',
                'payload': {
                    'type': 'navigate_rent_balance_by_park',
                    'rent_park_id': 'park_id2',
                },
                'horizontal_divider_type': 'bottom_gap',
                'title': 'Парк "Лещ"',
                'right_icon': 'navigate',
                'accent': True,
                'primary_text_size': 'title_small',
            },
            {
                'type': 'detail',
                'horizontal_divider_type': 'bottom_gap',
                'title': 'Будет удержано автоматически',
                'detail': '-300,<small>00</small> <small>₽</small>',
                'html': True,
            },
            {
                'type': 'detail',
                'horizontal_divider_type': 'none',
                'title': 'Парк должен вам наличными',
                'detail': '100,<small>00</small> <small>₽</small>',
                'html': True,
            },
        ],
    }


@pytest.mark.now('2020-02-01T12:00:00')
async def test_balance_by_park_no_parks(
        web_app_client, web_context: wc.Context, driver_auth_headers, patch,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_independent_driver_currency',
    )
    async def _get_independent_driver_currency(park_id: str, now):
        assert park_id == 'driver_park_id'
        return 'RUB'

    response = await web_app_client.get(
        '/driver/v1/periodic-payments/balance/by-park',
        headers=driver_auth_headers,
    )
    assert response.status == 200, response.text

    data = await response.json()
    assert data == {
        'title': 'Park services',
        'items': [
            {
                'type': 'header',
                'html': True,
                'horizontal_divider_type': 'none',
                'title': 'Will be withheld automatically',
                'subtitle': 'currency_with_sign.default',
            },
        ],
    }
