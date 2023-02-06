import pytest


CATALOG_STORAGE_DATA = [
    {
        'id': 1,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
        'country': {
            'id': 1,
            'code': 'abc',
            'name': 'USSR',
            'currency': {'sign': '$', 'code': 'RUB'},
        },
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'categories': [{'id': 1, 'name': 'some_name'}],
        'business': 'store',
        'type': 'marketplace',
    },
]


@pytest.mark.parametrize(
    ['eda_part', 'place_part', 'outcome'],
    [
        pytest.param(
            300,
            200,
            120,
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
                                    'value': '10.0',
                                    'maximum_discount': '1234',
                                },
                            },
                            'yandex_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '15.0',
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
            0,
            350,
            120,
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
            0,
            500,
            120,
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
            0,
            500,
            120,
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
            0,
            150,
            0,
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
            100,
            100,
            0,
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
            0,
            150,
            0,
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
            0,
            200,
            0,
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
            0,
            200,
            0,
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
            200,
            0,
            120,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
                    [
                        {
                            'subquery_id': 'offer_0',
                            'yandex_cashback': {
                                'menu_value': {
                                    'value_type': 'absolute',
                                    'value': '200.0',
                                },
                            },
                        },
                    ],
                ),
            ],
            id='absolute cashback for order',
        ),
        pytest.param(
            200,
            200,
            120,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
                    [
                        {
                            'subquery_id': 'offer_0',
                            'yandex_cashback': {
                                'menu_value': {
                                    'value_type': 'absolute',
                                    'value': '200.0',
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
            id='absolute cashback for order and other',
        ),
        pytest.param(
            200,
            150,
            120,
            marks=[
                pytest.mark.experiments3(
                    filename='exp3_eats_plus_menu_cashback.json',
                ),
                pytest.mark.eats_discounts_match(
                    [
                        {
                            'subquery_id': 'offer_0',
                            'yandex_cashback': {
                                'menu_value': {
                                    'value_type': 'absolute',
                                    'value': '200.0',
                                },
                            },
                            'place_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '5.0',
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
            id='different cashback test',
        ),
    ],
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_catalog_storage_cache(CATALOG_STORAGE_DATA)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
async def test_cashback_checkout_eats_discounts_set_cashback(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_discounts_match,
        eda_part,
        place_part,
        outcome,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 120})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'is_first_order': True,
            'yandex_uid': '34567257',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
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
    expected_response = {
        'cashback_income': {
            'eda_part': eda_part,
            'full': place_part + eda_part,
            'place_part': place_part,
            'decimal_eda_part': str(eda_part),
            'decimal_full': str(place_part + eda_part),
            'decimal_place_part': str(place_part),
        },
        'cashback_outcome': outcome,
        'decimal_cashback_outcome': str(outcome),
        'hide_cashback_income': False,
        'has_plus': True,
    }
    if outcome:
        expected_response['cashback_outcome_details'] = [
            {'cashback_outcome': str(outcome), 'service_type': 'product'},
        ]
    assert response.json() == expected_response


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_catalog_storage_cache(CATALOG_STORAGE_DATA)
@pytest.mark.eats_discounts_match([])
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
async def test_cashback_checkout_eats_discounts_no_cashback(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_discounts_match,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 120})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'is_first_order': True,
            'yandex_uid': '34567257',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
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

    assert response.status_code == 404
