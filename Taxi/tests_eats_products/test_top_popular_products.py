import copy

import pytest

from tests_eats_products import experiments
from tests_eats_products import utils


PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}


PRODUCTS_HEADERS = {
    'X-Eats-User': 'user_id=123',
    'X-AppMetrica-DeviceId': 'device_id',
}

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
]


@pytest.mark.redis_store(file='scoring_cache')
async def test_top_popular_products_save_to_redis(
        redis_store, stq_runner, load_json, mockserver,
):
    # Check, that top products in each category are saved in Redis cache

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        json = load_json('nomenclature_response.json')
        if 'category_id' not in request.query:
            return json
        for category in json['categories']:
            if category['public_id'] == int(request.query['category_id']):
                return {'categories': [category]}
        return {}

    # Run the STQ task, which should trigger the top products update
    await stq_runner.eats_products_update_nomenclature_product_mapping.call(
        task_id=str(utils.PLACE_ID), kwargs={'place_id': str(utils.PLACE_ID)},
    )

    # Check that top products are stored in Redis
    top_items_key = 'scores:top:yt_table_v3:1:44012'
    assert redis_store.exists(top_items_key)
    # Check expire time is set
    assert redis_store.ttl(top_items_key) == 234 * 60
    top_items = redis_store.zrevrange(top_items_key, 0, -1)
    assert top_items == [
        b'item_id_3',
        b'item_id_5',
        b'item_id_4',
        b'item_id_1',
    ]


@pytest.mark.parametrize(
    (),
    [
        pytest.param(id='top is empty'),
        pytest.param(
            marks=[
                pytest.mark.redis_store(file='redis_popular_products_cache'),
            ],
            id='top is not empty',
        ),
    ],
)
async def test_top_popular_products_save_without_scoring(
        redis_store, stq_runner, load_json, mockserver,
):
    # Тест проверяет, что топ продуктов в Redis не содержит данные,
    # если нет scores

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        json = load_json('nomenclature_response.json')
        if 'category_id' not in request.query:
            return json
        for category in json['categories']:
            if category['public_id'] == int(request.query['category_id']):
                return {'categories': [category]}
        return {}

    # Run the STQ task, which should trigger the top products update
    await stq_runner.eats_products_update_nomenclature_product_mapping.call(
        task_id=str(utils.PLACE_ID), kwargs={'place_id': str(utils.PLACE_ID)},
    )

    # Check that top products are stored in Redis
    top_items_key = 'scores:top:yt_table_v3:1:44012'
    assert not redis_store.exists(top_items_key)


@pytest.mark.parametrize(
    'max_items_count',
    [
        pytest.param(
            1,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {'max_popular_items_count': 1},
                    },
                ),
            ],
        ),
        pytest.param(
            2,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {'max_popular_items_count': 2},
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.redis_store(file='scoring_cache')
async def test_top_popular_products_max_items_count(
        redis_store, stq_runner, load_json, mockserver, max_items_count,
):
    # Тест проверяет работу ограничения max_popular_items_count
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature_response.json')

    await stq_runner.eats_products_update_nomenclature_product_mapping.call(
        task_id=str(utils.PLACE_ID), kwargs={'place_id': str(utils.PLACE_ID)},
    )

    # Check that only max_popular_items_count of products are stored
    top_items_key = 'scores:top:yt_table_v3:1:44012'
    assert redis_store.exists(top_items_key)
    top_items = redis_store.zrange(top_items_key, 0, -1)
    assert len(top_items) == max_items_count


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@experiments.products_scoring()
@experiments.popular_category()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_popular_products_cache')
async def test_top_popular_products_with_scores(
        taxi_eats_products,
        load_json,
        mockserver,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    # Тест проверяет ответ ручки /api/v2/menu/goods/get-categories
    # для категории "Популярное"

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        assert set(request.json['products']) == set(PUBLIC_IDS)
        return load_json('v2_place_assortment_details_response.json')

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[0],
        name='item_1',
        images=[{'url': 'url_1/{w}x{h}', 'sort_order': 0}],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[0], price=999, old_price=1000, in_stock=20,
    )
    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[1],
        name='item_2',
        images=[{'url': 'url_2/{w}x{h}', 'sort_order': 0}],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[1], price=999, old_price=1000, in_stock=99,
    )
    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[2],
        name='item_3',
        images=[{'url': 'url_3/{w}x{h}', 'sort_order': 0}],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[2], price=990, old_price=1000,
    )
    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[3],
        name='item_7',
        images=[{'url': 'url_4/{w}x{h}', 'sort_order': 0}],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[3], price=990, old_price=1000,
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return load_json('v1_product_categories_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': utils.POPULAR_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 50,
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_popular_response.json')
    if handlers_version == 'v1':
        assert _mock_eats_nomenclature_products.times_called == 1
        assert _mock_eats_nomenclature_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert _mock_eats_nomenclature_products.times_called == 0
        assert _mock_eats_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@experiments.products_scoring()
@experiments.popular_category()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_popular_products_cache')
async def test_top_popular_products_restrictions(
        taxi_eats_products,
        load_json,
        mockserver,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    # Тест проверяет работу ограничений max_items_count и min_items_count

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    for public_id in PUBLIC_IDS:
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return load_json('v1_product_categories_response.json')

    # Проверка ограничения max_items_count
    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': utils.POPULAR_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 3,
                },
            ],
        },
    )
    assert response.status_code == 200
    items_order = [
        item['public_id'] for item in response.json()['categories'][0]['items']
    ]
    assert items_order == [PUBLIC_IDS[3], PUBLIC_IDS[2], PUBLIC_IDS[1]]

    # Проверка ограничения min_items_count
    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': utils.POPULAR_CATEGORY_ID,
                    'min_items_count': 10,
                    'max_items_count': 50,
                },
            ],
        },
    )
    assert response.status_code == 200
    assert not response.json()['categories']
    if handlers_version == 'v1':
        assert _mock_eats_nomenclature_products.times_called == 1
        assert _mock_eats_nomenclature_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert _mock_eats_nomenclature_products.times_called == 0
        assert _mock_eats_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1


@experiments.products_scoring()
@experiments.popular_category()
@pytest.mark.redis_store(file='redis_popular_products_cache')
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_request_popular_category(
        taxi_eats_products, mockserver, load_json,
):
    # Тест проверяет, что если запрашивается категория "Популярное",
    # то возвращается только она.
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.POPULAR_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = response.json()['payload']['categories']
    assert len(categories) == 1
    assert categories[0]['id'] == products_request['category']
    assert (
        categories[0]['items']
        == load_json('expected_popular_response.json')['categories'][0][
            'items'
        ]
    )


@experiments.products_scoring()
@pytest.mark.experiments3(filename='min_10_products_experiment.json')
@pytest.mark.redis_store(file='redis_popular_products_cache')
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_min_restriction_on_popular_category(
        taxi_eats_products, mockserver, load_json,
):
    # Тест проверяет ограничение минимального количества продуктов
    # для категории "Популярное".
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.POPULAR_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    assert not response.json()['payload']['categories']


@experiments.products_scoring()
@pytest.mark.experiments3(filename='max_3_products_experiment.json')
@pytest.mark.redis_store(file='redis_popular_products_cache')
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_max_restriction_on_popular_category(
        taxi_eats_products, mockserver, load_json,
):
    # Тест проверяет ограничение максимального количества продуктов
    # для категории "Популярное".
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.POPULAR_CATEGORY_ID

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    items_order = [
        item['public_id']
        for item in response.json()['payload']['categories'][0]['items']
    ]
    assert items_order == [
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    ]


@experiments.products_scoring()
@experiments.popular_category()
@pytest.mark.redis_store(file='redis_popular_products_cache')
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_no_products_on_top_popular_category(
        taxi_eats_products, mockserver, load_json, taxi_config,
):
    # Тест проверяет, что категория "Популярное" не содержит
    # товары, если запрашивается корень магазина
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature_response.json')

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=PRODUCTS_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = {c['id']: c for c in response.json()['payload']['categories']}
    assert utils.POPULAR_CATEGORY_ID in categories
    assert not categories[utils.POPULAR_CATEGORY_ID]['items']


@pytest.mark.parametrize(
    (),
    [
        pytest.param(
            marks=(
                pytest.mark.redis_store(file='redis_popular_products_cache'),
            ),
            id='without popular category experiment',
        ),
        pytest.param(
            marks=(
                experiments.popular_category(enabled=False),
                pytest.mark.redis_store(file='redis_popular_products_cache'),
            ),
            id='popular category experiment disabled',
        ),
        pytest.param(
            marks=(
                pytest.mark.experiments3(
                    filename='min_10_products_experiment.json',
                ),
                pytest.mark.redis_store(file='redis_popular_products_cache'),
            ),
            id='min_products = 10',
        ),
        pytest.param(
            marks=experiments.popular_category(), id='empty redis storage',
        ),
    ],
)
@experiments.products_scoring()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_popular_category_not_returned(
        taxi_eats_products, mockserver, load_json, taxi_config,
):
    # Тест проверяет, что категория "Популярное" не отображается
    # при несоблюдении некоторых условий
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature_response.json')

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=PRODUCTS_BASE_REQUEST,
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    categories = {c['id']: c for c in response.json()['payload']['categories']}
    assert utils.POPULAR_CATEGORY_ID not in categories


@experiments.products_scoring()
@experiments.popular_category()
@pytest.mark.redis_store(file='redis_popular_products_cache')
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_popular_category_nomenclature_v2_place_404_code(
        taxi_eats_products, mock_nomenclature_v2_details_context,
):
    # Тест проверяет, что если
    # /eats-nomenclature/v2/place/assortment/details
    # возвращает 404, то ручка тоже возвращает 404
    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = utils.POPULAR_CATEGORY_ID

    mock_nomenclature_v2_details_context.set_status(status_code=404)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS,
        json=products_request,
        headers=PRODUCTS_HEADERS,
    )

    assert response.status_code == 404
    assert mock_nomenclature_v2_details_context.handler.times_called == 1


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@experiments.products_scoring()
@experiments.popular_category()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_popular_products_cache')
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS={
        'hide_product_public_ids': [PUBLIC_IDS[0], PUBLIC_IDS[1]],
    },
)
async def test_top_popular_hide_product_public_ids(
        taxi_eats_products,
        load_json,
        mockserver,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    # Тест проверяет, что в каруселях не приходят скрытые товары
    for public_id in PUBLIC_IDS:
        mock_nomenclature_static_info_context.add_product(public_id)
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        assert set(request.json['products']) == set(PUBLIC_IDS)
        return load_json('v2_place_assortment_details_response.json')

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return load_json('v1_product_categories_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': utils.POPULAR_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 50,
                },
            ],
        },
    )
    assert response.status_code == 200
    assert len(response.json()['categories'][0]['items']) == 2
    if handlers_version == 'v1':
        assert _mock_eats_nomenclature_products.times_called == 1
        assert _mock_eats_nomenclature_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert _mock_eats_nomenclature_products.times_called == 0
        assert _mock_eats_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1
