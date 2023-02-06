import pytest

from tests_eats_plus import conftest

MATCH_DISCOUNTS_RESPONSE = [
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
]

SERVICES = [
    {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
    {
        'service_type': 'product',
        'quantity': '3',
        'cost': '312.0',
        'public_id': 'coke',
    },
    {'service_type': 'product', 'quantity': '1', 'cost': '400.0'},
    {'service_type': 'product', 'quantity': '2', 'cost': '500.0'},
]


@pytest.mark.parametrize(
    'order_id, response_code, expected_response',
    [
        pytest.param(
            'order_disc',
            200,
            {
                'cashback_income': {
                    'decimal_eda_part': '0',
                    'decimal_full': '303',
                    'decimal_place_part': '303',
                    'eda_part': 0,
                    'full': 303,
                    'place_part': 303,
                },
                'cashback_outcome': 1206,
                'decimal_cashback_outcome': '1206',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '1206', 'service_type': 'product'},
                ],
                'has_plus': True,
            },
            id='cashback from eats discounts',
        ),
        pytest.param(
            'order_cashcorr',
            200,
            {
                'cashback_income': {
                    'decimal_eda_part': '121',
                    'decimal_full': '363',
                    'decimal_place_part': '242',
                    'eda_part': 121,
                    'full': 363,
                    'place_part': 242,
                },
                'cashback_outcome': 1206,
                'decimal_cashback_outcome': '1206',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '1206', 'service_type': 'product'},
                ],
                'has_plus': True,
            },
            id='cashback from cashback corrections',
        ),
        pytest.param('order_nocashback', 404, None, id='no cashback'),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source_order_id.json',
)
@pytest.mark.experiments3(filename='exp3_eats_plus_cashback_corrections.json')
@pytest.mark.eats_discounts_match(MATCH_DISCOUNTS_RESPONSE)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_checkout_cashback_source(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        order_id,
        response_code,
        expected_response,
):

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 2812})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '34567259',
            'order_id': order_id,
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': SERVICES,
        },
    )

    assert response.status_code == response_code
    if response.status_code == 200:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    'yandex_uid, response_code, expected_response',
    [
        pytest.param(
            '1',
            200,
            {
                'cashback': 303,
                'cashback_outcome': 1206,
                'decimal_cashback': '303',
                'decimal_cashback_outcome': '1206',
                'hide_cashback_income': False,
                'title': '',
            },
            id='cashback from eats discounts',
        ),
        pytest.param(
            '2',
            200,
            {
                'cashback': 363,
                'cashback_outcome': 1206,
                'decimal_cashback': '363',
                'decimal_cashback_outcome': '1206',
                'hide_cashback_income': False,
                'title': '',
            },
            id='cashback from cashback corrections',
        ),
        pytest.param('3', 204, None, id='no cashback'),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source_order_id.json',
)
@pytest.mark.experiments3(filename='exp3_eats_plus_cashback_corrections.json')
@pytest.mark.eats_discounts_match(MATCH_DISCOUNTS_RESPONSE)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_cart_cashback_source(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        yandex_uid,
        response_code,
        expected_response,
):

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 2812})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': yandex_uid,
            'order_id': 'order_id',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': SERVICES,
        },
    )

    assert response.status_code == response_code
    if response.status_code == 200:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    'yandex_uid, response_code, expected_response',
    [
        pytest.param(
            '1',
            200,
            {'cashback': 25, 'title': 'Смотри какой кешбек'},
            id='cashback from eats discounts',
        ),
        pytest.param(
            '2',
            200,
            {'cashback': 30, 'title': 'Смотри какой кешбек'},
            id='cashback from cashback corrections',
        ),
        pytest.param('3', 404, None, id='no cashback'),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source_order_id.json',
)
@pytest.mark.experiments3(filename='exp3_eats_plus_cashback_corrections.json')
@pytest.mark.experiments3(
    filename='exp3_eats_plus_place_cashback_presentation.json',
)
@pytest.mark.eats_discounts_match(MATCH_DISCOUNTS_RESPONSE)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_slug_cashback_source(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        yandex_uid,
        response_code,
        expected_response,
):

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 2812})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/place',
        json={'yandex_uid': yandex_uid, 'place_id': 1},
    )

    assert response.status_code == response_code
    if response.status_code == 200:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    'yandex_uid, response_code, expected_response',
    [
        pytest.param(
            '1',
            200,
            {
                'cashback': [
                    {'cashback': 25.0, 'place_id': 1},
                    {'cashback': 25.0, 'place_id': 2},
                    {'cashback': 25.0, 'place_id': 3},
                ],
            },
            id='cashback from eats discounts',
        ),
        pytest.param(
            '2',
            200,
            {
                'cashback': [
                    {'cashback': 30.0, 'place_id': 1},
                    {'cashback': 30.0, 'place_id': 2},
                    {'cashback': 30.0, 'place_id': 3},
                ],
            },
            id='cashback from cashback corrections',
        ),
        pytest.param('3', 200, {'cashback': []}, id='no cashback'),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source_order_id.json',
)
@pytest.mark.experiments3(filename='exp3_eats_plus_cashback_corrections.json')
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': '1',
            'place_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '25.0',
                    'maximum_discount': '1234',
                },
            },
        },
        {
            'subquery_id': '2',
            'place_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '25.0',
                    'maximum_discount': '1234',
                },
            },
        },
        {
            'subquery_id': '3',
            'place_cashback': {
                'menu_value': {
                    'value_type': 'fraction',
                    'value': '25.0',
                    'maximum_discount': '1234',
                },
            },
        },
    ],
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_catalog_cashback_source(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        yandex_uid,
        response_code,
        expected_response,
):

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 2812})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        json={'yandex_uid': yandex_uid, 'place_ids': [1, 2, 3]},
    )

    assert response.status_code == response_code
    if response.status_code == 200:
        assert response.json() == expected_response
