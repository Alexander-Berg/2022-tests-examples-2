import pytest

from . import common
from . import const


# проверяем, что ручка возвращает товары для всех существующих id
# вне зависимости от остатков
async def test_modes_goods_info_200(
        taxi_grocery_api, grocery_p13n, overlord_catalog, load_json,
):
    location = const.LOCATION
    products_data = load_json(
        'overlord_catalog_products_data_with_options.json',
    )
    common.prepare_overlord_catalog_json(
        load_json, overlord_catalog, location, products_data=products_data,
    )

    json = {
        'product_ids': [
            'product-1',
            'another-product',  # doesn't exist
            'product-2',
            'product-3',  # no stocks
        ],
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/goods-info',
        json=json,
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    data = response.json()

    # Проверим, что пришли только существующие товары
    assert len(data['products']) == 3
    assert data['products'][0]['id'] == 'product-1'
    assert data['products'][1]['id'] == 'product-2'
    assert data['products'][2]['id'] == 'product-3'
    for product in data['products']:
        assert product['type'] == 'good_info'
        assert 'image_url_templates' in product
    assert 'amount' in data['products'][0]['options']
    assert 'amount_units' in data['products'][0]['options']


@pytest.mark.translations(
    wms_attributes={
        'sahar': {'en': 'shugar'},
        'fish': {'en': 'translated_fish'},
    },
)
@pytest.mark.config(
    GROCERY_API_ATTRIBUTES_ICONS={
        'sahar': {'icon_link': 'sahar_icon'},
        'fish': {'icon_link': 'fish_icon', 'big_icon_link': 'big_fish_icon'},
    },
)
async def test_modes_goods_info_attributes_in_response(
        taxi_grocery_api,
        grocery_p13n,
        overlord_catalog,
        load_json,
        empty_upsale,
):
    location = const.LOCATION
    depot_id = const.DEPOT_ID
    product_id = 'product-1'
    products_data = load_json(
        'overlord_catalog_products_data_with_options.json',
    )
    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        products_data,
        depot_id=depot_id,
    )

    json = {
        'position': {'location': location},
        'product_ids': [product_id],
        'user_preferences': {
            'important_ingredients': ['sahar'],
            'main_allergens': ['fish', 'some more', 'sahar'],
            'custom_tags': ['halal'],
        },
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/goods-info',
        json=json,
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    options = response.json()['products'][0]['options']
    assert options['important_ingredients'] == [
        {'attribute': 'sahar', 'title': 'shugar', 'icon_link': 'sahar_icon'},
    ]
    assert options['main_allergens'] == [
        {
            'attribute': 'fish',
            'title': 'translated_fish',
            'icon_link': 'fish_icon',
            'big_icon_link': 'big_fish_icon',
        },
    ]
    assert options['custom_tags'] == [{'attribute': 'halal', 'title': 'halal'}]


# Проверка поля 'catalog_paths' в ответе ручки
@pytest.mark.parametrize('layout_id', ['layout-1', 'layout-2'])
@pytest.mark.parametrize('need_catalog_paths', [None, False, True])
async def test_catalog_paths(
        taxi_grocery_api,
        overlord_catalog,
        grocery_products,
        layout_id,
        need_catalog_paths,
):
    product_id = 'some-product-id'
    common.setup_catalog_for_paths_test(
        overlord_catalog, grocery_products, product_id,
    )

    headers = {'Accept-Language': 'en'}
    request_body = {
        'product_ids': [product_id],
        'position': {'location': common.DEFAULT_LOCATION},
        'layout_id': layout_id,
    }
    if need_catalog_paths is not None:
        request_body['need_catalog_paths'] = need_catalog_paths

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/modes/goods-info',
        headers=headers,
        json=request_body,
    )
    assert response.status_code == 200
    response_data = response.json()

    assert len(response_data['products']) == 1
    assert response_data['products'][0]['id'] == product_id
    if need_catalog_paths is True:
        assert 'catalog_paths' in response_data['products'][0]
        common.check_catalog_paths(
            response_data['products'][0]['catalog_paths'], layout_id,
        )
    else:
        assert 'catalog_paths' not in response_data['products'][0]
