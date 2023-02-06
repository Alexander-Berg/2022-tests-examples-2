import pytest

from tests_eats_plus import conftest

SETTINGS_USE_HANDLER = {
    'handler_enabled': True,
    'use_experiment': False,
    'handler_default': {'title': 'А тут у нас кешбек'},
}

SETTINGS_USE_EXP = {
    'handler_enabled': True,
    'use_experiment': True,
    'handler_default': {'title': 'А тут у нас кешбек'},
}


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_HANDLER)
@pytest.mark.parametrize(
    [
        'cashback_income',
        'cashback_outcome',
        'decimal_cashback_income',
        'decimal_cashback_outcome',
        'total_services_cost',
    ],
    [
        pytest.param(
            500,
            1997,
            '500',
            '1997',
            None,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
                    [
                        {
                            'subquery_id': 'offer_0',
                            'place_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '25.0',
                                    'maximum_discount': '1234',
                                },
                            },
                        },
                    ],
                ),
            ],
            id='place cahback only',
        ),
        pytest.param(
            350,
            1997,
            '350',
            '1997',
            None,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
                    [
                        {
                            'subquery_id': 'offer_0',
                            'place_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '25.0',
                                    'maximum_discount': '1234',
                                },
                            },
                        },
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
                    ],
                ),
            ],
            id='menu cashback for one product',
        ),
        pytest.param(
            500,
            1997,
            '500',
            '1997',
            None,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback_off.json',
                ),
                pytest.mark.eats_discounts_match(
                    [
                        {
                            'subquery_id': 'offer_0',
                            'place_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '25.0',
                                    'maximum_discount': '1234',
                                },
                            },
                        },
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
                    ],
                ),
            ],
            id='menu cashback disabled',
        ),
        pytest.param(
            500,
            1997,
            '500',
            '1997',
            None,
            marks=[
                pytest.mark.eats_discounts_match(
                    [
                        {
                            'subquery_id': 'offer_0',
                            'place_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '25.0',
                                    'maximum_discount': '1234',
                                },
                            },
                        },
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
                    ],
                ),
            ],
            id='experiment not found',
        ),
        pytest.param(
            150,
            0,
            '150',
            '0',
            None,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
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
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '5.0',
                                    'maximum_discount': '1234',
                                },
                            },
                        },
                    ],
                ),
            ],
            id='menu cashback from different hierarchy for products',
        ),
        pytest.param(
            200,
            0,
            '200',
            '0',
            None,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
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
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '5.0',
                                    'maximum_discount': '1234',
                                },
                            },
                            'yandex_menu_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '10.0',
                                    'maximum_discount': '1234',
                                },
                            },
                        },
                    ],
                ),
            ],
            id='choose the best menu cashback',
        ),
        pytest.param(
            150,
            0,
            '150',
            '0',
            None,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
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
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '5.0',
                                    'maximum_discount': '1234',
                                },
                            },
                            'yandex_menu_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '10.0',
                                    'maximum_discount': '10',
                                },
                            },
                        },
                        # применяется кэшбек с меньшим % из-за
                        # maximum_discount
                    ],
                ),
            ],
            id='choose the best available cashback',
        ),
        pytest.param(
            200,
            0,
            '200',
            '0',
            None,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
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
                                'menu_value': {
                                    'value_type': 'absolute',
                                    'value': '50.0',
                                },
                            },
                        },
                    ],
                ),
            ],
            id='absolute cashback',
        ),
        pytest.param(
            200,
            0,
            '200',
            '0',
            None,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
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
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '20.0',
                                    'maximum_discount': '50',
                                },
                            },
                        },
                    ],
                ),
            ],
            id='check max_cashback',
        ),
        pytest.param(
            67,
            0,
            '67',
            # decimal rounding is null_round_policy,
            # and the actual cashback outcome is 896.5,
            # so both floor to 896
            '0',
            '1000',
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
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
                            'yandex_menu_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '5.0',
                                    'maximum_discount': '1234',
                                },
                            },
                        },
                    ],
                ),
            ],
            id='menu cashback with promocode',
        ),
        pytest.param(
            145,
            0,
            '145',
            # decimal rounding is null_round_policy,
            # and the actual cashback outcome is 896.5,
            # so both floor to 896
            '0',
            '1000',
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
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
                                'menu_value': {
                                    'value_type': 'absolute',
                                    'value': '50.0',
                                },
                            },
                        },
                    ],
                ),
            ],
            id='absolute cashback with promocode',
        ),
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_cashback_cart_eats_discounts_set_cashback(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        eats_discounts_match,
        cashback_income,
        cashback_outcome,
        decimal_cashback_income,
        decimal_cashback_outcome,
        total_services_cost,
):
    eats_order_stats(has_orders=False)
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '34567257',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'total_cost': total_services_cost,
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '1',
                    'cost': '1000.0',
                    'public_id': '101',
                },
                {
                    'service_type': 'product',
                    'quantity': '2',
                    'cost': '1000.0',
                    'public_id': '102',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'cashback': cashback_income,
        'cashback_outcome': cashback_outcome,
        'decimal_cashback': decimal_cashback_income,
        'decimal_cashback_outcome': decimal_cashback_outcome,
        'hide_cashback_income': False,
        'title': 'А тут у нас кешбек',
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_HANDLER)
@pytest.mark.eats_discounts_match([])
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_cashback_cart_eats_discounts_no_cashback(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        eats_discounts_match,
):
    eats_order_stats(has_orders=False)
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '34567257',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'total_cost': None,
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '1',
                    'cost': '1000.0',
                    'public_id': '101',
                },
                {
                    'service_type': 'product',
                    'quantity': '2',
                    'cost': '1000.0',
                    'public_id': '102',
                },
            ],
        },
    )

    assert response.status_code == 204


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': '1',
            'yandex_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '20.0',
                    'maximum_discount': '1000',
                },
            },
        },
    ],
)
@pytest.mark.experiments3(filename='exp3_eats_plus_menu_cashback.json')
@pytest.mark.config(
    EATS_PLUS_EATS_DISCOUNTS_REQUEST_SETTINGS={
        'max_places_in_request': 1,
        'services_offers_tasks_count': 2,
    },
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_cashback_cart_bulk_discounts(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback-bulk',
        json={
            'yandex_uid': '34567257',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'shipping_type': 'delivery',
            'services_offers': [
                {
                    'id': 1,
                    'services': [
                        {
                            'service_type': 'delivery',
                            'quantity': '1',
                            'cost': '100',
                        },
                        {
                            'service_type': 'product',
                            'quantity': '1',
                            'cost': '1500',
                            'public_id': 'coke',
                        },
                    ],
                    'total_cost': '1600',
                },
                {
                    'id': 2,
                    'services': [
                        {
                            'service_type': 'delivery',
                            'quantity': '1',
                            'cost': '1500',
                        },
                        {
                            'service_type': 'product',
                            'quantity': '1',
                            'cost': '1500',
                            'public_id': 'coke',
                        },
                    ],
                    'total_cost': '3000',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert (
        sorted(
            response.json()['cashback_offers'], key=lambda offer: offer['id'],
        )
        == [
            {
                'id': 1,
                'cashback_offer': {
                    'cashback': 300,
                    'decimal_cashback': '300',
                    'cashback_outcome': 1499,
                    'decimal_cashback_outcome': '1499',
                    'title': '',
                },
            },
            {
                'id': 2,
                'cashback_offer': {
                    'cashback': 300,
                    'decimal_cashback': '300',
                    'cashback_outcome': 1499,
                    'decimal_cashback_outcome': '1499',
                    'title': '',
                },
            },
        ]
    )


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP)
@pytest.mark.parametrize(
    ['title_and_description'],
    [
        pytest.param(
            {
                'title': 'Вы получите целых 25% за этот заказ!',
                'description': 'Потому что сматчилась акция Плюса',
            },
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
                    [
                        {
                            'subquery_id': 'offer_0',
                            'place_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '25.0',
                                    'maximum_discount': '1234',
                                },
                            },
                        },
                    ],
                ),
            ],
            id='Plus promo text overrides base one',
        ),
        pytest.param(
            {'title': 'Смотри какой кешбек'},
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
                    [
                        {
                            'subquery_id': '0_plus_first_orders',
                            'place_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '25.0',
                                    'maximum_discount': '1234',
                                },
                            },
                        },
                    ],
                ),
            ],
            id='No Plus promo text in exp, so falling back to base',
        ),
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cart_cashback_with_plus_promos.json',
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_cashback_cart_eats_discounts_override_text_if_plus_promo(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        eats_discounts_match,
        title_and_description,
):
    eats_order_stats(has_orders=False)
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '34567257',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'total_cost': None,
            'services': [
                {
                    'service_type': 'product',
                    'quantity': '1',
                    'cost': '1000.0',
                    'public_id': '101',
                },
            ],
        },
    )

    expected_response = {
        'cashback': 250,
        'cashback_outcome': 999,
        'decimal_cashback': '250',
        'decimal_cashback_outcome': '999',
        'hide_cashback_income': False,
    }

    expected_response.update(title_and_description)

    assert response.status_code == 200
    assert response.json() == expected_response
