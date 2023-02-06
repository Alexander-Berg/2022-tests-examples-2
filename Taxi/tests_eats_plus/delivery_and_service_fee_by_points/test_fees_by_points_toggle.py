import pytest

from tests_eats_plus import conftest

SETTINGS_USE_EXP = {
    'handler_enabled': True,
    'use_experiment': False,
    'handler_default': {'title': 'Кешбек'},
}

SERVICES = [
    {'service_type': 'delivery', 'quantity': '1', 'cost': '100'},
    {'service_type': 'product', 'quantity': '1', 'cost': '100'},
    {'service_type': 'product', 'quantity': '1', 'cost': '100'},
    {'service_type': 'service_fee', 'quantity': '1', 'cost': '100'},
]

CASHBACK_INCOME = {
    'decimal_eda_part': '0',
    'decimal_full': '10',
    'decimal_place_part': '10',
    'eda_part': 0,
    'full': 10,
    'place_part': 10,
}


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP)
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
@pytest.mark.experiments3(filename='exp3_eats_plus_toggle.json')
@pytest.mark.parametrize(
    ['yandex_uid', 'balance', 'expected_response'],
    [
        pytest.param(
            '34567252',
            100,
            {
                'cashback': 10,
                'cashback_outcome': 100,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '100',
                'hide_cashback_income': False,
                'plus_toggle': {
                    'subtitle': 'У вас 100',
                    'title': [
                        {'text': 'Потратить '},
                        {
                            'styles': {'rainbow': True},
                            'text': '100 баллов Плюса',
                        },
                    ],
                },
                'title': 'Кешбек',
            },
            id='points < cashback outcome',
        ),
        pytest.param(
            '34567252',
            1000,
            {
                'cashback': 10,
                'cashback_outcome': 396,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '396',
                'hide_cashback_income': False,
                'plus_toggle': {
                    'subtitle': 'По 1 ₽ за товары, доставку и работу сервиса',
                    'title': [
                        {'text': 'Потратить '},
                        {
                            'styles': {'rainbow': True},
                            'text': '396 баллов Плюса',
                        },
                    ],
                },
                'title': 'Кешбек',
            },
            id=(
                'points >= cashback outcome '
                '(products + delivery + service fee)'
            ),
        ),
        pytest.param(
            '3456725',
            1000,
            {
                'cashback': 10,
                'cashback_outcome': 297,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '297',
                'hide_cashback_income': False,
                'plus_toggle': {
                    'subtitle': 'По 1 ₽ за товары и доставку',
                    'title': [
                        {'text': 'Потратить '},
                        {
                            'styles': {'rainbow': True},
                            'text': '297 баллов Плюса',
                        },
                    ],
                },
                'title': 'Кешбек',
            },
            id='points >= cashback outcome (products + delivery)',
        ),
        pytest.param(
            '34567251',
            1000,
            {
                'cashback': 10,
                'cashback_outcome': 297,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '297',
                'hide_cashback_income': False,
                'plus_toggle': {
                    'subtitle': 'По 1 ₽ за товары и работу сервиса',
                    'title': [
                        {'text': 'Потратить '},
                        {
                            'styles': {'rainbow': True},
                            'text': '297 баллов Плюса',
                        },
                    ],
                },
                'title': 'Кешбек',
            },
            id='points >= cashback outcome (products + service fee)',
        ),
        pytest.param(
            '123456',
            1000,
            {
                'cashback': 10,
                'cashback_outcome': 198,
                'decimal_cashback': '10',
                'decimal_cashback_outcome': '198',
                'hide_cashback_income': False,
                'plus_toggle': {
                    'subtitle': 'По 1 ₽ за товары',
                    'title': [
                        {'text': 'Потратить '},
                        {
                            'styles': {'rainbow': True},
                            'text': '198 баллов Плюса',
                        },
                    ],
                },
                'title': 'Кешбек',
            },
            id='points >= cashback outcome (only products)',
        ),
    ],
)
async def test_toggle_cart(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        yandex_uid,
        balance,
        expected_response,
):
    eats_order_stats(has_orders=True)
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': balance})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': yandex_uid,
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': SERVICES,
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == expected_response


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP)
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
@pytest.mark.experiments3(filename='exp3_eats_plus_toggle.json')
@pytest.mark.parametrize(
    ['yandex_uid', 'balance', 'expected_response'],
    [
        pytest.param(
            '34567252',
            100,
            {
                'cashback_income': CASHBACK_INCOME,
                'cashback_outcome': 100,
                'decimal_cashback_outcome': '100',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '100', 'service_type': 'product'},
                ],
                'has_plus': True,
                'plus_toggle': {
                    'subtitle': 'У вас 100',
                    'title': [
                        {'text': 'Потратить '},
                        {
                            'styles': {'rainbow': True},
                            'text': '100 баллов Плюса',
                        },
                    ],
                },
            },
            id='points < cashback outcome',
        ),
        pytest.param(
            '34567252',
            1000,
            {
                'cashback_income': CASHBACK_INCOME,
                'cashback_outcome': 396,
                'decimal_cashback_outcome': '396',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '198', 'service_type': 'product'},
                    {'cashback_outcome': '99', 'service_type': 'delivery'},
                    {'cashback_outcome': '99', 'service_type': 'service_fee'},
                ],
                'has_plus': True,
                'plus_toggle': {
                    'subtitle': 'По 1 ₽ за товары, доставку и работу сервиса',
                    'title': [
                        {'text': 'Потратить '},
                        {
                            'styles': {'rainbow': True},
                            'text': '396 баллов Плюса',
                        },
                    ],
                },
            },
            id=(
                'points >= cashback outcome '
                '(products + delivery + service fee)'
            ),
        ),
        pytest.param(
            '3456725',
            1000,
            {
                'cashback_income': CASHBACK_INCOME,
                'cashback_outcome': 297,
                'decimal_cashback_outcome': '297',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '198', 'service_type': 'product'},
                    {'cashback_outcome': '99', 'service_type': 'delivery'},
                ],
                'has_plus': True,
                'plus_toggle': {
                    'subtitle': 'По 1 ₽ за товары и доставку',
                    'title': [
                        {'text': 'Потратить '},
                        {
                            'styles': {'rainbow': True},
                            'text': '297 баллов Плюса',
                        },
                    ],
                },
            },
            id='points >= cashback outcome (products + delivery)',
        ),
        pytest.param(
            '34567251',
            1000,
            {
                'cashback_income': CASHBACK_INCOME,
                'cashback_outcome': 297,
                'decimal_cashback_outcome': '297',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '198', 'service_type': 'product'},
                    {'cashback_outcome': '99', 'service_type': 'service_fee'},
                ],
                'has_plus': True,
                'plus_toggle': {
                    'subtitle': 'По 1 ₽ за товары и работу сервиса',
                    'title': [
                        {'text': 'Потратить '},
                        {
                            'styles': {'rainbow': True},
                            'text': '297 баллов Плюса',
                        },
                    ],
                },
            },
            id='points >= cashback outcome (products + service fee)',
        ),
        pytest.param(
            '123456',
            1000,
            {
                'cashback_income': CASHBACK_INCOME,
                'cashback_outcome': 198,
                'decimal_cashback_outcome': '198',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '198', 'service_type': 'product'},
                ],
                'has_plus': True,
                'plus_toggle': {
                    'subtitle': 'По 1 ₽ за товары',
                    'title': [
                        {'text': 'Потратить '},
                        {
                            'styles': {'rainbow': True},
                            'text': '198 баллов Плюса',
                        },
                    ],
                },
            },
            id='points >= cashback outcome (only products)',
        ),
    ],
)
async def test_toggle_checkout(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        yandex_uid,
        balance,
        expected_response,
):
    eats_order_stats(has_orders=True)
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': balance})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': yandex_uid,
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': SERVICES,
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == expected_response
