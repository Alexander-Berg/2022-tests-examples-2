import pytest

from tests_eats_plus import conftest

SETTINGS_USE_EXP = {
    'handler_enabled': True,
    'use_experiment': False,
    'handler_default': {'title': 'А тут у нас кешбек'},
}


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(
    EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP,
    EATS_PLUS_WEIGHTED_PRODUCTS_QUANTITY={'income': True, 'outcome': True},
)
@pytest.mark.experiments3(filename='exp3_eats_plus_menu_cashback.json')
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': '101',
            'place_menu_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '10.0',
                    'maximum_discount': '1234',
                },
            },
        },
        {
            'subquery_id': '102',
            'place_menu_cashback': {
                'menu_value': {'value_type': 'absolute', 'value': '50.0'},
            },
        },
    ],
)
async def test_weighted_products_checkout(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '500',
                    'is_catch_weight': True,
                    'public_id': '101',
                },
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '400',
                    'is_catch_weight': True,
                    'public_id': '102',
                },
            ],
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback_income': {
            'decimal_eda_part': '0',
            'decimal_full': '100',
            'decimal_place_part': '100',
            'eda_part': 0,
            'full': 100,
            'place_part': 100,
        },
        'cashback_outcome': 0,
        'decimal_cashback_outcome': '0',
        'hide_cashback_income': False,
        'has_plus': True,
    }
