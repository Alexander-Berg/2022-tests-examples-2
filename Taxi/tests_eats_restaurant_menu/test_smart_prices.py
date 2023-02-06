import pytest

from . import util


@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.config(
    EATS_RESTAURANT_MENU_PLACES_CACHE_SETTINGS={
        'missed_revision_ttl': 1,
        'batch_size': 10,
    },
)
@pytest.mark.parametrize(
    'round_config',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_SMART_PRICES_ROUND={'enabled': True},
            ),
            id='turn_on_round_config',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                EATS_SMART_PRICES_ROUND={'enabled': False},
            ),
            id='turn_off_round_config',
        ),
    ],
)
@pytest.mark.parametrize(
    'dynamic_price',
    [
        pytest.param(
            True,
            marks=[
                util.dynamic_prices(10),
                pytest.mark.smart_prices_cache({'1': 100}),
            ],
            id='dynamic_prices_10_100',
        ),
        pytest.param(
            True,
            marks=[
                util.dynamic_prices(100),
                pytest.mark.smart_prices_cache({'1': 10}),
            ],
            id='dynamic_prices_100_10',
        ),
        pytest.param(
            False,
            marks=pytest.mark.smart_prices_cache({'1': 10}),
            id='dynamic_prices_off_by_exp',
        ),
        pytest.param(
            False,
            marks=util.dynamic_prices(10),
            id='dynamic_prices_off_by_service',
        ),
    ],
)
async def test_item_with_smart_prices(
        taxi_eats_restaurant_menu, dynamic_price, round_config,
):
    optionsgroups = [
        {
            'id': 10372250,
            'maxSelected': 2,
            'minSelected': 1,
            'name': 'Соус на выбор',
            'options': [
                {
                    'decimalPrice': '15.98',
                    'id': 1679268432,
                    'multiplier': 2,
                    'name': 'Сметана - 30 гр',
                    'price': 4,
                },
                {
                    'decimalPrice': '40.01',
                    'decimalPromoPrice': '20.01',
                    'id': 1679268437,
                    'multiplier': 2,
                    'name': 'Наршараб - 30 гр',
                    'price': 40,
                    'promoPrice': 20,
                },
            ],
            'required': True,
        },
    ]

    request = {
        'slug': 'test_slug',
        'payload': {
            'categories': [
                util.build_category(
                    category_id=1,
                    available=True,
                    items=[
                        util.build_item(
                            1, price=150.2, options_groups=optionsgroups,
                        ),
                    ],
                ),
                util.build_category(
                    category_id=2,
                    available=True,
                    items=[util.build_item(2, price=17, promo_price=15.01)],
                ),
                util.build_category(
                    category_id=3,
                    available=True,
                    items=[util.build_item(3, price=123)],
                ),
            ],
        },
    }
    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER,
        json=request,
        headers={'X-Eats-User': 'user_id=21'},
    )
    assert response.status_code == 200
    response_categories = response.json()['payload']['categories']

    if dynamic_price:
        item1 = response_categories[0]['items'][0]
        assert item1['decimalPrice'] == '165.2' if round_config else '165.22'
        assert item1['price'] == 165

        item3 = response_categories[2]['items'][0]
        assert item3['decimalPrice'] == '135' if round_config else '135.3'
        assert item3['price'] == 135
    else:
        item1 = response_categories[0]['items'][0]
        assert item1['decimalPrice'] == '150.2'
        assert item1['price'] == 150

        item3 = response_categories[2]['items'][0]
        assert item3['decimalPrice'] == '123'
        assert item3['price'] == 123

    item2 = response_categories[1]['items'][0]
    assert item2['decimalPrice'] == '17'
    assert item2['price'] == 17
    assert item2['decimalPromoPrice'] == '15.01'
    assert item2['promoPrice'] == 15


@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.config(
    EATS_RESTAURANT_MENU_PLACES_CACHE_SETTINGS={
        'missed_revision_ttl': 1,
        'batch_size': 10,
    },
)
@pytest.mark.parametrize(
    'round_config',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_SMART_PRICES_ROUND={'enabled': True},
            ),
            id='turn_on_round_config',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                EATS_SMART_PRICES_ROUND={'enabled': False},
            ),
            id='turn_off_round_config',
        ),
    ],
)
@pytest.mark.parametrize(
    'dynamic_price',
    [
        pytest.param(
            True,
            marks=[
                util.dynamic_prices(10),
                pytest.mark.smart_prices_cache({'1': 100}),
            ],
            id='dynamic_prices_10_100',
        ),
        pytest.param(
            True,
            marks=[
                util.dynamic_prices(100),
                pytest.mark.smart_prices_cache({'1': 10}),
            ],
            id='dynamic_prices_100_10',
        ),
        pytest.param(
            False,
            marks=pytest.mark.smart_prices_cache({'1': 10}),
            id='dynamic_prices_off_by_exp',
        ),
        pytest.param(
            False,
            marks=util.dynamic_prices(10),
            id='dynamic_prices_off_by_service',
        ),
    ],
)
async def test_search_item_with_smart_prices(
        taxi_eats_restaurant_menu, dynamic_price, round_config,
):
    optionsgroups = [
        {
            'id': 10372250,
            'maxSelected': 2,
            'minSelected': 1,
            'name': 'Соус на выбор',
            'options': [
                {
                    'decimalPrice': '15.98',
                    'id': 1679268432,
                    'multiplier': 2,
                    'name': 'Сметана - 30 гр',
                    'price': 4,
                },
                {
                    'decimalPrice': '40.01',
                    'decimalPromoPrice': '20.01',
                    'id': 1679268437,
                    'multiplier': 2,
                    'name': 'Наршараб - 30 гр',
                    'price': 40,
                    'promoPrice': 20,
                },
            ],
            'required': True,
        },
    ]

    request = {
        'slug': 'test_slug',
        'payload': [
            {
                'items': [
                    util.build_item(
                        1,
                        price=150.2,
                        options_groups=optionsgroups,
                        for_search=True,
                    ),
                ],
            },
            {
                'items': [
                    util.build_item(
                        2, price=17, promo_price=15.01, for_search=True,
                    ),
                ],
            },
            {'items': [util.build_item(3, price=123, for_search=True)]},
        ],
    }
    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_SEARCH_HANDLER,
        json=request,
        headers={'X-Eats-User': 'user_id=21'},
    )
    assert response.status_code == 200
    response_payload = response.json()['payload']

    if dynamic_price:
        item1 = response_payload[0]['items'][0]
        assert item1['decimalPrice'] == '165.2' if round_config else '165.22'
        assert item1['price'] == 165

        item3 = response_payload[2]['items'][0]
        assert item3['decimalPrice'] == '135' if round_config else '135.3'
        assert item3['price'] == 135
    else:
        item1 = response_payload[0]['items'][0]
        assert item1['decimalPrice'] == '150.2'
        assert item1['price'] == 150

        item3 = response_payload[2]['items'][0]
        assert item3['decimalPrice'] == '123'
        assert item3['price'] == 123

    item2 = response_payload[1]['items'][0]
    assert item2['decimalPrice'] == '17'
    assert item2['price'] == 17
    assert item2['decimalPromoPrice'] == '15.01'
    assert item2['promoPrice'] == 15
