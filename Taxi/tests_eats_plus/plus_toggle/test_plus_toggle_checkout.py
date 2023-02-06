import pytest

from tests_eats_plus import configs
from tests_eats_plus import conftest


@pytest.mark.experiments3(filename='exp3_discounts_plus_toggle.json')
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_plus_toggle_checkout_happy_path(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 780})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
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


@pytest.mark.config(
    EATS_PLUS_ROUNDING_AND_PRECISION_BY_CURRENCY_V2={
        'RUB': {
            'display_precision': 1,
            'income_round_policy': 'half_up_round_policy',
            'income_precision': 1,
            'outcome_precision': 1,
        },
    },
)
@pytest.mark.experiments3(filename='exp3_discounts_plus_toggle_float.json')
@pytest.mark.parametrize(
    'wallet_params, plus_toggle_in_response, toggle_response',
    [
        pytest.param(
            {'RUB': 0.1},
            True,
            {
                'subtitle': 'Всего 0.1',
                'title': [
                    {'text': 'Списать'},
                    {'styles': {'rainbow': True}, 'text': '0.1'},
                ],
            },
        ),
        pytest.param({'RUB': 0.0}, False, {}),
    ],
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_plus_toggle_float_checkout(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        wallet_params,
        plus_toggle_in_response,
        toggle_response,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet(wallet_params)
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
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
    if plus_toggle_in_response:
        assert 'plus_toggle' in response
        assert response['plus_toggle'] == toggle_response
    else:
        assert 'plus_toggle' not in response


@pytest.mark.experiments3(filename='exp3_discounts_plus_toggle.json')
@configs.EATS_PLUS_ENABLED_CURRENCIES
@configs.EATS_PLUS_CURRENCY_FOR_PLUS
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_plus_toggle_checkout_happy_path_byn(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 0, 'BYN': 780})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'BYN',
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


@pytest.mark.experiments3(filename='exp3_discounts_plus_toggle.json')
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_plus_toggle_checkout_zero_balance(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 0})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
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


@pytest.mark.experiments3(filename='exp3_discounts_plus_toggle.json')
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_plus_toggle_checkout_no_plus(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=False)
    plus_wallet({'RUB': 1000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
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


@pytest.mark.eats_discounts_match([])
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.experiments3(filename='exp3_discounts_plus_toggle.json')
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_plus_toggle_checkout_place_can_not_spend(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 780})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
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
    assert response.status_code == 404


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
async def test_plus_toggle_checkout_pluralization(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        taxi_config,
        cost,
        expected_toggle,
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
    plus_wallet({'RUB': 363636})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
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
