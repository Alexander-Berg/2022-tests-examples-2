import pytest

from tests_eats_products import experiments
from tests_eats_products import utils

CATEGORY_ID = '123'
PLACE_ID = 1
INTEGER_ID = {'id': int(CATEGORY_ID)}
STRING_ID = {'uid': CATEGORY_ID}
PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
]


@pytest.mark.config(
    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
        '__default__': {
            'categories': [101, 105, 109],
            'top_expire_time_minutes': 234,
        },
    },
)
@pytest.mark.redis_store(file='scoring_cache')
async def test_top_products_save_to_redis(
        redis_store, stq_runner, load_json, mockserver,
):
    """Check, that top products in each category are saved in Redis cache"""

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature_response.json')

    # Run the STQ task, which should trigger the top products update
    await stq_runner.eats_products_update_nomenclature_product_mapping.call(
        task_id=str(PLACE_ID), kwargs={'place_id': str(PLACE_ID)},
    )

    # Check that top products are stored in Redis, for two categories
    top_items_key = 'scores:top:yt_table_v3:1:101'
    assert redis_store.exists(top_items_key)
    assert redis_store.ttl(top_items_key) == 234 * 60
    top_items = redis_store.zrevrange(top_items_key, 0, -1)
    assert top_items == [
        # product is not available but still in top
        b'item_id_5',
        b'item_id_4',
        # scoring data for this product is absent, so it is in the tail
        b'item_id_2',
    ]

    # The following categories are nested and not present in the mapping
    top_items_key = 'scores:top:yt_table_v3:1:109'
    assert not redis_store.exists(top_items_key)
    top_items_key = 'scores:top:yt_table_v3:1:105'
    assert not redis_store.exists(top_items_key)


@pytest.mark.parametrize(
    ('expected_prepared', 'expected_not_prepared'),
    [
        pytest.param(
            (),
            (101, 105),
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={'__default__': {}},
                ),
            ],
        ),
        pytest.param(
            (),
            (101, 105),
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {'categories': []},
                    },
                ),
            ],
        ),
        pytest.param(
            (101,),
            (105,),
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '1': {'categories': [101]},
                    },
                ),
            ],
        ),
        pytest.param(
            (),
            (101, 105),
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {'categories': [101]},
                        '1': {'categories': []},
                    },
                ),
            ],
        ),
        pytest.param(
            (101,),
            (105,),
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {'categories': []},
                        '1': {'categories': [101]},
                    },
                ),
            ],
        ),
        pytest.param(
            (),
            (105, 101),
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {'categories': [101]},
                        '1': {},
                    },
                ),
            ],
        ),
        pytest.param(
            (101,),
            (105, 109),
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {'add_top_level_categories': True},
                    },
                ),
                pytest.mark.redis_store(
                    [
                        'hset',
                        'scores:brands:yt_table_v3:1',
                        'item_id_2',
                        '0.0012667591308368007',
                    ],
                ),
            ],
            id='top level categories',
        ),
    ],
)
@pytest.mark.redis_store(file='scoring_cache')
async def test_top_products_filter_categories(
        redis_store,
        stq_runner,
        load_json,
        mockserver,
        expected_prepared,
        expected_not_prepared,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature_response.json')

    await stq_runner.eats_products_update_nomenclature_product_mapping.call(
        task_id=str(PLACE_ID), kwargs={'place_id': str(PLACE_ID)},
    )

    # Check that top products are stored in Redis, for enabled categories
    for cat_id in expected_prepared:
        assert redis_store.exists(f'scores:top:yt_table_v3:1:{cat_id}')

    # No scoring data for not enabled categories
    for cat_id in expected_not_prepared:
        assert not redis_store.exists(f'scores:top:yt_table_v3:1:{cat_id}')


@pytest.mark.parametrize(
    'max_items_count',
    [
        pytest.param(
            1,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {
                            'categories': [101],
                            'max_items_count': 1,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            2,
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {
                            'categories': [101],
                            'max_items_count': 2,
                        },
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.redis_store(file='scoring_cache')
async def test_top_products_max_items_count(
        redis_store, stq_runner, load_json, mockserver, max_items_count,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature_response.json')

    await stq_runner.eats_products_update_nomenclature_product_mapping.call(
        task_id=str(PLACE_ID), kwargs={'place_id': str(PLACE_ID)},
    )

    # Check that only max_items_count of products are stored
    top_items_key = 'scores:top:yt_table_v3:1:101'
    assert redis_store.exists(top_items_key)
    top_items = redis_store.zrange(top_items_key, 0, -1)
    assert len(top_items) == max_items_count


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize('category_id', (INTEGER_ID, STRING_ID))
@experiments.products_scoring()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_top_products_cache')
async def test_top_products_get_categories_min_max(
        load_json,
        mockserver,
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        category_id,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        assert set(request.json['products']) == set(PUBLIC_IDS)
        return load_json('v2_place_assortment_details_response.json')

    is_available = [True, True, False]
    for i in range(3):
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[i])
        mock_nomenclature_dynamic_info_context.add_product(
            PUBLIC_IDS[i], is_available=is_available[i],
        )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        assert set(
            {val['origin_id'] for val in request.json['products']},
        ) == set(['item_id_4', 'item_id_2', 'item_id_3', 'item_id_1'])
        return load_json('v1_product_categories_response.json')

    mock_nomenclature_get_parent_context.add_category(CATEGORY_ID)

    # Check for min compliance
    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {**category_id, 'min_items_count': 3, 'max_items_count': 4},
            ],
        },
    )
    assert response.status_code == 200
    assert not response.json()['categories']

    # Check for max compliance
    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {**category_id, 'min_items_count': 1, 'max_items_count': 1},
            ],
        },
    )
    assert response.status_code == 200
    assert len(response.json()['categories'][0]['items']) == 1
    if handlers_version == 'v1':
        assert _mock_eats_nomenclature_products.times_called == 2
        assert _mock_eats_nomenclature_categories.times_called == 2
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert _mock_eats_nomenclature_products.times_called == 0
        assert _mock_eats_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 2
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 2
        assert mock_nomenclature_get_parent_context.handler.times_called == 2


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize('category_id', (INTEGER_ID, STRING_ID))
@experiments.products_scoring()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_top_products_cache')
async def test_top_products_get_categories_happy_path(
        load_json,
        mockserver,
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        category_id,
        handlers_version,
):
    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[0],
        name='item_1',
        images=[{'url': 'url_1/{w}x{h}', 'sort_order': 0}],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[0], price=999, in_stock=20,
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
        PUBLIC_IDS[2], name='item_3',
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[2], is_available=False, in_stock=None,
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        assert set(request.json['products']) == set(PUBLIC_IDS)
        return load_json('v2_place_assortment_details_response.json')

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        assert set(
            {val['origin_id'] for val in request.json['products']},
        ) == set(['item_id_4', 'item_id_2', 'item_id_3', 'item_id_1'])
        return load_json('v1_product_categories_response.json')

    mock_nomenclature_get_parent_context.add_category(CATEGORY_ID)

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {**category_id, 'min_items_count': 1, 'max_items_count': 4},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
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
@pytest.mark.parametrize('category_id', (INTEGER_ID, STRING_ID))
@experiments.products_scoring()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_top_products_cache')
async def test_top_products_no_available_products(
        load_json,
        mockserver,
        taxi_eats_products,
        category_id,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[0], is_available=False,
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        resp = load_json('v2_place_assortment_details_response.json')
        for product in resp['products']:
            product['is_available'] = False
        return resp

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return load_json('v1_product_categories_response.json')

    mock_nomenclature_get_parent_context.add_category(CATEGORY_ID)

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {**category_id, 'min_items_count': 1, 'max_items_count': 4},
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


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize('category_id', (INTEGER_ID, STRING_ID))
@experiments.products_scoring()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
async def test_top_products_no_data_in_redis(
        load_json,
        mockserver,
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        category_id,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    mock_nomenclature_static_info_context.add_product(
        PUBLIC_IDS[0],
        name='item_1',
        images=[{'url': 'url_1/{w}x{h}', 'sort_order': 0}],
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[0], price=999, in_stock=20,
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
        PUBLIC_IDS[2], name='item_3',
    )
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[2], is_available=False, in_stock=None,
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return load_json('v1_product_categories_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {**category_id, 'min_items_count': 1, 'max_items_count': 4},
            ],
        },
    )
    assert response.status_code == 200
    assert not response.json()['categories']
    assert _mock_eats_nomenclature_products.times_called == 0
    assert _mock_eats_nomenclature_categories.times_called == 0
    assert mock_nomenclature_static_info_context.handler.times_called == 0
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
    assert mock_nomenclature_get_parent_context.handler.times_called == 0


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize('category_id', (INTEGER_ID, STRING_ID))
@pytest.mark.parametrize('response_code', [404, 500])
@experiments.products_scoring()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_top_products_cache')
async def test_top_products_nomenclature_categories_bad_response(
        load_json,
        mockserver,
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        category_id,
        response_code,
):
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(PUBLIC_IDS[0])

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return mockserver.make_response('bad request', status=response_code)

    mock_nomenclature_get_parent_context.set_status(response_code)

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {**category_id, 'min_items_count': 1, 'max_items_count': 4},
            ],
        },
    )
    assert response.status_code == response_code
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
@pytest.mark.parametrize('category_id', (INTEGER_ID, STRING_ID))
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_top_products_cache')
async def test_top_products_no_scoring_exp(
        load_json,
        mockserver,
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        category_id,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        return load_json('v2_place_assortment_details_response.json')

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return load_json('v1_product_categories_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {**category_id, 'min_items_count': 1, 'max_items_count': 4},
            ],
        },
    )
    assert response.status_code == 200

    assert response.json()['categories'] == []

    assert _mock_eats_nomenclature_products.times_called == 0
    assert _mock_eats_nomenclature_categories.times_called == 0
    assert mock_nomenclature_static_info_context.handler.times_called == 0
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
    assert mock_nomenclature_get_parent_context.handler.times_called == 0


@pytest.mark.config(
    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={'__default__': {'categories': [1]}},
)
@experiments.products_scoring()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(
    ['zadd', 'scores:top:yt_table_v3:1:1', '0.00001', 'item_id_1'],
)
async def test_top_products_delete(mockserver, stq_runner, redis_store):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return {
            'categories': [
                {
                    'available': True,
                    'id': 'category_id_1',
                    'images': [],
                    'items': [],
                    'name': 'name',
                    'parent_id': None,
                    'parent_public_id': None,
                    'public_id': 1,
                    'sort_order': 0,
                },
            ],
        }

    top_items_key = 'scores:top:yt_table_v3:1:1'
    assert redis_store.exists(top_items_key)
    # Run the STQ task, which should trigger the top products update
    await stq_runner.eats_products_update_nomenclature_product_mapping.call(
        task_id=str(PLACE_ID), kwargs={'place_id': str(PLACE_ID)},
    )

    assert not redis_store.exists(top_items_key)


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@experiments.products_scoring()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='redis_top_products_cache')
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS={'hide_product_public_ids': [PUBLIC_IDS[0]]},
)
async def test_top_products_hide_product_public_ids(
        load_json,
        mockserver,
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    for i in range(2):
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[i])
        mock_nomenclature_dynamic_info_context.add_product(PUBLIC_IDS[i])

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        assert set(request.json['products']) == set(PUBLIC_IDS)
        return load_json('v2_place_assortment_details_response.json')

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return load_json('v1_product_categories_response.json')

    mock_nomenclature_get_parent_context.add_category(CATEGORY_ID)

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {**INTEGER_ID, 'min_items_count': 1, 'max_items_count': 10},
            ],
        },
    )
    assert response.status_code == 200
    assert len(response.json()['categories'][0]['items']) == 1
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


@utils.PARAMETRIZE_WEIGHT_DATA_ROUNDING
@experiments.weight_data()
@experiments.products_scoring()
@pytest.mark.redis_store(file='redis_top_products_cache')
async def test_top_products_weight_data(
        load_json,
        mockserver,
        taxi_eats_products,
        add_default_product_mapping,
        mock_nomenclature_v2_details_context,
        should_round_prices,
):
    add_default_product_mapping()
    product_public_id = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
    mock_nomenclature_v2_details_context.add_product(
        product_public_id,
        price=101,
        promo_price=49,
        measure={'unit': 'KGRM', 'value': 2},
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return load_json('v1_product_categories_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {'id': 123, 'min_items_count': 1, 'max_items_count': 10},
            ],
        },
    )
    assert response.status_code == 200
    items = response.json()['categories'][0]['items']
    assert len(items) == 1
    assert items[0]['weight_data'] == {
        'price_per_kg': '51' if should_round_prices else '50.5',
        'promo_price_per_kg': '25' if should_round_prices else '24.5',
        'quantim_value_g': 2000,
    }


@pytest.mark.parametrize(
    'menu_request',
    [
        pytest.param({'slug': '&'}, id='wrong_slug_1'),
        pytest.param({'slug': 'ghjijhj_2&'}, id='wrong_slug_2'),
        pytest.param({'slug': 'ghjijhj_2 '}, id='wrong_slug_3'),
        pytest.param({'slug': 'ghjijhj_2о'}, id='wrong_slug_4'),
        pytest.param({'slug': ''}, id='wrong_slug_5'),
        pytest.param(
            {
                'slug': 'slug',
                'category': {'uid': 'x' * 300},
                'min_items_count': 1,
                'max_items_count': 10,
            },
            id='wrong_category_uid',
        ),
    ],
)
async def test_get_categories_wrong_request(taxi_eats_products, menu_request):
    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES, json=menu_request,
    )
    assert response.status_code == 400
