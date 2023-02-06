import pytest

from tests_eats_restaurant_menu import util


@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.config(
    EATS_RESTAURANT_MENU_PLACES_CACHE_SETTINGS={
        'missed_revision_ttl': 1,
        'batch_size': 10,
    },
)
@util.discounts_applicator_enabled()
@util.promo_category_enabled()
@pytest.mark.parametrize(
    'discounts',
    [
        pytest.param(False, id='discounts_disabled'),
        pytest.param(
            True,
            marks=util.discounts_applicator_menu(),
            id='discount_enabled',
        ),
    ],
)
async def test_item_with_discounts(
        taxi_eats_restaurant_menu, discounts, eats_discounts_applicator,
):
    eats_discounts_applicator.mock_eats_tags = [
        'tag1',
        '2tag',
        '3tag3',
        '1234',
    ]
    if discounts:
        eats_discounts_applicator.add_menu_discount(
            item_id='1',
            discount_id='1',
            value_type='fraction',
            value='10',
            name='Скидка деньгами',
            description='item discount',
            picture_uri='some_uri',
        )
        eats_discounts_applicator.add_restaurant_menu_discounts(
            item_id='10',
            discount_id='2',
            value='5.0',
            name='Скидка деньгами от ресторана',
            description='restaurant item discount',
            picture_uri='another_uri',
        )
        eats_discounts_applicator.add_product_discount(
            item_id='3',
            discount_id='3',
            bundle=2,
            value='100',
            name='1+1',
            description='Второе блюдо в подарок',
            picture_uri='some_uri',
        )

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
                    'decimalPrice': '10.00',
                    'id': 1679268437,
                    'multiplier': 2,
                    'name': 'Наршараб - 30 гр',
                    'price': 40,
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
                    items=[util.build_item(2, price=17)],
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
    categories = response.json()['payload']['categories']

    if discounts:
        assert categories[1]['items'][0]['decimalPromoPrice'] == '135.18'
        assert categories[1]['items'][0]['promoPrice'] == 136
        assert categories[1]['items'][0]['promoTypes'] == [
            {'id': 100, 'name': 'Скидка деньгами', 'pictureUri': 'some_uri'},
        ]
        assert categories[3]['items'][0]['promoTypes'] == [
            {'id': 103, 'name': 'Скидка товаром', 'pictureUri': 'some_uri'},
        ]
        assert (
            categories[1]['items'][0]['optionsGroups'][0]['options'][0][
                'decimalPromoPrice'
            ]
            == '14.38'
        )
        assert (
            categories[1]['items'][0]['optionsGroups'][0]['options'][0][
                'promoPrice'
            ]
            == 15
        )
        assert (
            categories[1]['items'][0]['optionsGroups'][0]['options'][1][
                'decimalPromoPrice'
            ]
            == '9'
        )
        assert (
            categories[1]['items'][0]['optionsGroups'][0]['options'][1][
                'promoPrice'
            ]
            == 9
        )
    else:
        assert not categories[0]['items'][0].get('decimalPromoPrice')
        assert not categories[0]['items'][0].get('promoPrice')
        assert not categories[0]['items'][0]['promoTypes']
        assert not categories[0]['items'][0]['optionsGroups'][0]['options'][
            0
        ].get('decimalPromoPrice')
        assert not categories[0]['items'][0]['optionsGroups'][0]['options'][
            0
        ].get('promoPrice')
        assert not categories[0]['items'][0]['optionsGroups'][0]['options'][
            1
        ].get('decimalPromoPrice')
        assert not categories[0]['items'][0]['optionsGroups'][0]['options'][
            1
        ].get('promoPrice')


@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.config(
    EATS_RESTAURANT_MENU_PLACES_CACHE_SETTINGS={
        'missed_revision_ttl': 1,
        'batch_size': 10,
    },
)
@util.discounts_applicator_enabled()
@pytest.mark.parametrize(
    'discounts,is_promo_price',
    [
        pytest.param(False, False, id='discounts_disabled'),
        pytest.param(False, True, id='promo_price_enabled'),
        pytest.param(
            True,
            False,
            marks=util.discounts_applicator_menu(),
            id='promo_types_enabled',
        ),
        pytest.param(
            True,
            True,
            marks=util.discounts_applicator_menu(),
            id='discount_enabled',
        ),
    ],
)
async def test_old_discounts(
        mockserver, taxi_eats_restaurant_menu, discounts, is_promo_price,
):
    # возвращает несуществующую скидку
    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _match_discounts(load_json):
        return load_json('item_discount.json')

    request = {
        'slug': 'test_slug',
        'payload': {
            'categories': [
                util.build_category(
                    category_id=1,
                    available=True,
                    items=[
                        util.build_item(
                            1,
                            price=150.2,
                            promo_types=[
                                {
                                    'detailedPictureUrl': 'some_uri',
                                    'id': 100,
                                    'name': 'Discount',
                                    'pictureUri': 'some_uri',
                                },
                            ],
                        ),
                    ],
                ),
            ],
        },
    }
    if is_promo_price:
        request['payload']['categories'][0]['items'][0][
            'decimalPromoPrice'
        ] = '111.1'
        request['payload']['categories'][0]['items'][0]['promoPrice'] = 112
    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER,
        json=request,
        headers={'X-Eats-User': 'user_id=21'},
    )
    assert response.status_code == 200
    # ожидаем, что ответ не изменился
    data = response.json()
    assert data['payload']['categories'][0]['items'][0]['promoTypes'] == [
        {
            'id': 100,
            'name': 'Discount',
            'pictureUri': 'some_uri',
            'detailedPictureUrl': 'some_uri',
        },
    ]
    if is_promo_price:
        assert (
            data['payload']['categories'][0]['items'][0]['decimalPromoPrice']
            == '111.1'
        )
    else:
        assert not data['payload']['categories'][0]['items'][0].get(
            'decimalPromoPrice',
        )
    del request['slug']
    assert data == request
    assert _match_discounts.times_called == 0


@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.config(
    EATS_RESTAURANT_MENU_PLACES_CACHE_SETTINGS={
        'missed_revision_ttl': 1,
        'batch_size': 10,
    },
)
@util.discounts_applicator_enabled()
@pytest.mark.parametrize(
    'new_discounts',
    [
        pytest.param(False, id='new_discounts_disabled'),
        pytest.param(
            True,
            marks=util.discounts_applicator_menu(),
            id='new_discount_enabled',
        ),
    ],
)
async def test_new_and_old_discounts(
        taxi_eats_restaurant_menu, new_discounts, eats_discounts_applicator,
):
    if new_discounts:
        eats_discounts_applicator.add_menu_discount(
            item_id='2',
            discount_id='1',
            value_type='fraction',
            value='10',
            name='Скидка деньгами',
            description='item discount',
            picture_uri='some_uri',
        )
        eats_discounts_applicator.add_menu_discount(
            item_id='1',
            discount_id='2',
            value='5.0',
            name='Скидка деньгами от ресторана',
            description='restaurant item discount',
            picture_uri='another_uri',
        )
        eats_discounts_applicator.add_product_discount(
            item_id='3',
            discount_id='3',
            bundle=2,
            value='100',
            name='1+1',
            description='Второе блюдо в подарок',
            picture_uri='some_uri',
        )

    request = {
        'slug': 'test_slug',
        'payload': {
            'categories': [
                util.build_category(
                    category_id=1,
                    available=True,
                    items=[
                        util.build_item(1, price=170),
                        util.build_item(
                            2,
                            price=150.2,
                            promo_types=[
                                {
                                    'id': 41,
                                    'name': 'Название акции',
                                    'pictureUri': 'some_uri',
                                    'detailedPictureUrl': 'some_uri',
                                },
                            ],
                        ),
                        util.build_item(3, price=159, promo_price=123.4),
                    ],
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

    del request['slug']
    data = response.json()
    if new_discounts:
        request['payload']['categories'][0]['items'][0][
            'decimalPromoPrice'
        ] = '165'
        request['payload']['categories'][0]['items'][0]['promoPrice'] = 165
        request['payload']['categories'][0]['items'][0]['promoTypes'] = [
            {
                'id': 100,
                'name': 'Скидка деньгами',
                'pictureUri': 'another_uri',
            },
        ]
    assert data == request


@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.config(
    EATS_RESTAURANT_MENU_PLACES_CACHE_SETTINGS={
        'missed_revision_ttl': 1,
        'batch_size': 10,
    },
)
@util.discounts_applicator_enabled()
@util.promo_category_enabled()
@pytest.mark.parametrize(
    'old_discount_category',
    [
        pytest.param(
            True,
            marks=util.discounts_applicator_menu(),
            id='old_smart_category_true',
        ),
        pytest.param(
            False,
            marks=util.discounts_applicator_menu(),
            id='old_smart_category_false',
        ),
    ],
)
async def test_smart_category(
        taxi_eats_restaurant_menu,
        old_discount_category,
        eats_discounts_applicator,
):

    eats_discounts_applicator.add_menu_discount(
        item_id='1',
        discount_id='1',
        value_type='fraction',
        value='10',
        name='Скидка деньгами',
        description='item discount',
        picture_uri='some_uri',
    )
    eats_discounts_applicator.add_restaurant_menu_discounts(
        item_id='2',
        discount_id='2',
        value='5.0',
        name='Скидка деньгами от ресторана',
        description='restaurant item discount',
        picture_uri='another_uri',
    )

    request = {
        'slug': 'test_slug',
        'payload': {
            'categories': [
                util.build_category(
                    category_id=1,
                    available=True,
                    items=[util.build_item(1, price=150.2)],
                ),
                util.build_category(
                    category_id=2,
                    available=True,
                    items=[
                        util.build_item(2, price=17),
                        util.build_item(3, price=123),
                    ],
                ),
            ],
        },
    }
    if old_discount_category:
        request['payload']['categories'].insert(
            0,
            util.build_category(
                category_id=None,
                available=True,
                dynamic_id='popular',
                name='Популярные',
                items=[
                    util.build_item(2, price=17),
                    util.build_item(3, price=123),
                ],
            ),
        )
    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_MENU_HANDLER,
        json=request,
        headers={'X-Eats-User': 'user_id=21'},
    )
    assert response.status_code == 200

    data = response.json()
    assert data['payload']['categories'][0]['dynamicId'] == 'promo'
    assert data['payload']['categories'][0]['name'] == 'Акции'
    assert data['payload']['categories'][1]['id'] == 1
    assert len(data['payload']['categories'][0]['items']) == 2
    assert len(data['payload']['categories']) == 3


@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.config(
    EATS_RESTAURANT_MENU_PLACES_CACHE_SETTINGS={
        'missed_revision_ttl': 1,
        'batch_size': 10,
    },
)
@util.discounts_applicator_enabled()
@util.promo_category_enabled()
@util.discounts_applicator_menu()
async def test_sort_smart_category(
        taxi_eats_restaurant_menu, eats_discounts_applicator, load_json,
):
    discount_items = ['1', '11', '4', '2', '12', '14', '25']
    picture_value = {
        'uri': '/images/1368744/1af1fe5c61e6c3469e7d77676230620c-{w}x{h}.jpeg',
        'ratio': 1,
        'scale': 'aspect_fill',
    }
    for item in discount_items:
        eats_discounts_applicator.add_menu_discount(
            item_id=item,
            discount_id='1',
            value_type='fraction',
            value='10',
            name='Скидка деньгами',
            description='item discount',
            picture_uri='some_uri',
        )

    request = {
        'slug': 'test_slug',
        'payload': {
            'categories': [
                util.build_category(
                    category_id=1,
                    available=True,
                    items=[
                        util.build_item(1, price=150.2, available=False),
                        util.build_item(9, price=210, picture=picture_value),
                        util.build_item(
                            11, price=170, description='some description',
                        ),
                    ],
                ),
                util.build_category(
                    category_id=2,
                    available=True,
                    items=[
                        util.build_item(2, price=17.7, picture=picture_value),
                        util.build_item(
                            4,
                            price=56,
                            available=False,
                            picture=picture_value,
                            description='some description',
                        ),
                        util.build_item(5, price=109.3),
                    ],
                ),
                util.build_category(
                    category_id=3,
                    available=True,
                    items=[
                        util.build_item(
                            12,
                            price=107.7,
                            available=False,
                            picture=picture_value,
                        ),
                        util.build_item(
                            14,
                            price=506,
                            picture=picture_value,
                            description='some description',
                        ),
                        util.build_item(25, price=19.3),
                    ],
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

    expected_json = load_json('smart_category_response.json')
    assert response.json()['payload']['categories'][0] == expected_json


@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.config(
    EATS_RESTAURANT_MENU_PLACES_CACHE_SETTINGS={
        'missed_revision_ttl': 1,
        'batch_size': 10,
    },
)
@util.discounts_applicator_enabled()
@util.promo_category_enabled()
@pytest.mark.parametrize(
    'discounts',
    [
        pytest.param(False, id='discounts_disabled'),
        pytest.param(
            True,
            marks=util.discounts_applicator_menu(),
            id='discount_enabled',
        ),
    ],
)
async def test_search_item_with_discounts(
        taxi_eats_restaurant_menu, discounts, eats_discounts_applicator,
):
    eats_discounts_applicator.mock_eats_tags = [
        'tag1',
        '2tag',
        '3tag3',
        '1234',
    ]
    if discounts:
        eats_discounts_applicator.add_menu_discount(
            item_id='1',
            discount_id='1',
            value_type='fraction',
            value='10',
            name='Скидка деньгами',
            description='item discount',
            picture_uri='some_uri',
        )
        eats_discounts_applicator.add_restaurant_menu_discounts(
            item_id='10',
            discount_id='2',
            value='5.0',
            name='Скидка деньгами от ресторана',
            description='restaurant item discount',
            picture_uri='another_uri',
        )
        eats_discounts_applicator.add_product_discount(
            item_id='3',
            discount_id='3',
            bundle=2,
            value='100',
            name='1+1',
            description='Второе блюдо в подарок',
            picture_uri='some_uri',
        )

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
                    'decimalPrice': '10.00',
                    'id': 1679268437,
                    'multiplier': 2,
                    'name': 'Наршараб - 30 гр',
                    'price': 40,
                },
            ],
            'required': True,
        },
    ]

    request = {
        'slug': 'test_slug',
        'payload': [
            {
                'extra': 'data',
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
                'extra': 'data2',
                'items': [util.build_item(2, price=17, for_search=True)],
            },
            {
                'extra': 'data3',
                'items': [util.build_item(3, price=123, for_search=True)],
            },
        ],
    }
    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_SEARCH_HANDLER,
        json=request,
        headers={'X-Eats-User': 'user_id=21'},
    )
    assert response.status_code == 200

    payload = response.json()['payload']

    if discounts:
        assert payload[0]['items'][0]['decimalPromoPrice'] == '135.18'
        assert payload[0]['items'][0]['promoPrice'] == 136
        assert payload[0]['items'][0]['promoTypes'] == [
            {'id': 100, 'name': 'Скидка деньгами', 'pictureUri': 'some_uri'},
        ]
        assert payload[2]['items'][0]['promoTypes'] == [
            {'id': 103, 'name': 'Скидка товаром', 'pictureUri': 'some_uri'},
        ]
        assert (
            payload[0]['items'][0]['optionGroups'][0]['options'][0][
                'decimalPromoPrice'
            ]
            == '14.38'
        )
        assert (
            payload[0]['items'][0]['optionGroups'][0]['options'][0][
                'promoPrice'
            ]
            == 15
        )
        assert (
            payload[0]['items'][0]['optionGroups'][0]['options'][1][
                'decimalPromoPrice'
            ]
            == '9'
        )
        assert (
            payload[0]['items'][0]['optionGroups'][0]['options'][1][
                'promoPrice'
            ]
            == 9
        )
    else:
        assert not payload[0]['items'][0].get('decimalPromoPrice')
        assert not payload[0]['items'][0].get('promoPrice')
        assert not payload[0]['items'][0]['promoTypes']
        assert not payload[0]['items'][0]['promoTypes']
        assert not payload[0]['items'][0]['optionGroups'][0]['options'][0].get(
            'decimalPromoPrice',
        )
        assert not payload[0]['items'][0]['optionGroups'][0]['options'][0].get(
            'promoPrice',
        )
        assert not payload[0]['items'][0]['optionGroups'][0]['options'][1].get(
            'decimalPromoPrice',
        )
        assert not payload[0]['items'][0]['optionGroups'][0]['options'][1].get(
            'promoPrice',
        )


@pytest.mark.eats_catalog_storage_cache(
    util.EATS_RESTAURANT_MENU_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.config(
    EATS_RESTAURANT_MENU_PLACES_CACHE_SETTINGS={
        'missed_revision_ttl': 1,
        'batch_size': 10,
    },
)
@util.discounts_applicator_enabled()
@pytest.mark.parametrize(
    'is_promo_price',
    [
        pytest.param(False, id='discounts_disabled'),
        pytest.param(True, id='promo_price_enabled'),
        pytest.param(
            False,
            marks=util.discounts_applicator_menu(),
            id='promo_types_enabled',
        ),
        pytest.param(
            True,
            marks=util.discounts_applicator_menu(),
            id='discount_enabled',
        ),
    ],
)
async def test_search_old_discounts(
        mockserver, taxi_eats_restaurant_menu, is_promo_price, load_json,
):
    # возвращает несуществующую скидку
    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _match_discounts():
        return load_json('item_discount.json')

    request = {
        'slug': 'test_slug',
        'payload': [
            {
                'items': [
                    util.build_item(
                        1,
                        price=150.2,
                        promo_types=[
                            {
                                'detailedPictureUrl': 'some_uri',
                                'id': 100,
                                'name': 'Discount',
                                'pictureUri': 'some_uri',
                            },
                        ],
                        for_search=True,
                    ),
                ],
            },
        ],
    }
    if is_promo_price:
        request['payload'][0]['items'][0]['decimalPromoPrice'] = '111.1'
        request['payload'][0]['items'][0]['promoPrice'] = 112

    response = await taxi_eats_restaurant_menu.post(
        util.MODIFY_SEARCH_HANDLER,
        json=request,
        headers={'X-Eats-User': 'user_id=21'},
    )
    assert response.status_code == 200
    # ожидаем, что ответ не изменился
    data = response.json()

    del request['slug']
    assert data == request
    assert _match_discounts.times_called == 0
