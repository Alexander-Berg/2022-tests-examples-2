import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
]


@pytest.mark.parametrize(
    ['yt_table', 'expected_order'],
    [
        pytest.param(
            'yt_table_v3',
            [b'item_id_3', b'item_id_5', b'item_id_1', b'item_id_2'],
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {
                            'top_expire_time_minutes': 234,
                            'max_discount_items_count': 100,
                        },
                    },
                ),
            ],
            id='v3_all',
        ),
        pytest.param(
            'yt_table_v2',
            [b'item_id_2', b'item_id_3', b'item_id_5', b'item_id_1'],
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {
                            'top_expire_time_minutes': 234,
                            'max_discount_items_count': 100,
                        },
                    },
                ),
            ],
            id='v2_all',
        ),
        pytest.param(
            'yt_table_v3',
            [b'item_id_3', b'item_id_5', b'item_id_1'],
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {
                            'top_expire_time_minutes': 234,
                            'max_discount_items_count': 3,
                        },
                    },
                ),
            ],
            id='v3_only_3',
        ),
        pytest.param(
            'yt_table_v2',
            [b'item_id_2', b'item_id_3', b'item_id_5'],
            marks=[
                pytest.mark.config(
                    EATS_PRODUCTS_TOP_PRODUCTS_SETTINGS={
                        '__default__': {
                            'top_expire_time_minutes': 234,
                            'max_discount_items_count': 3,
                        },
                    },
                ),
            ],
            id='v2_only_3',
        ),
    ],
)
@pytest.mark.pgsql('eats_products', files=['pg_eats_products.sql'])
@pytest.mark.redis_store(file='scoring_cache')
async def test_cache_top_discount_products_with_scores(
        load_json,
        stq_runner,
        mockserver,
        redis_store,
        yt_table,
        expected_order,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature_response.json')

    def assert_redis(table_name, items):
        key = (
            f'scores:top:{table_name}:{place_id}:{utils.DISCOUNT_CATEGORY_ID}'
        )
        assert redis_store.exists(key)
        assert redis_store.ttl(key) == 234 * 60
        redis_items = redis_store.zrevrange(key, 0, -1)
        assert redis_items == items

    place_id = 1

    await stq_runner.eats_products_update_discount_products.call(
        task_id=str(place_id),
        kwargs={'place_id': str(place_id)},
        expect_fail=False,
    )

    assert_redis(yt_table, expected_order)


@pytest.mark.redis_store(file='scoring_cache')
async def test_cache_empty_nomenclature_response(
        stq_runner, mockserver, redis_store,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return {'categories': []}

    place_id = 1

    await stq_runner.eats_products_update_discount_products.call(
        task_id=str(place_id),
        kwargs={'place_id': str(place_id)},
        expect_fail=False,
    )

    key = f'scores:top:yt_table_v3:{place_id}:{utils.DISCOUNT_CATEGORY_ID}'
    assert not redis_store.exists(key)


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@experiments.products_scoring()
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='scoring_cache')
async def test_top_discount_products_with_scores(
        taxi_eats_products,
        load_json,
        stq_runner,
        mockserver,
        redis_store,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature_response.json')

    place_id = 1
    category_id = utils.DISCOUNT_CATEGORY_ID

    await stq_runner.eats_products_update_discount_products.call(
        task_id=str(place_id),
        kwargs={'place_id': str(place_id)},
        expect_fail=False,
    )
    key = f'scores:top:yt_table_v3:{place_id}:{category_id}'
    assert redis_store.exists(key)
    redis_items = redis_store.zrevrange(key, 0, -1)
    assert redis_items == [
        b'item_id_3',
        b'item_id_5',
        b'item_id_1',
        b'item_id_2',
    ]

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
        PUBLIC_IDS[2], price=990, old_price=1000, in_stock=None,
    )

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
                    'id': category_id,
                    'min_items_count': 1,
                    'max_items_count': 4,
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_discounts_response.json')
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
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'pg_add_discount_products.sql'],
)
@pytest.mark.redis_store(file='scoring_cache')
async def test_top_discount_products_product_no_longer_discounted(
        taxi_eats_products,
        load_json,
        stq_runner,
        mockserver,
        redis_store,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature_response.json')

    place_id = 1
    category_id = utils.DISCOUNT_CATEGORY_ID

    await stq_runner.eats_products_update_discount_products.call(
        task_id=str(place_id),
        kwargs={'place_id': str(place_id)},
        expect_fail=False,
    )
    key = f'scores:top:yt_table_v3:{place_id}:{category_id}'
    assert redis_store.exists(key)
    redis_items = redis_store.zrevrange(key, 0, -1)
    assert redis_items == [
        b'item_id_3',
        b'item_id_5',
        b'item_id_1',
        b'item_id_2',
    ]

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
        PUBLIC_IDS[2], price=990, in_stock=None,
    )

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_products(request):
        assert set(request.json['products']) == set(PUBLIC_IDS)
        products_response = load_json(
            'v2_place_assortment_details_response.json',
        )
        products_response['products'][2]['old_price'] = None
        return products_response

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return load_json('v1_product_categories_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': category_id,
                    'min_items_count': 1,
                    'max_items_count': 4,
                },
            ],
        },
    )
    assert response.status_code == 200
    expected_response = load_json('expected_discounts_response.json')
    expected_items = expected_response['categories'][0]['items'][1:]
    assert response.json()['categories'][0]['items'] == expected_items
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
@pytest.mark.parametrize(
    'has_cashback',
    [
        pytest.param(
            True,
            id='has cashback',
            marks=[experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED],
        ),
        pytest.param(False, id='no cashback'),
    ],
)
@experiments.products_scoring()
@experiments.discount_category()
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.config(EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS)
@pytest.mark.redis_store(file='scoring_cache')
@pytest.mark.redis_store(
    [
        'zadd',
        f'scores:top:yt_table_v3:1:{utils.DISCOUNT_CATEGORY_ID}',
        '0.00001',
        'item_id_1',
    ],
)
async def test_top_and_discounts_from_lib(
        taxi_eats_products,
        load_json,
        mockserver,
        mock_nomenclature_v2_details_context,
        add_place_products_mapping,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        has_cashback,
):
    # Проверяется, что если есть скидки и в кеше и в либе,
    # то все эти товары возвращаются
    # И проверяется, что если кешбек включен, то он будет в ответе
    mapping = [
        conftest.ProductMapping(
            origin_id='item_id_1', core_id=1, public_id=PUBLIC_IDS[0],
        ),
        conftest.ProductMapping(
            origin_id='item_id_3', core_id=2, public_id=PUBLIC_IDS[1],
        ),
        conftest.ProductMapping(
            origin_id='item_id_4', core_id=3, public_id=PUBLIC_IDS[2],
        ),
    ]
    add_place_products_mapping(mapping)

    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[0], price=100, promo_price=90,
    )
    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[1], price=100, promo_price=90,
    )
    mock_nomenclature_v2_details_context.add_product(PUBLIC_IDS[2], price=100)

    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[0], price=90, old_price=100,
    )
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[1])
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[1], price=90, old_price=100,
    )
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[2])
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[2], price=100,
    )

    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[1], value_type='absolute', value=20,
    )
    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[2], value_type='absolute', value=30,
    )

    mock_v2_fetch_discounts_context.add_cashback_product(
        PUBLIC_IDS[1], value_type='absolute', value=22,
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
                    'id': utils.DISCOUNT_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 4,
                },
            ],
        },
    )
    assert response.status_code == 200
    assert mock_v2_fetch_discounts_context.handler.times_called == 1

    items = response.json()['categories'][0]['items']
    assert len(items) == 3
    assert [item['public_id'] for item in items] == [
        PUBLIC_IDS[1],
        PUBLIC_IDS[0],
        PUBLIC_IDS[2],
    ]
    if has_cashback:
        assert items[0]['promoTypes'][1]['value'] == 22
    else:
        assert len(items[0]['promoTypes']) == 1
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert _mock_eats_nomenclature_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert _mock_eats_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@experiments.products_scoring()
@experiments.discount_category()
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.redis_store(file='scoring_cache')
async def test_discounts_only_from_lib(
        taxi_eats_products,
        load_json,
        mockserver,
        mock_nomenclature_v2_details_context,
        add_place_products_mapping,
        mock_v2_fetch_discounts_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
):
    # Проверяется, что если есть в кеше нет скидок, но есть в либе,
    # то они будут возвращены
    mapping = [
        conftest.ProductMapping(
            origin_id='item_id_3', core_id=2, public_id=PUBLIC_IDS[0],
        ),
        conftest.ProductMapping(
            origin_id='item_id_4', core_id=3, public_id=PUBLIC_IDS[1],
        ),
    ]
    add_place_products_mapping(mapping)

    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[0], price=100, promo_price=90,
    )
    mock_nomenclature_v2_details_context.add_product(PUBLIC_IDS[1], price=100)

    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[0], price=90, old_price=100,
    )
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[1])
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[1], price=100,
    )

    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[0], value_type='absolute', value=20,
    )
    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[1], value_type='absolute', value=30,
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
                    'id': utils.DISCOUNT_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 4,
                },
            ],
        },
    )
    assert response.status_code == 200
    assert mock_v2_fetch_discounts_context.handler.times_called == 1

    items = response.json()['categories'][0]['items']
    assert len(items) == 2
    assert [item['public_id'] for item in items] == [
        PUBLIC_IDS[0],
        PUBLIC_IDS[1],
    ]
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert _mock_eats_nomenclature_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert _mock_eats_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@pytest.mark.parametrize(
    'match_called',
    [
        pytest.param(
            True,
            id='category disabled',
            marks=[
                experiments.discount_category(enabled=False),
                experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED,
            ],
        ),
        pytest.param(
            False, id='lib disabled', marks=[experiments.discount_category()],
        ),
    ],
)
@experiments.products_scoring()
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.redis_store(file='scoring_cache')
@pytest.mark.redis_store(
    [
        'zadd',
        f'scores:top:yt_table_v3:1:{utils.DISCOUNT_CATEGORY_ID}',
        '0.00001',
        'item_id_1',
    ],
)
async def test_no_fetching_discounts(
        taxi_eats_products,
        load_json,
        mockserver,
        mock_nomenclature_v2_details_context,
        add_place_products_mapping,
        mock_v2_fetch_discounts_context,
        mock_v2_match_discounts_context,
        eats_order_stats,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        match_called,
):
    # Проверяется, если либа выключена, то скидки оттуда не будут в ответе
    mapping = [
        conftest.ProductMapping(
            origin_id='item_id_1', core_id=2, public_id=PUBLIC_IDS[0],
        ),
        conftest.ProductMapping(
            origin_id='item_id_3', core_id=3, public_id=PUBLIC_IDS[1],
        ),
    ]
    add_place_products_mapping(mapping)

    mock_nomenclature_v2_details_context.add_product(
        PUBLIC_IDS[0], price=100, promo_price=90,
    )
    mock_nomenclature_v2_details_context.add_product(PUBLIC_IDS[1], price=100)

    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[0])
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[0], price=90, old_price=100,
    )
    mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[1])
    mock_nomenclature_dynamic_info_context.add_product(
        PUBLIC_IDS[1], price=100,
    )

    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[0], value_type='absolute', value=20,
    )
    mock_v2_fetch_discounts_context.add_discount_product(
        PUBLIC_IDS[1], value_type='absolute', value=30,
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
                    'id': utils.DISCOUNT_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 4,
                },
            ],
        },
    )
    assert response.status_code == 200
    assert mock_v2_fetch_discounts_context.handler.times_called == 0
    assert mock_v2_match_discounts_context.handler.times_called == match_called

    items = response.json()['categories'][0]['items']
    assert len(items) == 1
    assert [item['public_id'] for item in items] == [PUBLIC_IDS[0]]
    assert items[0]['promoPrice'] == 90
    if handlers_version == 'v1':
        assert mock_nomenclature_v2_details_context.handler.times_called == 1
        assert _mock_eats_nomenclature_categories.times_called == 1
        assert mock_nomenclature_static_info_context.handler.times_called == 0
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 0
        assert mock_nomenclature_get_parent_context.handler.times_called == 0
    else:
        assert mock_nomenclature_v2_details_context.handler.times_called == 0
        assert _mock_eats_nomenclature_categories.times_called == 0
        assert mock_nomenclature_static_info_context.handler.times_called == 1
        assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
        assert mock_nomenclature_get_parent_context.handler.times_called == 1
