from typing import List

import pytest

from testsuite.utils import matching

from . import configs
from . import eats_catalog_storage
from . import eats_products
from . import experiments
from . import types
from . import umlaas_eats
from . import utils


@pytest.mark.parametrize(
    'business, place_slug, core_calls, products_calls',
    [
        pytest.param(
            eats_catalog_storage.Business.RESTAURANT,
            None,
            2,
            0,
            id='restaraunt no slug',
        ),
        pytest.param(
            eats_catalog_storage.Business.RESTAURANT,
            'place_1',
            1,
            0,
            id='restaraunt with slug',
        ),
        pytest.param(
            eats_catalog_storage.Business.SHOP, None, 1, 1, id='shop no slug',
        ),
        pytest.param(
            eats_catalog_storage.Business.SHOP,
            'place_1',
            0,
            1,
            id='shop with slug',
        ),
    ],
)
async def test_place_info_source(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        core_menu_items,
        products_menu_items,
        business,
        place_slug,
        umlaas_suggest,
        core_calls,
        products_calls,
        products_id_mappings,
        umlaas_eats_retail_suggest,
):
    """
    Тест проверяет что информация для ритейловых заведений
    получается из eats-products
    """

    for item_id in [1, 2, 3]:
        core_menu_items.add_item(utils.build_core_item(item_id))
        products_menu_items.add_item(
            eats_products.RetailItem(
                core_item_id=item_id, public_id=str(item_id),
            ),
        )
        products_id_mappings.add_mapping(
            eats_products.Mapping(core_id=item_id),
        )

    umlaas_eats_retail_suggest.set_recommendations(['2', '3'])
    umlaas_suggest.add_items(
        [umlaas_eats.SuggestItem(uuid='2'), umlaas_eats.SuggestItem(uuid='3')],
    )

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(
            place_id=1, business=business,
        ),
    )

    request: dict = {
        'requestSource': 'cart',
        'context': {
            'shippingType': 'delivery',
            'items': [{'id': 1}],
            'cart': {
                'total': 100,
                'items': [{'id': 1, 'quantity': 1, 'options': []}],
            },
        },
    }
    if place_slug:
        request['context']['place_slug'] = place_slug

    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell', json=request,
    )

    # если в ручку не передан слаг, то тип заведения определяется только
    # после первого похода в core, иначе со слагом можно сразу пойти в
    # сторадж и получить тип заведения
    assert eats_catalog_storage_service.times_called == 1
    assert core_menu_items.times_called == core_calls
    assert products_menu_items.times_called == products_calls

    # проверить содержимое ответа
    expected_items_ids = [2, 3]

    assert response.status_code == 200
    items = response.json()['payload']['items']
    assert len(expected_items_ids) == len(items)
    for expected_id, response_item in zip(expected_items_ids, items):
        assert expected_id == response_item['id']


@pytest.mark.yt(static_table_data=['yt_retail_promo_suitable_categories.yaml'])
@experiments.promo_settings(positions=[0, 1])
@experiments.create_promo_experiment(
    name='retail_suitable_categories',
    promo={'promo_name': 'retail_suitable_categories'},
)
@configs.adverts_cache_config(
    tables=[
        configs.YtTable(
            path='//testsuite/retail/promo/suitable_categories',
            promotion='retail_suitable_categories',
            type=configs.YtTableType.Retail,
        ),
    ],
)
async def test_yt_suitable_categories(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        yt_apply,
        products_menu_items,
        products_id_mappings,
        umlaas_eats_retail_suggest,
):
    """
    EDACAT-1916: проверяет, что категории товара корректно парсятся из
    yt-вой таблицы.
    """

    place_id: int = 1
    place_slug: str = f'place_{place_id}'
    place = eats_catalog_storage.StoragePlace(
        place_id=place_id,
        place=eats_catalog_storage.Place(
            slug=place_slug, business=eats_catalog_storage.Business.SHOP,
        ),
    )
    eats_catalog_storage_service.add_place(place)

    core_item_id: int = 1
    products_id_mappings.add_mapping(
        eats_products.Mapping(core_id=core_item_id),
    )

    items: List[eats_products.RetailItem] = [
        eats_products.RetailItem(
            core_item_id=core_item_id,
            public_id='1',
            categories=['1', '2', '3', '4'],
        ),  # т.к. товар лежит в корзине, то добавляем ему категории
        eats_products.RetailItem(core_item_id=2, public_id='2'),
        eats_products.RetailItem(core_item_id=3, public_id='3'),
        eats_products.RetailItem(core_item_id=4, public_id='4'),
    ]

    for item in items:
        products_menu_items.add_item(item)

    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'place_slug': place_slug,
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {
                    'total': 100,
                    'items': [
                        {'id': core_item_id, 'quantity': 1, 'options': []},
                    ],
                },
            },
        },
    )
    assert response.status_code == 200
    assert eats_catalog_storage_service.times_called == 1
    assert products_menu_items.times_called == 1

    expected_item_ids: list = [2, 4]

    items: list = response.json()['payload']['items']
    assert len(items) == len(expected_item_ids)
    for item, expected_item_id in zip(items, expected_item_ids):
        assert item['id'] == expected_item_id


@experiments.use_retail_new_flow(True)
@experiments.create_promo_experiment(
    name='retail_new_flow', promo={'promo_name': 'retail_new_flow'},
)
@configs.adverts_cache_config(
    tables=[
        configs.YtTable(
            path='//testsuite/retail/promo/retail_new_flow',
            promotion='retail_new_flow',
            type=configs.YtTableType.Retail,
        ),
    ],
)
@pytest.mark.parametrize(
    'umlaas_recommendations, request_items, request_cart_items, expected',
    [
        pytest.param([], [], [1], [], id='no recommendations at all'),
        pytest.param(
            ['2'],
            [],
            [1],
            [types.UpsellItem(core_id=2)],
            id='recommend single item',
        ),
        pytest.param(
            ['2', '3'],
            [],
            [1],
            [types.UpsellItem(core_id=2), types.UpsellItem(core_id=3)],
            id='recommend many items',
        ),
        pytest.param(
            ['2', '3', '4', '5'],
            [],
            [1],
            [
                types.UpsellItem(core_id=3, is_promoted=True),
                types.UpsellItem(core_id=4, is_promoted=True),
                types.UpsellItem(core_id=5, is_promoted=True),
                types.UpsellItem(core_id=2, is_promoted=False),
            ],
            marks=(
                experiments.promo_settings(positions=[0, 1, 2]),
                pytest.mark.yt(
                    static_table_data=['yt_retail_promo_retail_new_flow.yaml'],
                ),
            ),
            id='recommend and promote',
        ),
    ],
)
async def test_upsell_retail_new_flow(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        yt_apply,
        umlaas_suggest,
        products_menu_items,
        products_id_mappings,
        umlaas_eats_retail_suggest,
        umlaas_recommendations: List[str],
        request_items: List[int],
        request_cart_items: List[int],
        expected: List[types.UpsellItem],
):
    """
    EDACAT-2030: проверяет запрос на апсейл в ритейле для нового флоу.
    """

    place_id: int = 1
    place_slug: str = f'place_{place_id}'
    place = eats_catalog_storage.StoragePlace(
        place_id=place_id,
        place=eats_catalog_storage.Place(
            slug=place_slug, business=eats_catalog_storage.Business.SHOP,
        ),
    )
    eats_catalog_storage_service.add_place(place)

    umlaas_eats_retail_suggest.set_recommendations(umlaas_recommendations)
    for umlaas_recommendation in umlaas_recommendations:
        products_menu_items.add_item(
            eats_products.RetailItem(core_item_id=int(umlaas_recommendation)),
        )

    items: list = []
    for item in request_items:
        items.append({'id': item})
        products_id_mappings.add_mapping(eats_products.Mapping(item))
        products_menu_items.add_item(
            eats_products.RetailItem(core_item_id=item, public_id=str(item)),
        )

    cart_items: list = []
    for cart_item in request_cart_items:
        cart_items.append({'id': cart_item, 'quantity': 1, 'options': []})
        products_id_mappings.add_mapping(eats_products.Mapping(cart_item))
        products_menu_items.add_item(
            eats_products.RetailItem(core_item_id=cart_item),
        )

    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': items,
                'cart': {'total': 0, 'items': cart_items},
                'place_slug': place_slug,
            },
        },
    )
    assert response.status_code == 200
    assert eats_catalog_storage_service.times_called == 1
    assert products_menu_items.times_called == 1
    assert products_id_mappings.times_called == 1
    assert umlaas_eats_retail_suggest.times_called == 1

    actual: list = response.json()['payload']['items']
    assert len(expected) == len(actual)
    for want, got in zip(expected, actual):
        types.assert_equal_to_response_item(want, got)


async def test_upsell_retail_check_duplicating(
        taxi_eats_upsell,
        testpoint,
        eats_catalog_storage_service,
        yt_apply,
        umlaas_suggest,
        products_menu_items,
        products_id_mappings,
        umlaas_eats_retail_suggest,
):

    """
    EDACAT-2273: проверяет отсутствие дубликатов товаров в запросе к
    /api/v2/menu/get-items
    """

    @testpoint('getitems')
    def getitems(data):
        assert data['public_ids'] == 1

    umlaas_recommendations = ['1', '1', '1']

    await taxi_eats_upsell.enable_testpoints()

    place_id: int = 1
    place_slug: str = f'place_{place_id}'
    place = eats_catalog_storage.StoragePlace(
        place_id=place_id,
        place=eats_catalog_storage.Place(
            slug=place_slug, business=eats_catalog_storage.Business.SHOP,
        ),
    )
    eats_catalog_storage_service.add_place(place)

    items: list = []
    for item in [1, 1, 1]:
        items.append({'id': item})
        products_id_mappings.add_mapping(eats_products.Mapping(item))
        products_menu_items.add_item(
            eats_products.RetailItem(core_item_id=item, public_id=str(item)),
        )

    cart_items: list = []
    for cart_item in [1, 1, 1]:
        cart_items.append({'id': cart_item, 'quantity': 1, 'options': []})
        products_id_mappings.add_mapping(eats_products.Mapping(cart_item))
        products_menu_items.add_item(
            eats_products.RetailItem(core_item_id=cart_item),
        )

    umlaas_eats_retail_suggest.set_recommendations(umlaas_recommendations)
    for umlaas_recommendation in umlaas_recommendations:
        products_menu_items.add_item(
            eats_products.RetailItem(core_item_id=int(umlaas_recommendation)),
        )

    await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'place_slug': place_slug,
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {
                    'total': 3,
                    'items': [
                        {'id': 1, 'quantity': 1, 'options': []},
                        {'id': 1, 'quantity': 1, 'options': []},
                        {'id': 1, 'quantity': 1, 'options': []},
                    ],
                },
            },
        },
    )

    assert getitems.times_called == 1


async def test_upsell_retail_check_umlaas_request(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        products_menu_items,
        products_id_mappings,
        umlaas_eats_retail_suggest,
):

    place_id: int = 1
    place_slug: str = f'place_{place_id}'
    place = eats_catalog_storage.StoragePlace(
        place_id=place_id,
        place=eats_catalog_storage.Place(
            slug=place_slug, business=eats_catalog_storage.Business.SHOP,
        ),
    )
    eats_catalog_storage_service.add_place(place)

    for public_id in [1, 2, 3]:
        products_id_mappings.add_mapping(eats_products.Mapping(public_id))
        products_menu_items.add_item(
            eats_products.RetailItem(
                core_item_id=public_id, public_id=str(public_id),
            ),
        )

    umlaas_eats_retail_suggest.set_expected_request(
        {
            'request_id': matching.any_string,
            'items': ['1'],
            'cart': {'items': [{'public_id': '1', 'quantity': 1}]},
            'brand_id': place.brand.brand_id,
            'place_id': place.place_id,
            'source': 'cart',
        },
    )
    umlaas_eats_retail_suggest.set_recommendations(['2', '3'])

    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'place_slug': place_slug,
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {
                    'total': 1,
                    'items': [{'id': 1, 'quantity': 1, 'options': []}],
                },
            },
        },
    )
    assert response.status_code == 200
