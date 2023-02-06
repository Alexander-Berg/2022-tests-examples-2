import math

import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils


PRODUCTS_HEADERS = {
    'X-AppMetrica-DeviceId': 'device_id',
    'x-platform': 'android_app',
    'x-app-version': '12.11.12',
    'X-Eats-User': 'user_id=456',
}
PLACE_ID = '1'
DISCOUNT_PROMO = {
    'enabled': True,
    'id': 25,
    'name': 'Скидка для магазинов.',
    'picture_uri': (
        'https://avatars.mds.yandex.net/get-eda/1370147/5b73e9ea19587/80x80'
    ),
    'detailed_picture_url': (
        'https://avatars.mds.yandex.net/get-eda/1370148/5b73e9ea19588/80x80'
    ),
}

DYNAMIC_INFO_BATCH_SIZE = 50
PARENT_CATEGORIES_BATCH_SIZE = 10

USE_NEW_HANDLERS_CONFIG = pytest.mark.config(
    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
        {'get_items_handlers_version': 'v2'}
    ),
)


@pytest.fixture(name='several_places_products_mapping')
def _several_places_products_mapping(
        sql_add_place, add_place_products_mapping,
):
    def _insert_mapping():
        sql_add_place(2, 'slug2', 1)

        add_place_products_mapping(
            [
                conftest.ProductMapping(
                    '9000000001', 101, 'f92b147c-a05f-40df-a68b-064fbaed7059',
                ),
                conftest.ProductMapping(
                    '9000000002', 102, '9c6b8cb2-8d1b-4d80-a5cb-f609c4b633aa',
                ),
                conftest.ProductMapping(
                    '9000000003', 103, '45685053-db9c-4eb5-a6b2-c4f643faa4ec',
                ),
                conftest.ProductMapping(
                    '9000000004', 104, '5cd71cec-9d5d-4570-a234-36b3b1cbc4d2',
                ),
            ],
        )

        add_place_products_mapping(
            [
                conftest.ProductMapping(
                    '9000000005', 201, '33514313-4503-4dc6-9947-138a33356c62',
                ),
                conftest.ProductMapping(
                    '9000000006', 202, '3ed537e8-94c5-4967-800e-7b9bc1f64b39',
                ),
            ],
            2,
        )

    return _insert_mapping


@pytest.mark.config(EATS_PRODUCTS_SETTINGS={'discount_promo': DISCOUNT_PROMO})
async def test_get_items_v2(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        several_places_products_mapping,
        load_json,
):
    several_places_products_mapping()

    mock_nomenclature_static_info_context.add_product(
        id_='f92b147c-a05f-40df-a68b-064fbaed7059', name='101',
    )
    mock_nomenclature_static_info_context.add_product(
        id_='9c6b8cb2-8d1b-4d80-a5cb-f609c4b633aa', name='102',
    )
    mock_nomenclature_static_info_context.add_product(
        id_='45685053-db9c-4eb5-a6b2-c4f643faa4ec', name='103',
    )

    mock_nomenclature_dynamic_info_context.add_product(
        'f92b147c-a05f-40df-a68b-064fbaed7059', price=1,
    )
    mock_nomenclature_dynamic_info_context.add_product(
        '9c6b8cb2-8d1b-4d80-a5cb-f609c4b633aa', price=3,
    )
    mock_nomenclature_dynamic_info_context.add_product(
        '45685053-db9c-4eb5-a6b2-c4f643faa4ec', price=4,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': ['101', '102', '103']},
        headers=PRODUCTS_HEADERS,
    )

    assert response.json() == load_json('products_response.json')

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_get_parent_context.handler.times_called == 1


async def test_no_place_found_in_mapping(taxi_eats_products):
    # Тест проверяет, что если по core_id не удалось найти place
    # возвращается ошибка
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS, json={'items': ['999']},
    )
    assert response.status_code == 400
    assert response.json()['error'] == 'not_found_place'


async def test_some_items_not_found_in_mapping(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        several_places_products_mapping,
):
    several_places_products_mapping()
    public_ids = {
        '101': 'f92b147c-a05f-40df-a68b-064fbaed7059',
        '102': '9c6b8cb2-8d1b-4d80-a5cb-f609c4b633aa',
    }

    for key in public_ids:
        mock_nomenclature_static_info_context.add_product(
            id_=public_ids[key], name=key,
        )
        mock_nomenclature_dynamic_info_context.add_product(public_ids[key])

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS, json={'items': ['101', '102', '999']},
    )
    assert response.status_code == 200

    assert {
        item['name']: item['public_id']
        for item in response.json()['place_menu_items']
    } == public_ids

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_get_parent_context.handler.times_called == 1


async def test_some_items_not_found_in_nomenclature(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        several_places_products_mapping,
):
    several_places_products_mapping()
    public_ids = {
        '101': 'f92b147c-a05f-40df-a68b-064fbaed7059',
        '102': '9c6b8cb2-8d1b-4d80-a5cb-f609c4b633aa',
    }

    for key in public_ids:
        mock_nomenclature_static_info_context.add_product(
            id_=public_ids[key], name=key,
        )
        mock_nomenclature_dynamic_info_context.add_product(public_ids[key])

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS, json={'items': ['101', '102', '104']},
    )
    assert response.status_code == 200
    assert {
        item['name']: item['public_id']
        for item in response.json()['place_menu_items']
    } == public_ids

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_get_parent_context.handler.times_called == 1


async def test_no_items_found_in_nomenclature(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        several_places_products_mapping,
):
    several_places_products_mapping()
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS, json={'items': ['101', '102', '104']},
    )
    assert response.status_code == 400
    assert response.json()['error'] == 'place_menu_items_not_found'


async def test_items_from_different_places(
        taxi_eats_products, several_places_products_mapping,
):
    several_places_products_mapping()
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS, json={'items': ['101', '102', '201']},
    )
    assert response.status_code == 400
    assert response.json()['error'] == 'different_places_forbidden'


async def test_nomenclature_v2_static_info_404_code(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        several_places_products_mapping,
):
    # Тест проверяет, что если /v1/products/info возвращает 404, то ручка
    # возвращает 400
    several_places_products_mapping()
    mock_nomenclature_static_info_context.set_status(status_code=404)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS, json={'items': ['101']},
    )
    assert response.status_code == 400
    assert response.json()['error'] == 'not_found_place'
    assert response.json()['message'] == (
        'PlaceNotFound from POST /v1/products/info; requested ids count 1; '
        'first id f92b147c-a05f-40df-a68b-064fbaed7059; '
        'for place slug. Initial exception is: POST /v1/products/info'
    )
    assert mock_nomenclature_static_info_context.handler.times_called == 1


async def test_nomenclature_dynamic_info_404_code(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        several_places_products_mapping,
):
    # Тест проверяет, что если /v1/place/products/info возвращает 404,
    # то ручка возвращает 400
    several_places_products_mapping()
    mock_nomenclature_dynamic_info_context.set_status(status_code=404)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS, json={'items': ['101']},
    )
    assert response.status_code == 400
    assert response.json()['error'] == 'not_found_place'
    assert response.json()['message'] == (
        'PlaceNotFound from POST /v1/place/products/info; requested ids '
        'count 1; first id f92b147c-a05f-40df-a68b-064fbaed7059; '
        'for place slug. Initial exception is: POST /v1/place/products/info'
    )


@pytest.mark.config(EATS_PRODUCTS_SETTINGS={'discount_promo': DISCOUNT_PROMO})
async def test_get_items_v2_returns_public_id(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        several_places_products_mapping,
):
    several_places_products_mapping()
    public_ids = {
        '101': 'f92b147c-a05f-40df-a68b-064fbaed7059',
        '102': '9c6b8cb2-8d1b-4d80-a5cb-f609c4b633aa',
        '103': '45685053-db9c-4eb5-a6b2-c4f643faa4ec',
    }

    for key in public_ids:
        mock_nomenclature_static_info_context.add_product(
            id_=public_ids[key], name=key,
        )
        mock_nomenclature_dynamic_info_context.add_product(public_ids[key])

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': ['101', '102', '103']},
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert {
        item['name']: item['public_id']
        for item in response.json()['place_menu_items']
    } == public_ids

    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_get_parent_context.handler.times_called == 1
    assert mock_nomenclature_get_parent_context.handler.times_called == 1


@pytest.mark.config(EATS_PRODUCTS_SETTINGS={'discount_promo': DISCOUNT_PROMO})
async def test_get_items_v2_with_categories_handlers_v2(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
):
    # Тест проверяет что ответ ручки содержит массив id категорий
    # для каждого товара, полученный из сервиса номенклатуры с использованием
    # новых ручек

    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='origin_id_1', core_id=101, public_id='public_id_1',
            ),
            conftest.ProductMapping(
                origin_id='origin_id_2', core_id=102, public_id='public_id_2',
            ),
            conftest.ProductMapping(
                origin_id='origin_id_3', core_id=103, public_id='public_id_3',
            ),
        ],
    )

    mock_nomenclature_static_info_context.add_product(id_='public_id_1')
    mock_nomenclature_static_info_context.add_product(id_='public_id_2')
    mock_nomenclature_static_info_context.add_product(id_='public_id_3')

    mock_nomenclature_dynamic_info_context.add_product(
        id_='public_id_1', origin_id='origin_id_1', parent_category_ids=['1'],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        id_='public_id_2', origin_id='origin_id_2', parent_category_ids=['2'],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        id_='public_id_3',
        origin_id='origin_id_3',
        parent_category_ids=['1', '3'],
    )

    mock_nomenclature_get_parent_context.add_category(id_='1', parent_id=None)
    mock_nomenclature_get_parent_context.add_category(id_='2', parent_id='1')
    mock_nomenclature_get_parent_context.add_category(id_='3', parent_id='4')
    mock_nomenclature_get_parent_context.add_category(id_='4', parent_id='5')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': ['101', '102', '103']},
        headers=PRODUCTS_HEADERS,
    )

    # different OS calculate the hash differently, so we need to sort
    def sort_categories(products):
        for place_menu_item in products['place_menu_items']:
            place_menu_item['categories'].sort()

    assert response.status_code == 200
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_get_parent_context.handler.times_called == 1

    result = response.json()

    assert 'place_menu_items' in result
    assert len(result['place_menu_items']) == 3

    sort_categories(result)

    items_dict = {
        item['public_id']: item for item in result['place_menu_items']
    }

    assert 'public_id_1' in items_dict
    item = items_dict['public_id_1']
    assert item['categories'] == ['1']

    assert 'public_id_2' in items_dict
    item = items_dict['public_id_2']
    assert item['categories'] == ['1', '2']

    assert 'public_id_3' in items_dict
    item = items_dict['public_id_3']
    assert item['categories'] == ['1', '3', '4', '5']


@pytest.mark.parametrize('items_count', [10, 100, 203])
@pytest.mark.config(EATS_PRODUCTS_SETTINGS={'discount_promo': DISCOUNT_PROMO})
@pytest.mark.config(
    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS={
        'v1_place_products_info_batch_size': DYNAMIC_INFO_BATCH_SIZE,
        'v1_place_categories_get_parent_batch_size': (
            PARENT_CATEGORIES_BATCH_SIZE
        ),
        'get_items_handlers_version': 'v2',
    },
)
async def test_get_items_v2_batching(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        items_count,
):
    # Тест проверяет что ответ ручки содержит массив id категорий
    # для каждого товара, полученный из сервиса номенклатуры с использованием
    # новых ручек и батч запросах

    ids_mapping = []
    parent_category_offset = 10000
    parent_category = parent_category_offset
    for i in range(1, items_count + 1):
        origin_id = 'origin_id_' + str(i)
        core_id = 100 + i
        public_id = 'public_id_' + str(i)
        parent_category += 1

        ids_mapping.append(
            conftest.ProductMapping(origin_id, core_id, public_id),
        )

        mock_nomenclature_static_info_context.add_product(public_id)

        mock_nomenclature_dynamic_info_context.add_product(
            id_=public_id, origin_id=origin_id, parent_category_ids=[str(i)],
        )
        mock_nomenclature_get_parent_context.add_category(
            id_=str(i), parent_id=str(parent_category),
        )

    add_place_products_mapping(ids_mapping)

    requested_items = [str(item.core_id) for item in ids_mapping]
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': requested_items},
        headers=PRODUCTS_HEADERS,
    )

    # different OS calculate the hash differently, so we need to sort
    def sort_categories(products):
        for place_menu_item in products['place_menu_items']:
            place_menu_item['categories'].sort()

    assert response.status_code == 200
    assert (
        mock_nomenclature_dynamic_info_context.handler.times_called
        == math.ceil(items_count / DYNAMIC_INFO_BATCH_SIZE)
    )
    assert (
        mock_nomenclature_get_parent_context.handler.times_called
        == math.ceil(items_count / PARENT_CATEGORIES_BATCH_SIZE)
    )

    result = response.json()

    assert 'place_menu_items' in result
    assert len(result['place_menu_items']) == items_count

    sort_categories(result)

    items_dict = {
        item['public_id']: item for item in result['place_menu_items']
    }

    parent_category = parent_category_offset
    for i in range(1, items_count + 1):
        public_id = 'public_id_' + str(i)
        parent_category += 1

        assert public_id in items_dict
        item = items_dict[public_id]

        expected = [str(i), str(parent_category)]

        assert item['categories'] == sorted(expected)


@pytest.mark.config(EATS_PRODUCTS_SETTINGS={'discount_promo': DISCOUNT_PROMO})
async def test_nomenclature_categories_get_parent_unavailable(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
):
    # Тест проверяет, что в случае если при запросе ручки
    # utils.Handlers.NOMENCLATURE_PLACE_CATEGORIES_GET_PARENT
    # возникает проблема с сетью, таймаут или ответ кодом 500
    # eats-products все равно вернет валидный и одинаковый ответ

    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='origin_id_1', core_id=101, public_id='public_id_1',
            ),
            conftest.ProductMapping(
                origin_id='origin_id_2', core_id=102, public_id='public_id_2',
            ),
            conftest.ProductMapping(
                origin_id='origin_id_3', core_id=103, public_id='public_id_3',
            ),
        ],
    )

    mock_nomenclature_static_info_context.add_product('public_id_1')
    mock_nomenclature_static_info_context.add_product('public_id_2')
    mock_nomenclature_static_info_context.add_product('public_id_3')

    mock_nomenclature_dynamic_info_context.add_product(
        id_='public_id_1', origin_id='origin_id_1', parent_category_ids=['1'],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        id_='public_id_2', origin_id='origin_id_2', parent_category_ids=['1'],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        id_='public_id_3', origin_id='origin_id_3', parent_category_ids=['1'],
    )

    mock_nomenclature_get_parent_context.set_status(500)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': ['101', '102', '103']},
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200

    result = response.json()
    assert 'place_menu_items' in result
    assert len(result['place_menu_items']) == 3

    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_get_parent_context.handler.times_called == 1

    mock_nomenclature_get_parent_context.set_status(200)
    mock_nomenclature_get_parent_context.set_network_error(True)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': ['101', '102', '103']},
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200

    assert result == response.json()

    assert mock_nomenclature_dynamic_info_context.handler.times_called == 2
    assert mock_nomenclature_get_parent_context.handler.times_called == 2

    mock_nomenclature_get_parent_context.set_network_error(False)
    mock_nomenclature_get_parent_context.set_timeout_error(True)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': ['101', '102', '103']},
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200

    assert result == response.json()

    assert mock_nomenclature_dynamic_info_context.handler.times_called == 3
    assert mock_nomenclature_get_parent_context.handler.times_called == 3


@pytest.mark.config(EATS_PRODUCTS_SETTINGS={'discount_promo': DISCOUNT_PROMO})
async def test_get_items_v2_by_public_ids(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        several_places_products_mapping,
):
    # Тест проверяет, что при указании public_ids в запросе будут получены
    # данные именно для этих товаров, игнорируя id в поле items

    several_places_products_mapping()
    mock_nomenclature_dynamic_info_context.expected_request = {
        'product_ids': [
            'f92b147c-a05f-40df-a68b-064fbaed7059',
            '9c6b8cb2-8d1b-4d80-a5cb-f609c4b633aa',
            '45685053-db9c-4eb5-a6b2-c4f643faa4ec',
        ],
    }
    mock_nomenclature_dynamic_info_context.add_product(
        'f92b147c-a05f-40df-a68b-064fbaed7059', price=50,
    )

    mock_nomenclature_dynamic_info_context.add_product(
        '9c6b8cb2-8d1b-4d80-a5cb-f609c4b633aa', price=50,
    )

    mock_nomenclature_dynamic_info_context.add_product(
        '45685053-db9c-4eb5-a6b2-c4f643faa4ec', price=50,
    )
    mock_nomenclature_static_info_context.add_product(
        'f92b147c-a05f-40df-a68b-064fbaed7059',
    )
    mock_nomenclature_static_info_context.add_product(
        '9c6b8cb2-8d1b-4d80-a5cb-f609c4b633aa',
    )
    mock_nomenclature_static_info_context.add_product(
        '45685053-db9c-4eb5-a6b2-c4f643faa4ec',
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={
            'items': ['104'],
            'place_id': 1,
            'public_ids': [
                'f92b147c-a05f-40df-a68b-064fbaed7059',  # core id 101
                '9c6b8cb2-8d1b-4d80-a5cb-f609c4b633aa',  # core id 102
                '45685053-db9c-4eb5-a6b2-c4f643faa4ec',  # core id 103
            ],
        },
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    assert (
        {
            product['public_id']
            for product in response.json()['place_menu_items']
        }
        == {
            'f92b147c-a05f-40df-a68b-064fbaed7059',
            '9c6b8cb2-8d1b-4d80-a5cb-f609c4b633aa',
            '45685053-db9c-4eb5-a6b2-c4f643faa4ec',
        }
    )

    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_nomenclature_get_parent_context.handler.times_called == 1


async def test_get_items_v2_no_place_id(taxi_eats_products):
    # Тест проверяет, что запрос с public_id, но без place_id
    # получит в ответ BAD_REQUEST

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={
            'items': ['101'],
            'public_ids': [
                'f92b147c-a05f-40df-a68b-064fbaed7059',  # core id 101
            ],
        },
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 400
    assert response.json() == {
        'error': 'validation_error',
        'message': 'place_id is required when public_ids is presented',
    }


async def test_origin_to_public_id_mapping_not_found(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        add_place_products_mapping,
):
    # Тест проверяет что если для запрошенных core_id были найдены origin_id,
    # но затем не были найдены public_id, то ручки номенклатуры не будут
    # вызваны, а ручка get-items возвратит код 400

    add_place_products_mapping(
        [
            conftest.ProductMapping(origin_id='id_1', core_id=1),
            conftest.ProductMapping(origin_id='id_2', core_id=2),
        ],
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS, json={'items': ['1', '2']},
    )
    assert response.status_code == 400
    assert response.json()['error'] == 'place_menu_items_not_found'
    assert mock_nomenclature_static_info_context.handler.times_called == 0
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
    assert mock_nomenclature_get_parent_context.handler.times_called == 0


PRODUCT_ID_1 = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'


@pytest.mark.parametrize(
    ['expected_stock'],
    (
        pytest.param(
            None,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_SETTINGS={
                        'discount_promo': DISCOUNT_PROMO,
                        'hide_product_public_ids': [PRODUCT_ID_1],
                    },
                ),
            ],
        ),
        pytest.param(
            1,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_SETTINGS={
                        'discount_promo': DISCOUNT_PROMO,
                        'hide_product_public_ids': [PRODUCT_ID_1],
                        'hide_product_public_ids_stock': 1,
                    },
                ),
            ],
        ),
    ),
)
async def test_get_items_v2_hide_product_public_ids(
        taxi_eats_products,
        mock_nomenclature_get_parent_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        several_places_products_mapping,
        add_place_products_mapping,
        expected_stock,
):
    """
    Тест проверяет, что товары не скрываются по конфигу
    `hide_product_public_ids`, и у них проставляется available=true и
    in_stock=1, если это задано в конфиге
    """
    several_places_products_mapping()
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', core_id=1, public_id=PRODUCT_ID_1,
            ),
        ],
    )

    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_ID_1,
        price=50,
        is_available=bool(expected_stock),
        old_price=expected_stock,
    )
    mock_nomenclature_static_info_context.add_product(PRODUCT_ID_1)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': ['1']},
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200

    assert len(response.json()['place_menu_items']) == 1
    item = response.json()['place_menu_items'][0]

    if expected_stock:
        assert item['in_stock'] == expected_stock
        assert item['available'] is True
    else:
        assert 'in_stock' not in item
        assert item['available'] is False


@utils.PARAMETRIZE_WEIGHT_DATA_ROUNDING
@experiments.weight_data()
async def test_get_items_v2_weight_data(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        add_default_product_mapping,
        should_round_prices,
):
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', price=50, old_price=100,
    )
    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        measure={'unit': 'GRM', 'value': 250},
    )
    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', price=50, old_price=100,
    )
    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
        measure={'unit': 'KGRM', 'value': 3},
    )
    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', price=50, old_price=100,
    )
    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
        is_catch_weight=False,
        measure={'unit': 'GRM', 'value': 0},
    )
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': ['1', '2', '3']},
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    items = sorted(
        response.json()['place_menu_items'], key=lambda item: item['id'],
    )
    assert len(items) == 3
    assert items[0]['weight_data'] == {
        'price_per_kg': '400',
        'promo_price_per_kg': '200',
        'quantim_value_g': 250,
    }
    assert items[1]['weight_data'] == {
        'price_per_kg': '34' if should_round_prices else '33.33',
        'promo_price_per_kg': '17' if should_round_prices else '16.67',
        'quantim_value_g': 3000,
    }
    assert 'weight_data' not in items[2]


async def test_get_items_v2_no_mapping(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        add_place_products_mapping,
):
    """
    Тест проверяет, что если core_id не найден
    для public_id, то ручка не упадет с 500
    """
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='origin_id_1', core_id=101, public_id='public_id_1',
            ),
            conftest.ProductMapping(
                origin_id='origin_id_2', core_id=102, public_id='public_id_2',
            ),
            conftest.ProductMapping(
                origin_id='origin_id_3', public_id='public_id_3',
            ),
        ],
    )
    public_ids = ['public_id_1', 'public_id_2', 'public_id_3']

    for public_id in public_ids:
        mock_nomenclature_dynamic_info_context.add_product(public_id, price=5)
        mock_nomenclature_static_info_context.add_product(public_id)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': [], 'place_id': 1, 'public_ids': public_ids},
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 200


async def test_get_items_is_alcohol(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        add_default_product_mapping,
):
    """
    Тест проверяет, что если ручка статической информации о товаре вернула
    признак алкогольности для товара, то ручка get-items тоже вернет его.
    """

    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    )
    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    )
    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    )
    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', is_alcohol=True,
    )
    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    )
    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', is_alcohol=False,
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': ['1', '2', '3']},
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    items = sorted(
        response.json()['place_menu_items'], key=lambda item: item['id'],
    )
    assert len(items) == 3
    assert 'is_alcohol' not in items[0]
    assert items[1]['is_alcohol'] is True
    assert 'is_alcohol' not in items[2]


@pytest.mark.parametrize(
    'tag_name',
    (
        pytest.param(None, marks=experiments.weight_data()),
        pytest.param('tag', marks=experiments.weight_data(tag_name='tag')),
    ),
)
@pytest.mark.parametrize('tags', (['tag'], ['tag_1'], [], None))
async def test_get_items_v2_weight_tags(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        add_default_product_mapping,
        tag_name,
        tags,
):
    """
    Проверяется, что weight_data добавляется в зависимости от тегов категории
    """
    add_default_product_mapping()
    mock_nomenclature_get_parent_context.add_category(
        id_='1', parent_id=None, tags=tags,
    )
    mock_nomenclature_dynamic_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', price=50, old_price=100,
    )
    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        measure={'unit': 'GRM', 'value': 250},
    )
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': ['1']},
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    item = response.json()['place_menu_items'][0]
    if tag_name is None or (tags and tag_name in tags):
        assert 'weight_data' in item
    else:
        assert 'weight_data' not in item
    assert mock_nomenclature_get_parent_context.handler.times_called == 1


async def test_get_items_no_items_ids(taxi_eats_products):
    """
    Тест проверяет, что запрос без items и public_ids получит в ответ
    BAD_REQUEST
    """
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'items': []},
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 400
    assert response.json() == {
        'error': 'validation_error',
        'message': 'core_ids or public_ids are required in the request',
    }


@pytest.mark.pgsql('eats_products', files=[])
async def test_get_items_no_place(taxi_eats_products):
    """
    Тест проверяет, что запрос для плейса, которого нет в кэше получит в ответ
    ошибку
    """
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GET_ITEMS,
        json={'public_ids': [''], 'items': [], 'place_id': 1},
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 400
    assert response.json() == {
        'error': 'not_found_place',
        'message': 'Not found place with id 1',
    }
