import pytest

from tests_eats_plus import conftest

SETTINGS_USE_EXP = {
    'handler_enabled': True,
    'use_experiment': False,
    'handler_default': {'title': 'Кешбек'},
}


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP)
@pytest.mark.parametrize(
    ['yandex_uid', 'discount_info', 'balance', 'cashback', 'expected_code'],
    [
        (
            '3456725',
            {'is_old': False, 'has_plus': True},
            1000,
            {
                'cashback': 10,
                'cashback_outcome': 297,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '297',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
        ),
        (
            '34567251',
            {'is_old': False, 'has_plus': True},
            1000,
            {
                'cashback': 10,
                'cashback_outcome': 297,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '297',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
        ),
        (
            '34567252',
            {'is_old': False, 'has_plus': True},
            1000,
            {
                'cashback': 10,
                'cashback_outcome': 396,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '396',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
        ),
        (
            '3456725',
            {'is_old': True, 'has_plus': True},
            1000,
            {
                'cashback': 10,
                'cashback_outcome': 297,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '297',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
        ),
        (
            '3456725',
            {'is_old': True, 'has_plus': False},
            1000,
            {
                'cashback': 10,
                'cashback_outcome': 0,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '0',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
        ),
        (
            '3456725',
            {'is_old': False, 'has_plus': False},
            1000,
            {
                'cashback': 10,
                'cashback_outcome': 0,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '0',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
        ),
        (
            '3456725',
            {'is_old': True, 'has_plus': True},
            200,
            {
                'cashback': 10,
                'cashback_outcome': 200,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '200',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
        ),
        (
            '34567251',
            {'is_old': True, 'has_plus': True},
            200,
            {
                'cashback': 10,
                'cashback_outcome': 200,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '200',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
        ),
        (
            '34567252',
            {'is_old': True, 'has_plus': True},
            200,
            {
                'cashback': 10,
                'cashback_outcome': 200,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '200',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
        ),
        (
            '3456726',
            {'is_old': True, 'has_plus': True},
            1000,
            {
                'cashback': 10,
                'cashback_outcome': 198,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '198',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
        ),
        (
            '3456726',
            {'is_old': True, 'has_plus': False},
            1100,
            {
                'cashback': 10,
                'cashback_outcome': 0,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '0',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': 'offer_0',
            'place_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '5.0',
                    'maximum_discount': '99999',
                },
            },
        },
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_delivery_and_service_fee_by_points.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
async def test_cashback_cart_delivery_by_points(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        yandex_uid,
        discount_info,
        expected_code,
        balance,
        cashback,
):
    eats_order_stats(has_orders=discount_info['is_old'])
    passport_blackbox(has_plus=discount_info['has_plus'], has_cashback=True)
    plus_wallet({'RUB': balance})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': yandex_uid,
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100'},
                {'service_type': 'product', 'quantity': '1', 'cost': '100'},
                {'service_type': 'product', 'quantity': '1', 'cost': '100'},
                {
                    'service_type': 'service_fee',
                    'quantity': '1',
                    'cost': '100',
                },
            ],
        },
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        response = response.json()
        assert response == cashback


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP)
@pytest.mark.parametrize(
    ['yandex_uid', 'discount_info', 'cashback', 'expected_code'],
    [
        pytest.param(
            '3456725',
            {'is_old': False, 'has_plus': True},
            {
                'cashback': 0,
                'cashback_outcome': 99,
                'decimal_cashback': '0',
                'decimal_cashback_outcome': '99',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
            id='plus user; only delivery',
        ),
        pytest.param(
            '34567251',
            {'is_old': False, 'has_plus': True},
            {
                'cashback': 0,
                'cashback_outcome': 99,
                'decimal_cashback': '0',
                'decimal_cashback_outcome': '99',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
            id='plus user; only service fee',
        ),
        pytest.param(
            '34567252',
            {'is_old': False, 'has_plus': True},
            {
                'cashback': 0,
                'cashback_outcome': 198,
                'decimal_cashback': '0',
                'decimal_cashback_outcome': '198',
                'hide_cashback_income': False,
                'title': 'Кешбек',
            },
            200,
            id='plus user; delivery and service fee',
        ),
        pytest.param(
            '34567253',
            {'is_old': False, 'has_plus': True},
            None,
            204,
            id='plus user; without outcome',
        ),
        pytest.param(
            '3456725',
            {'is_old': False, 'has_plus': False},
            None,
            204,
            id='non plus user; without outcome',
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match([])
@pytest.mark.experiments3(
    filename='exp3_eats_plus_delivery_and_service_fee_by_points.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_spend_in_non_plus_places.json',
)
async def test_cashback_cart_delivery_by_points_in_non_plus_places(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        yandex_uid,
        discount_info,
        expected_code,
        cashback,
):
    eats_order_stats(has_orders=discount_info['is_old'])
    passport_blackbox(has_plus=discount_info['has_plus'], has_cashback=True)
    plus_wallet({'RUB': 1000})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': yandex_uid,
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100'},
                {'service_type': 'product', 'quantity': '1', 'cost': '100'},
                {'service_type': 'product', 'quantity': '1', 'cost': '100'},
                {
                    'service_type': 'service_fee',
                    'quantity': '1',
                    'cost': '100',
                },
            ],
        },
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        response = response.json()
        assert response == cashback
