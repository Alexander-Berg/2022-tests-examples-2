import pytest

from tests_eats_plus import conftest

# supposed to differ from default config only in mode


@pytest.mark.config(
    EATS_PLUS_ORDER_STATS_SETTINGS={
        'fallback_order_stats': {
            'default_brand_orders_count': 0,
            'default_place_orders_count': 0,
            'is_first_order': False,
            'orders_count': 1,
        },
        'mode': 'first_order_always_false_no_counters',
    },
)
@pytest.mark.experiments3(filename='exp3_discounts_plus_toggle.json')
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_plus_toggle_cart_happy_path(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 780})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '500.0',
                    'public_id': 'coke',
                },
            ],
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert 'plus_toggle' in response
    assert response['plus_toggle'] == {
        'subtitle': 'Всего 780',
        'title': [
            {'text': 'Списать'},
            {'styles': {'rainbow': True}, 'text': '497'},
        ],
    }


# supposed to differ from default config only in mode
@pytest.mark.config(
    EATS_PLUS_ORDER_STATS_SETTINGS={
        'fallback_order_stats': {
            'default_brand_orders_count': 0,
            'default_place_orders_count': 0,
            'is_first_order': False,
            'orders_count': 1,
        },
        'mode': 'first_order_always_false_no_counters',
    },
)
@pytest.mark.experiments3(filename='exp3_discounts_plus_toggle.json')
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_plus_toggle_cart_zero_balance(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 0})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '500.0',
                    'public_id': 'coke',
                },
            ],
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert 'plus_toggle' not in response


# supposed to differ from default config only in mode
@pytest.mark.config(
    EATS_PLUS_ORDER_STATS_SETTINGS={
        'fallback_order_stats': {
            'default_brand_orders_count': 0,
            'default_place_orders_count': 0,
            'is_first_order': False,
            'orders_count': 1,
        },
        'mode': 'first_order_always_false_no_counters',
    },
)
@pytest.mark.experiments3(filename='exp3_discounts_plus_toggle.json')
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_plus_toggle_cart_no_plus(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=False, has_cashback=False)
    plus_wallet({'RUB': 1000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '500.0',
                    'public_id': 'coke',
                },
            ],
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert 'plus_toggle' not in response


# supposed to differ from default config only in mode
@pytest.mark.config(
    EATS_PLUS_ORDER_STATS_SETTINGS={
        'fallback_order_stats': {
            'default_brand_orders_count': 0,
            'default_place_orders_count': 0,
            'is_first_order': False,
            'orders_count': 1,
        },
        'mode': 'first_order_always_false_no_counters',
    },
)
@pytest.mark.experiments3(filename='exp3_discounts_plus_toggle.json')
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_discounts_match([])
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_plus_toggle_cart_cannot_spend(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '2', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '500.0',
                    'public_id': 'coke',
                },
            ],
        },
    )
    assert response.status_code == 204


@pytest.mark.parametrize(
    'cost, expected_toggle',
    [
        (
            500,
            {
                'subtitle': 'Всего 363636',
                'title': [
                    {'text': 'Списать '},
                    {
                        'styles': {'rainbow': True},
                        'text': 'Потратить 499 баллов Плюса',
                    },
                ],
            },
        ),
        (
            495,
            {
                'subtitle': 'Всего 363636',
                'title': [
                    {'text': 'Списать '},
                    {
                        'styles': {'rainbow': True},
                        'text': 'Потратить 494 балла Плюса',
                    },
                ],
            },
        ),
        (
            492,
            {
                'subtitle': 'Всего 363636',
                'title': [
                    {'text': 'Списать '},
                    {
                        'styles': {'rainbow': True},
                        'text': 'Потратить 491 балл Плюса',
                    },
                ],
            },
        ),
        (
            500.5,
            {
                'subtitle': 'Всего 363636',
                'title': [
                    {'text': 'Списать '},
                    {
                        'styles': {'rainbow': True},
                        'text': 'Потратить 499.5 балла Плюса',
                    },
                ],
            },
        ),
    ],
)
# supposed to differ from default config only in mode
@pytest.mark.config(
    EATS_PLUS_ORDER_STATS_SETTINGS={
        'fallback_order_stats': {
            'default_brand_orders_count': 0,
            'default_place_orders_count': 0,
            'is_first_order': False,
            'orders_count': 1,
        },
        'mode': 'first_order_always_false_no_counters',
    },
)
@pytest.mark.experiments3(filename='exp3_discounts_plus_toggle.json')
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_plus_toggle_cart_pluralization(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        cost,
        expected_toggle,
        taxi_config,
        eats_order_stats,
):
    taxi_config.set_values(
        {
            'EATS_PLUS_ROUNDING_AND_PRECISION_BY_CURRENCY_V2': {
                'RUB': {
                    'display_precision': 1,
                    'income_round_policy': 'half_up_round_policy',
                    'income_precision': 1,
                    'outcome_precision': 1,  # to test fractional pluralization
                },
            },
        },
    )

    passport_blackbox(has_plus=True, has_cashback=True)
    # specific balance causes experiment to return
    # tanker toggle
    plus_wallet({'RUB': 363636})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '1',
                    'cost': str(cost),
                    'public_id': 'coke',
                },
            ],
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert 'plus_toggle' in response
    assert response['plus_toggle'] == expected_toggle
