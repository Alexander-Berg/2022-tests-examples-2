import copy

import pytest

from . import eats_catalog_storage
from . import eats_discounts
from . import eats_rest_menu_storage as rest_menu_storage
from . import experiments
from . import types
from . import umlaas_eats


HANDLER = '/eats-upsell/v1/upsell'
REQUEST = {
    'requestSource': 'cart',
    'context': {
        'shippingType': 'delivery',
        'items': [{'id': 20}],
        'cart': {
            'total': 0,
            'items': [{'id': 20, 'quantity': 1, 'options': []}],
        },
    },
}

# -- returned by get items -- #
FULL_ITEM_ID = 'my_full_item_id'
MIN_ITEM_ID = 'my_min_item_id'
CART_ITEM_ID = 'my_cart_item_id'

FULL_ITEM = rest_menu_storage.Item(
    id=FULL_ITEM_ID,
    origin_id='item_origin_id_1',
    legacy_id=10,
    adult=False,
    available=True,
    name='item_name_1',
    price='123.45',
    description='item_description_1',
    pictures=[rest_menu_storage.ItemPicture()],
    weight_unit=rest_menu_storage.WeightUnits.LITER.value,
    weight_value='500',
    categories_ids=[
        rest_menu_storage.CategoryIds(id='category_id_1', legacy_id=10),
    ],
    sort=100,
    stock=10,
    options_groups=[
        rest_menu_storage.OptionsGroup(  # all fields
            id='full_option_group_id_1',
            origin_id='option_group_origin_id_1',
            name='option_group_name_1',
            legacy_id=1,
            sort=10,
            min_selected_options=10,
            max_selected_options=20,
            is_required=True,
            options=[
                rest_menu_storage.Option(  # available + promo_price
                    id='option_id_1',
                    origin_id='option_origin_id_1',
                    name='option_name_1',
                    multiplier=1,
                    available=True,
                    price='10.5',
                    legacy_id=100,
                ),
                rest_menu_storage.Option(  # unavailable
                    id='option_id_2',
                    origin_id='option_origin_id_2',
                    name='option_name_2',
                    multiplier=2,
                    available=False,
                    legacy_id=200,
                    price='200',
                ),
            ],
        ),
        rest_menu_storage.OptionsGroup(  # required fields
            id='min_option_group_id_2',
            origin_id='option_group_origin_id_12',
            name='option_group_name_2',
            legacy_id=2,
            options=[
                rest_menu_storage.Option(
                    id='option_id_3',
                    origin_id='option_origin_id_3',
                    name='option_name_3',
                    multiplier=3,
                    available=True,
                    legacy_id=300,
                    price='300',
                ),
                rest_menu_storage.Option(  # without legacy id
                    id='option_id_4',
                    origin_id='option_origin_id_4',
                    name='option_name_4',
                    multiplier=4,
                    available=True,
                    price='400',
                ),
                rest_menu_storage.Option(  # without price
                    id='option_id_5',
                    origin_id='option_origin_id_5',
                    name='option_name_5',
                    multiplier=5,
                    available=True,
                    legacy_id=500,
                ),
            ],
        ),
    ],
)

MIN_ITEM = rest_menu_storage.Item(
    id=MIN_ITEM_ID,
    origin_id='min_item_origind_id',
    name='min_item_name',
    adult=True,
    legacy_id=40,
    categories_ids=[
        rest_menu_storage.CategoryIds(id='category_id_2', legacy_id=20),
    ],
    price='10',
)

CART_ITEM = rest_menu_storage.Item(
    id=CART_ITEM_ID,
    origin_id='item_origin_id_2',
    name='item_name_2',
    legacy_id=20,
    adult=False,
    available=True,
)

# -- GET ITEMS END --

EXPECTED_ITEMS = [
    types.FullUpsellItem(
        id=10,
        name='item_name_1',
        available=True,
        inStock=10,
        price=123,
        decimalPrice='123.45',
        description='item_description_1',
        adult=False,
        optionsGroups=[
            types.ItemGroup(
                id=1,
                name='option_group_name_1',
                minSelected=10,
                maxSelected=20,
                required=True,
                options=[
                    types.ItemOption(
                        id=100,
                        name='option_name_1',
                        price=11,
                        decimalPrice='10.5',
                        multiplier=1,
                    ),
                    types.ItemOption(
                        id=200,
                        name='option_name_2',
                        price=200,
                        decimalPrice='200',
                        multiplier=2,
                    ),
                ],
            ),
            types.ItemGroup(
                id=2,
                name='option_group_name_2',
                required=False,
                options=[
                    types.ItemOption(
                        id=300,
                        name='option_name_3',
                        price=300,
                        decimalPrice='300',
                        multiplier=3,
                    ),
                ],
            ),
        ],
        picture=types.Picture(
            uri='https://eda.yandex.ru/image.png',
            ratio=1.0,
            scale=types.PictureScale.AspectFit.value,
        ),
        weight='500 л',
        promoted=None,
        shippingType=types.ItemShippingType.ALL.value,
    ).as_dict(),
    types.FullUpsellItem(
        id=40,
        name='min_item_name',
        adult=True,
        available=True,
        price=10,
        decimalPrice='10',
        decimalPromoPrice=None,
        promoted=None,
        shippingType=types.ItemShippingType.ALL.value,
        picture=None,
        optionsGroups=[],
    ).as_dict(),
]


@experiments.create_rest_menu_storage_exp()
async def test_eats_rest_menu_storage(
        taxi_eats_upsell,
        core_menu_items,
        rest_menu_storage_get_items,
        eats_catalog_storage_service,
        umlaas_suggest,
        discounts_match_discounts,
):
    """
    EDACAT-2679: проверяет что сервис правильно
    обрабатывает все поля которые прислал erms
    """

    rest_menu_storage_get_items.places = [
        rest_menu_storage.Place(
            place_id='1', items=[FULL_ITEM, MIN_ITEM, CART_ITEM],
        ),
    ]

    def rest_menu_storage_callback(request):
        # первый запрос для получения id плейса
        if rest_menu_storage_get_items.times_called == 0:
            assert len(request.json['legacy_ids']) == 1
            assert frozenset(request.json['shipping_types']) == frozenset(
                ['delivery'],
            )
            assert frozenset(request.json['legacy_ids']) == frozenset([20])
        else:
            assert len(request.json['legacy_ids']) == 3
            assert frozenset(request.json['shipping_types']) == frozenset(
                ['delivery'],
            )
            assert frozenset(request.json['legacy_ids']) == frozenset(
                [10, 20, 40],
            )

    rest_menu_storage_get_items.assert_callback = rest_menu_storage_callback

    core_menu_items.assert_callback = lambda: True
    discounts_match_discounts.assert_callback = lambda request: True

    eats_catalog_storage_service.assert_callback = lambda: True
    eats_catalog_storage_service.add_place(
        eats_catalog_storage.StoragePlace(
            place_id=1, place=eats_catalog_storage.Place(slug='place_slug_1'),
        ),
    )

    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid=str(40)))
    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid=str(10)))

    response = await taxi_eats_upsell.post(HANDLER, json=REQUEST)

    assert response.status == 200

    assert rest_menu_storage_get_items.times_called == 2

    response_items = response.json()['payload']['items']

    assert sorted(response_items, key=lambda item: item['id']) == sorted(
        EXPECTED_ITEMS, key=lambda item: item['id'],
    )


# кажется формула
# new_price = old_price + (old_price * fraction) * cache_fraction


@pytest.mark.parametrize(
    'dynamic_price, expected_prices',
    [
        pytest.param(
            True,
            [[135, '135.45'], [11, '11']],
            marks=[
                pytest.mark.smart_prices_cache({'1': 100}),
                experiments.create_rest_menu_storage_exp(),
                experiments.dynamic_prices(10),
            ],
            id='dynamic_prices_10_100',
        ),
        pytest.param(
            True,
            [[135, '135.45'], [11, '11']],
            marks=[
                pytest.mark.smart_prices_cache({'1': 10}),
                experiments.create_rest_menu_storage_exp(),
                experiments.dynamic_prices(100),
            ],
            id='dynamic_prices_100_10',
        ),
        pytest.param(
            False,
            None,
            marks=[
                pytest.mark.smart_prices_cache({'1': 10}),
                experiments.create_rest_menu_storage_exp(),
            ],
            id='dynamic_prices_off_by_exp',
        ),
        pytest.param(
            False,
            None,
            marks=[
                experiments.create_rest_menu_storage_exp(),
                experiments.dynamic_prices(100),
            ],
            id='dynamic_prices_off_by_service',
        ),
    ],
)
async def test_upsell_smart_prices(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        rest_menu_storage_get_items,
        umlaas_suggest,
        dynamic_price,
        expected_prices,
        discounts_match_discounts,
):
    'проверяет что если умные цены работают правильно для ответа erms'
    rest_menu_storage_get_items.places = [
        rest_menu_storage.Place(
            place_id='1', items=[FULL_ITEM, MIN_ITEM, CART_ITEM],
        ),
    ]

    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid=str(40)))
    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid=str(10)))

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=1),
    )
    response = await taxi_eats_upsell.post(HANDLER, json=REQUEST)
    assert response.status_code == 200
    expected_items = sorted(
        copy.deepcopy(EXPECTED_ITEMS), key=lambda item: item['id'],
    )

    if dynamic_price is True:
        expected_items[0]['price'] = expected_prices[0][0]
        expected_items[0]['decimalPrice'] = expected_prices[0][1]

        expected_items[1]['price'] = expected_prices[1][0]
        expected_items[1]['decimalPrice'] = expected_prices[1][1]

    assert sorted(
        response.json()['payload']['items'], key=lambda item: item['id'],
    ) == sorted(expected_items, key=lambda item: item['id'])

    assert rest_menu_storage_get_items.times_called == 2
    assert eats_catalog_storage_service.times_called == 1
    assert umlaas_suggest.times_called == 1


@experiments.create_rest_menu_storage_exp()
async def test_erms_place_id_with_2_places(
        taxi_eats_upsell,
        core_menu_items,
        rest_menu_storage_get_items,
        eats_catalog_storage_service,
        umlaas_suggest,
        discounts_match_discounts,
):
    """
        EDACAT-2679:Проверяет что если erms вернул два плейса возникает ворнинг
        и айтемы не возвращаются
    """
    rest_menu_storage_get_items.places = [
        rest_menu_storage.Place(
            place_id='1', items=[FULL_ITEM, MIN_ITEM, CART_ITEM],
        ),
        rest_menu_storage.Place(place_id='2', items=[FULL_ITEM]),
    ]

    rest_menu_storage_get_items.assert_callback = lambda request: True

    core_menu_items.assert_callback = lambda: True

    eats_catalog_storage_service.assert_callback = lambda: True
    eats_catalog_storage_service.add_place(
        eats_catalog_storage.StoragePlace(
            place_id=1, place=eats_catalog_storage.Place(slug='place_slug_1'),
        ),
    )

    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid=str(40)))
    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid=str(10)))

    response = await taxi_eats_upsell.post(HANDLER, json=REQUEST)

    assert response.status == 200

    assert rest_menu_storage_get_items.times_called == 1

    assert response.json()['payload']['items'] == []


@experiments.create_rest_menu_storage_exp()
async def test_erms_responded_two_places(
        taxi_eats_upsell,
        core_menu_items,
        rest_menu_storage_get_items,
        eats_catalog_storage_service,
        umlaas_suggest,
        discounts_match_discounts,
):
    """
    EDACAT-2679: проверяет что если erms ответил двумя плейсами
    код выбирает тот который вернул каталог
    """
    rest_menu_storage_get_items.places = [
        rest_menu_storage.Place(
            place_id='1', items=[FULL_ITEM, MIN_ITEM, CART_ITEM],
        ),
        rest_menu_storage.Place(place_id='2', items=[FULL_ITEM]),
    ]

    rest_menu_storage_get_items.assert_callback = lambda request: True

    core_menu_items.assert_callback = lambda: True

    eats_catalog_storage_service.assert_callback = lambda: True
    eats_catalog_storage_service.add_place(
        eats_catalog_storage.StoragePlace(
            place_id=1, place=eats_catalog_storage.Place(slug='place_slug_1'),
        ),
    )

    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid=str(40)))
    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid=str(10)))

    response = await taxi_eats_upsell.post(
        HANDLER,
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 20}],
                'cart': {
                    'total': 0,
                    'items': [{'id': 20, 'quantity': 1, 'options': []}],
                },
                'place_slug': 'place_slug_1',
            },
        },
    )

    assert response.status == 200

    assert rest_menu_storage_get_items.times_called == 1

    response_items = response.json()['payload']['items']

    assert sorted(response_items, key=lambda item: item['id']) == sorted(
        EXPECTED_ITEMS, key=lambda item: item['id'],
    )


@pytest.mark.parametrize(
    'discounts',
    [
        pytest.param(
            False,
            id='discounts_disabled',
            marks=[experiments.create_rest_menu_storage_exp()],
        ),
        pytest.param(
            True,
            id='discount_enabled',
            marks=[experiments.create_rest_menu_storage_exp()],
        ),
        pytest.param(
            True,
            id='smart_prices_enabled',
            marks=[
                pytest.mark.smart_prices_cache({'1': 100}),
                experiments.create_rest_menu_storage_exp(),
                experiments.dynamic_prices(10),
            ],
        ),
    ],
)
async def test_upsell_discounts(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        rest_menu_storage_get_items,
        umlaas_suggest,
        discounts_match_discounts,
        discounts,
):
    'EDACAT-2774: проверяет что скидки работают правильно для ответа erms'
    expected_items = sorted(
        copy.deepcopy(EXPECTED_ITEMS), key=lambda item: item['id'],
    )

    if discounts:
        expected_items[0]['promoTypes'] = [
            {
                'detailedPictureUrl': None,
                'id': 100,
                'name': 'Скидка деньгами',
                'pictureUri': 'some_uri',
            },
        ]
        expected_items[1]['promoTypes'] = [
            {
                'detailedPictureUrl': None,
                'id': 100,
                'name': 'Скидка деньгами',
                'pictureUri': 'another_uri',
            },
        ]

        discounts_match_discounts.add_menu_discount(
            eats_discounts.MenuDiscount(
                id='40',
                discount_id='2',
                value='5.5',
                value_type='absolute',
                name='Скидка деньгами',
                description='restaurant item discount',
                picture_uri='another_uri',
                promo_type='skidka2',
            ),
        )
        discounts_match_discounts.add_menu_discount(
            eats_discounts.MenuDiscount(
                id='10',
                discount_id='1',
                value_type='fraction',
                value='10',
                name='Скидка деньгами',
                description='item discount',
                picture_uri='some_uri',
                promo_type='skidka',
            ),
        )

        expected_items[0]['promoPrice'] = 111
        expected_items[0]['decimalPromoPrice'] = '111.1'
        expected_items[0]['optionsGroups'][0]['options'][0]['promoPrice'] = 9
        expected_items[0]['optionsGroups'][0]['options'][0][
            'decimalPromoPrice'
        ] = '9.45'

        expected_items[0]['optionsGroups'][0]['options'][1]['promoPrice'] = 180
        expected_items[0]['optionsGroups'][0]['options'][1][
            'decimalPromoPrice'
        ] = '180'

        expected_items[0]['optionsGroups'][1]['options'][0]['promoPrice'] = 270
        expected_items[0]['optionsGroups'][1]['options'][0][
            'decimalPromoPrice'
        ] = '270'

        expected_items[1]['promoPrice'] = 5
        expected_items[1]['decimalPromoPrice'] = '4.5'

    rest_menu_storage_get_items.places = [
        rest_menu_storage.Place(
            place_id='1', items=[FULL_ITEM, MIN_ITEM, CART_ITEM],
        ),
    ]
    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid=str(40)))
    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid=str(10)))
    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=1),
    )
    response = await taxi_eats_upsell.post(HANDLER, json=REQUEST)
    assert response.status_code == 200
    assert sorted(
        response.json()['payload']['items'], key=lambda item: item['id'],
    ) == sorted(expected_items, key=lambda item: item['id'])
    assert rest_menu_storage_get_items.times_called == 2
    assert eats_catalog_storage_service.times_called == 1
    assert umlaas_suggest.times_called == 1
