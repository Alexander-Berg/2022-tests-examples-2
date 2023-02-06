# pylint: disable=import-error
# pylint: disable=too-many-lines

from grocery_mocks import grocery_menu as mock_grocery_menu
import pytest

from tests_grocery_caas_promo import common
from tests_grocery_caas_promo import experiments


def _check_hierarchy_names(request):
    assert sorted(request.json['hierarchy_names']) == sorted(
        ['bundle_discounts', 'menu_discounts'],
    )


EMPTY_TREE = common.build_tree([])


def build_expiring_products(enabled):
    return pytest.mark.experiments3(
        name='grocery_caas_promo_build_expiring_subcategory',
        consumers=['grocery-caas-promo/discounts'],
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        is_config=False,
    )


@pytest.mark.parametrize('pigeon_data_enabled', [True, False])
async def test_single_group_discounts(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
        pigeon_data_enabled,
):
    grocery_products.products_response_enabled = not pigeon_data_enabled
    grocery_products.menu_response_enabled = pigeon_data_enabled

    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='subcategory_1')
    virtual_category.add_subcategory(subcategory_id='subcategory_2')
    virtual_category.add_subcategory(subcategory_id='subcategory_3')

    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [
                {
                    'id': 'subcategory_1',
                    'products': ['product_1', 'product_2'],
                },
                {
                    'id': 'subcategory_2',
                    'products': ['product_3', 'product_4'],
                },
                {
                    'id': 'subcategory_3',
                    'products': ['product_1', 'product_4'],
                },
            ],
        ),
    )
    grocery_discounts.add_money_discount(
        product_id='subcategory_1',
        value_type='absolute',
        value='10',
        is_subcategory=True,
    )
    grocery_discounts.add_money_discount(
        product_id='subcategory_3',
        value_type='absolute',
        value='10',
        is_subcategory=True,
    )
    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST
        | {'pigeon_data_enabled': pigeon_data_enabled},
    )
    assert response.status == 200
    assert [item['id'] for item in response.json()['items']] == [
        'group_category-group-1',
        'product_1',
        'product_2',
        'product_4',
    ]
    assert sorted(
        [item['product_id'] for item in response.json()['products']],
    ) == ['product_1', 'product_2', 'product_4']
    assert (
        [
            (item['subcategory_id'], item['keyset_tanker_key']['keyset'])
            for item in response.json()['subcategories']
        ]
        == [
            (
                'group_category-group-1',
                'pigeon_catalog' if pigeon_data_enabled else 'virtual_catalog',
            ),
        ]
    )


async def test_multiple_groups_discounts(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
):
    layout = grocery_products.add_layout(test_id='1')
    group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = group_1.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(subcategory_id='subcategory_1')
    virtual_category_1.add_subcategory(subcategory_id='subcategory_2')
    group_2 = layout.add_category_group(test_id='2')
    virtual_category_2 = group_2.add_virtual_category(test_id='2')
    virtual_category_2.add_subcategory(subcategory_id='subcategory_1')
    virtual_category_2.add_subcategory(subcategory_id='subcategory_2')
    virtual_category_2.add_subcategory(subcategory_id='subcategory_3')

    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [
                {
                    'id': 'subcategory_1',
                    'products': ['product_1', 'product_2'],
                },
                {
                    'id': 'subcategory_2',
                    'products': ['product_3', 'product_4'],
                },
                {
                    'id': 'subcategory_3',
                    'products': ['product_5', 'product_6'],
                },
            ],
        ),
    )
    grocery_discounts.add_money_discount(
        product_id='subcategory_1',
        value_type='absolute',
        value='10',
        is_subcategory=True,
    )
    grocery_discounts.add_money_discount(
        product_id='subcategory_2',
        value_type='absolute',
        value='10',
        is_subcategory=True,
    )
    grocery_discounts.add_money_discount(
        product_id='subcategory_3',
        value_type='absolute',
        value='10',
        is_subcategory=True,
    )
    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 200
    assert [item['id'] for item in response.json()['items']] == [
        'group_category-group-1',
        'product_1',
        'product_2',
        'product_3',
        'product_4',
        'group_category-group-2',
        'product_5',
        'product_6',
    ]
    assert sorted(
        [item['product_id'] for item in response.json()['products']],
    ) == ['product_' + str(i) for i in range(1, 7)]
    assert (
        sorted(
            [
                (item['subcategory_id'], item['tanker_key'])
                for item in response.json()['subcategories']
            ],
        )
        == [
            (
                'group_category-group-' + str(i),
                'category_group_title_' + str(i),
            )
            for i in range(1, 3)
        ]
    )


async def test_more_discounts(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
):
    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='subcategory_1')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [{'id': 'subcategory_2', 'products': ['product_1', 'product_2']}],
        ),
    )
    grocery_discounts.add_money_discount(
        product_id='product_1',
        value_type='absolute',
        value='10',
        is_subcategory=False,
    )
    grocery_discounts.add_money_discount(
        product_id='product_2',
        value_type='absolute',
        value='10',
        is_subcategory=False,
    )
    # not in category-tree will be filtered
    grocery_discounts.add_money_discount(
        product_id='product_not_in_tree',
        value_type='absolute',
        value='10',
        is_subcategory=False,
    )
    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json={'depot': common.DEPOT, 'layout_id': 'layout-1'},
    )

    assert response.status == 200
    assert [item['id'] for item in response.json()['items']] == [
        'promo-more-discounts',
        'product_1',
        'product_2',
    ]
    assert sorted(
        [item['product_id'] for item in response.json()['products']],
    ) == ['product_1', 'product_2']
    assert response.json()['subcategories'] == [
        {
            'subcategory_id': 'promo-more-discounts',
            'tanker_key': 'promo-more-discounts',
            'keyset_tanker_key': {
                'key': 'promo-more-discounts',
                'keyset': 'virtual_catalog',
            },
        },
    ]


# Протаскивает метки из эксперимента 3.0 в скидки
@experiments.GROCERY_DISCOUNTS_LABELS
@pytest.mark.config(
    GROCERY_DISCOUNTS_LABELS_EXPERIMENTS=[
        {'name': 'grocery_discounts_labels', 'experiment_type': 'config'},
    ],
)
async def test_fetch_discounts_experiment_labels(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_products,
        mockserver,
):
    grocery_products.add_layout(test_id='1')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'], category_tree=EMPTY_TREE,
    )

    @mockserver.json_handler('/grocery-discounts/v4/fetch-discounted-products')
    def _mock_grocery_discounts(request):
        assert request.json['experiments'] == ['from_user_id']
        _check_hierarchy_names(request)
        return mockserver.make_response(json={'items': []}, status=200)

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        headers=experiments.GROCERY_DISCOUNTS_LABELS_HEADERS,
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status_code == 200


# Проверяем выдачу сервиса скидок по частям
@pytest.mark.config(GROCERY_P13N_FETCH_DISCOUNTS_LIMIT=1)
async def test_fetch_discounts_by_parts(
        taxi_grocery_caas_promo,
        mockserver,
        overlord_catalog,
        grocery_products,
):
    grocery_products.add_layout(test_id='1')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [
                {
                    'id': 'subcategory_1',
                    'products': [f'product-{i}' for i in range(0, 5)],
                },
            ],
        ),
    )

    @mockserver.json_handler('/grocery-discounts/v4/fetch-discounted-products')
    def mock_grocery_discounts(request):
        _check_hierarchy_names(request)
        iteration_number = (
            request.json['iteration_number']
            if 'iteration_number' in request.json
            else 0
        )
        assert request.json['limit'] == 1
        discount_response = {
            'items': [
                {
                    'hierarchy_name': 'menu_discounts',
                    'products': [f'product-{iteration_number}'],
                },
            ],
            'count_iteration': 5,
        }
        return discount_response

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status_code == 200
    assert [item['id'] for item in response.json()['items']] == [
        'promo-more-discounts',
    ] + [f'product-{i}' for i in range(0, 5)]
    assert mock_grocery_discounts.times_called == 5


# Протаскивает теги пользователя в скидки
async def test_fetch_discounts_user_tags(
        taxi_grocery_caas_promo,
        grocery_tags,
        overlord_catalog,
        mockserver,
        grocery_products,
):
    grocery_products.add_layout(test_id='1')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'], category_tree=EMPTY_TREE,
    )
    personal_phone_id = 'test_phone_id'
    tags = ['tag_1', 'tag_2']
    grocery_tags.add_tags(personal_phone_id=personal_phone_id, tags=tags)

    @mockserver.json_handler('/grocery-discounts/v4/fetch-discounted-products')
    def mock_grocery_discounts(request):
        assert request.json['tags'] == tags
        _check_hierarchy_names(request)
        return mockserver.make_response(json={'items': []}, status=200)

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        headers={'X-YaTaxi-User': f'personal_phone_id={personal_phone_id}'},
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1


# Проверяем что кол-во заказов пользователя отдается в g-discounts
@pytest.mark.parametrize(
    'marketing_response',
    [
        {'json': {'usage_count': 1}, 'status': 200},
        {'json': {'message': 'error'}, 'status': 500},
    ],
)
async def test_orders_count_to_discounts(
        taxi_grocery_caas_promo,
        mockserver,
        grocery_tags,
        overlord_catalog,
        marketing_response,
        grocery_products,
):
    grocery_products.add_layout(test_id='1')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'], category_tree=EMPTY_TREE,
    )
    personal_phone_id = 'test_phone_id'

    @mockserver.json_handler('/grocery-discounts/v4/fetch-discounted-products')
    def mock_grocery_discounts(request):
        _check_hierarchy_names(request)
        if marketing_response['status'] == 200:
            assert request.json['orders_counts'][0] == {
                'orders_count': 1,
                'payment_method': 'All',
                'application_name': 'All',
            }
        else:
            assert 'orders_counts' not in request.json
        return mockserver.make_response(json={'items': []}, status=200)

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v2/tag/retrieve',
    )
    def mock_grocery_marketing(request):
        return mockserver.make_response(
            json=marketing_response['json'],
            status=marketing_response['status'],
        )

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        headers={
            'X-YaTaxi-User': f'personal_phone_id={personal_phone_id}',
            'X-Yandex-UID': 'test_yuid',
        },
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1
    assert mock_grocery_marketing.times_called == 1


async def test_discounts_unavailable(
        taxi_grocery_caas_promo,
        overlord_catalog,
        mockserver,
        grocery_products,
):
    grocery_products.add_layout(test_id='1')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [
                {
                    'id': 'subcategory_1',
                    'products': ['product_1', 'product_2'],
                },
                {
                    'id': 'subcategory_2',
                    'products': ['product_3', 'product_4'],
                },
                {
                    'id': 'subcategory_3',
                    'products': ['product_1', 'product_4'],
                },
            ],
        ),
    )

    @mockserver.json_handler('/grocery-discounts/v4/fetch-discounted-products')
    def _mock_grocery_discounts(request):
        return mockserver.make_response(json='fails', status=500)

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 500
    assert response.json()['code'] == 'GROCERY_DISCOUNTS_ERROR'


@pytest.mark.config(
    OVERLORD_CATALOG_REGION_IDS_BY_COUNTRY_ID=[
        {'country_id': 225, 'region_ids': [213]},
    ],
)
async def test_suppliers_discounts(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
):
    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='subcategory_1')

    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [{'id': 'subcategory_1', 'products': ['product_1', 'product_2']}],
        ),
    )
    grocery_discounts.add_money_discount(
        product_id='product_1',
        value_type='absolute',
        value='10',
        hierarchy_name='suppliers_discounts',
    )
    grocery_discounts.add_money_discount(
        product_id='product_2',
        value_type='absolute',
        value='10',
        hierarchy_name='suppliers_discounts',
    )
    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 200
    assert [item['id'] for item in response.json()['items']] == [
        'group_category-group-1',
        'product_1',
        'product_2',
    ]
    assert sorted(
        [item['product_id'] for item in response.json()['products']],
    ) == ['product_1', 'product_2']
    assert sorted(
        [item['subcategory_id'] for item in response.json()['subcategories']],
    ) == ['group_category-group-1']


def _format_store_item_id(depot_id, product_id):
    return f'{depot_id}_{product_id}'


# Проверяем выдачу подкатегории с товарами с истекающими сроками годности.
# Товар с истекающим сроком годности должен обладать тегом и этот тег должен
# соответсвовать скидки с флагом is_expiring = True. Так же товар должен
# быть в кеше expiring-products-cache которая строится походом в cold-storage
@build_expiring_products(enabled=True)
@pytest.mark.config(
    GROCERY_CAAS_PROMO_BUILD_EXPIRING_CACHE_SETTINGS={
        'batch_update_size': 100,
        'update_enabled': True,
    },
)
@pytest.mark.config(
    OVERLORD_CATALOG_REGION_IDS_BY_COUNTRY_ID=[
        {'country_id': 225, 'region_ids': [213]},
    ],
)
@pytest.mark.parametrize('tags_response_with_error', [True, False])
async def test_expiring_discounts_subcategory(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
        grocery_tags,
        tags_response_with_error,
        mockserver,
):
    # only product_1 and product_3 has tag related to expiring discount
    # only product_1 and product_2 in expiring products cache
    # as result only product-1 will be in handler response

    product_1 = 'product_1'
    product_2 = 'product_2'
    product_3 = 'product_3'
    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='subcategory_1')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [
                {
                    'id': 'subcategory_1',
                    'products': [product_1, product_2, product_3],
                },
            ],
        ),
    )

    grocery_tags.add_store_item_id_tag(
        store_item_id=_format_store_item_id(
            common.DEPOT['depot_id'], product_1,
        ),
        tag='tag_1',
    )
    grocery_tags.add_store_item_id_tag(
        store_item_id=_format_store_item_id(
            common.DEPOT['depot_id'], product_2,
        ),
        tag='tag_2',
    )
    grocery_tags.add_store_item_id_tag(
        store_item_id=_format_store_item_id(
            common.DEPOT['depot_id'], product_3,
        ),
        tag='tag_3',
    )
    grocery_discounts.add_money_discount(
        product_id='tag_1',
        value_type='absolute',
        value='10',
        hierarchy_name='dynamic_discounts',
        discount_meta={'is_expiring': True},
    )
    grocery_discounts.add_money_discount(
        product_id='tag_2',
        value_type='absolute',
        value='10',
        hierarchy_name='dynamic_discounts',
    )
    grocery_discounts.add_money_discount(
        product_id='tag_3',
        value_type='absolute',
        value='10',
        hierarchy_name='dynamic_discounts',
        discount_meta={'is_expiring': True},
    )

    grocery_tags.set_response_with_error(is_error=tags_response_with_error)

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/cold-storage/v1/get/'
        'expiring-products',
    )
    def _mock_cold_storage(request):
        return {
            'items': [
                {
                    'product_id': product_1,
                    'store_wms_id': common.DEPOT['depot_id'],
                },
                {
                    'product_id': product_2,
                    'store_wms_id': common.DEPOT['depot_id'],
                },
            ],
        }

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 200
    if tags_response_with_error:
        assert not response.json()['items']
    else:
        assert [item['id'] for item in response.json()['items']] == [
            'promo-expiring-products',
            'product_1',
        ]
        assert sorted(
            [item['product_id'] for item in response.json()['products']],
        ) == ['product_1']
        assert sorted(
            [
                item['subcategory_id']
                for item in response.json()['subcategories']
            ],
        ) == ['promo-expiring-products']


# Проверяем выдачу подкатегории с товарами с истекающими сроками годности.
# Если значение grocery_caas_promo_build_expiring_subcategory = false
# то товары с истекающем сроком годности не возвращаются
@build_expiring_products(enabled=False)
@pytest.mark.config(
    OVERLORD_CATALOG_REGION_IDS_BY_COUNTRY_ID=[
        {'country_id': 225, 'region_ids': [213]},
    ],
)
async def test_expiring_discounts_subcategory_disabled(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
        grocery_tags,
):
    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='subcategory_1')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [{'id': 'subcategory_1', 'products': ['product_1', 'product_2']}],
        ),
    )

    # only product-1 has tag related to expiring discount
    grocery_tags.add_store_item_id_tag(
        store_item_id=_format_store_item_id(
            common.DEPOT['depot_id'], 'product_1',
        ),
        tag='tag_1',
    )
    grocery_discounts.add_money_discount(
        product_id='tag_1',
        value_type='absolute',
        value='10',
        hierarchy_name='dynamic_discounts',
        discount_meta={'is_expiring': True},
    )

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 200
    assert not response.json()['items']


# Проверяем что группы с флагом skip_caas_usage не используются
# при разбивке товаров по прилавкам
async def test_skip_group(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
):
    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(
        test_id='1', item_meta='{"skip_in_caas_promo": true}',
    )
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='subcategory_1')

    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [{'id': 'subcategory_1', 'products': ['product_1', 'product_2']}],
        ),
    )
    grocery_discounts.add_money_discount(
        product_id='subcategory_1',
        value_type='absolute',
        value='10',
        is_subcategory=True,
    )
    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 200
    assert [item['id'] for item in response.json()['items']] == [
        'promo-more-discounts',
        'product_1',
        'product_2',
    ]


# Если продукты лежат в игнорируемой подкатегории,
# то они переходят в больше скидок
@pytest.mark.config(
    GROCERY_CAAS_PROMO_IGNORED_SUBCATEGORIES=['ignored_subcategory'],
)
async def test_ignored_subcategory_products(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
):
    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='ignored_subcategory')
    virtual_category.add_subcategory(subcategory_id='subcategory')

    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [
                {
                    'id': 'ignored_subcategory',
                    'products': ['product_1', 'product_2'],
                },
                {'id': 'subcategory', 'products': ['product_3', 'product_4']},
            ],
        ),
    )
    grocery_discounts.add_money_discount(
        product_id='product_1',
        value_type='absolute',
        value='10',
        is_subcategory=False,
    )
    grocery_discounts.add_money_discount(
        product_id='subcategory',
        value_type='absolute',
        value='10',
        is_subcategory=True,
    )
    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 200
    assert [item['id'] for item in response.json()['items']] == [
        'group_category-group-1',
        'product_3',
        'product_4',
        'promo-more-discounts',
        'product_1',
    ]


# При скидке на игнорируемую подкатегорию товары переходят в больше скидок
@pytest.mark.config(
    GROCERY_CAAS_PROMO_IGNORED_SUBCATEGORIES=['ignored_subcategory'],
)
async def test_ignored_subcategory(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
):
    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='ignored_subcategory')

    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [
                {
                    'id': 'ignored_subcategory',
                    'products': ['product_1', 'product_2'],
                },
            ],
        ),
    )
    grocery_discounts.add_money_discount(
        product_id='ignored_subcategory',
        value_type='absolute',
        value='10',
        is_subcategory=True,
    )
    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 200
    assert [item['id'] for item in response.json()['items']] == [
        'promo-more-discounts',
        'product_1',
        'product_2',
    ]


# проверяем что ответ ручки при наличии всех скидок имеет вид:
# 1. Проудкты с истекающим сроком годности
# 2. Продукты разитые по прилавкам
# 3. Больше скидок
@build_expiring_products(enabled=True)
@pytest.mark.config(
    GROCERY_CAAS_PROMO_BUILD_EXPIRING_CACHE_SETTINGS={
        'batch_update_size': 100,
        'update_enabled': True,
    },
)
@pytest.mark.config(
    OVERLORD_CATALOG_REGION_IDS_BY_COUNTRY_ID=[
        {'country_id': 225, 'region_ids': [213]},
    ],
)
async def test_all_discounts_subcategories(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
        grocery_tags,
        grocery_menu,
        mockserver,
):
    product_1 = 'product_1'
    product_2 = 'product_2'
    product_3 = 'product_3'
    meta_product = 'meta_product'
    combo_revision = 'combo_revision'
    layout = grocery_products.add_layout(test_id='1')
    group = layout.add_category_group(test_id='1')
    virtual_category = group.add_virtual_category(test_id='1')
    virtual_category.add_subcategory(subcategory_id='subcategory_1')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [
                {'id': 'subcategory_1', 'products': [product_1, product_2]},
                {'id': 'subcategory_2', 'products': [product_3, meta_product]},
            ],
        ),
    )

    grocery_tags.add_store_item_id_tag(
        store_item_id=_format_store_item_id(
            common.DEPOT['depot_id'], product_1,
        ),
        tag='expiring_tag',
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'test_combo',
            [meta_product],
            [
                mock_grocery_menu.ProductGroup(
                    False, 2, ['product-11', 'product-22'],
                ),
            ],
            combo_revision,
        ),
    )

    grocery_discounts.add_money_discount(
        product_id='expiring_tag',
        value_type='absolute',
        value='10',
        hierarchy_name='dynamic_discounts',
        discount_meta={'is_expiring': True},
    )
    grocery_discounts.add_money_discount(
        product_id=product_2,
        value_type='absolute',
        value='10',
        hierarchy_name='suppliers_discounts',
    )
    grocery_discounts.add_money_discount(
        product_id=product_3, value_type='absolute', value='10',
    )
    grocery_discounts.add_money_discount(
        product_id=combo_revision,
        value_type='absolute',
        value='10',
        hierarchy_name='bundle_discounts',
    )

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/cold-storage/v1/get/'
        'expiring-products',
    )
    def _mock_cold_storage(request):
        return {
            'items': [
                {
                    'product_id': product_1,
                    'store_wms_id': common.DEPOT['depot_id'],
                },
            ],
        }

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 200
    assert [item['id'] for item in response.json()['items']] == [
        'promo-expiring-products',
        product_1,
        'promo-combo-products',
        meta_product,
        'group_category-group-1',
        product_2,
        'promo-more-discounts',
        product_3,
    ]


# Пробрасываем uid пользователя в сервис скидок
async def test_fetch_discounts_uid_header(
        taxi_grocery_caas_promo,
        overlord_catalog,
        mockserver,
        grocery_products,
):
    uid = '1234567'
    grocery_products.add_layout(test_id='1')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'], category_tree=EMPTY_TREE,
    )

    @mockserver.json_handler('/grocery-discounts/v4/fetch-discounted-products')
    def mock_grocery_discounts(request):
        assert request.headers['X-Yandex-UID'] == uid
        return mockserver.make_response(json={'items': []}, status=200)

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        headers={'X-Yandex-UID': uid},
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1


async def test_fetch_discounts_phone_header(
        taxi_grocery_caas_promo,
        overlord_catalog,
        mockserver,
        grocery_products,
):
    grocery_products.add_layout(test_id='1')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'], category_tree=EMPTY_TREE,
    )

    @mockserver.json_handler('/grocery-discounts/v4/fetch-discounted-products')
    def mock_grocery_discounts(request):
        assert request.json['personal_phone_id'] == 'test_phone_id'
        return mockserver.make_response(json={'items': []}, status=200)

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        headers={'X-YaTaxi-User': 'personal_phone_id=test_phone_id'},
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status_code == 200
    assert mock_grocery_discounts.times_called == 1


async def test_combo_discounts_subcategory(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
        grocery_menu,
):
    grocery_products.add_layout(test_id='1')
    meta_product_1 = 'available_meta_product'
    combo_revision_1 = 'combo_revision_1'
    meta_product_2 = 'meta_product_not_in_tree'
    combo_revision_2 = 'combo_revision_2'

    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [{'id': 'subcategory_1', 'products': [meta_product_1]}],
        ),
    )

    for revision, meta_product in [
            (combo_revision_1, meta_product_1),
            (combo_revision_2, meta_product_2),
    ]:
        grocery_menu.add_combo_product(
            mock_grocery_menu.ComboProduct(
                f'id_{revision}',
                [meta_product],
                [
                    mock_grocery_menu.ProductGroup(
                        False, 2, ['product-11', 'product-22'],
                    ),
                ],
                revision,
            ),
        )
        grocery_discounts.add_money_discount(
            product_id=revision,
            value_type='absolute',
            value='10',
            hierarchy_name='bundle_discounts',
        )

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 200
    assert [item['id'] for item in response.json()['items']] == [
        'promo-combo-products',
        meta_product_1,
    ]


async def test_combo_items_shared_by_groups(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_discounts,
        grocery_products,
        grocery_menu,
):
    layout = grocery_products.add_layout(test_id='1')
    group_1 = layout.add_category_group(test_id='1')
    virtual_category_1 = group_1.add_virtual_category(test_id='1')
    virtual_category_1.add_subcategory(subcategory_id='subcategory_1')
    group_2 = layout.add_category_group(test_id='2')
    virtual_category_2 = group_2.add_virtual_category(test_id='2')
    virtual_category_2.add_subcategory(subcategory_id='subcategory_2')
    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'],
        category_tree=common.build_tree(
            [
                {
                    'id': 'subcategory_1',
                    'products': ['product_1', 'product_2'],
                },
                {
                    'id': 'subcategory_2',
                    'products': ['product_3', 'product_4'],
                },
            ],
        ),
    )
    revision = 'combo_revision'
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            f'id_{revision}',
            [],
            [
                mock_grocery_menu.ProductGroup(
                    False,
                    2,
                    ['product_1', 'product_2', 'product_3', 'product_4'],
                ),
            ],
            revision,
        ),
    )

    grocery_discounts.add_money_discount(
        product_id=revision,
        value_type='absolute',
        value='10',
        hierarchy_name='bundle_discounts',
    )

    response = await taxi_grocery_caas_promo.post(
        '/internal/v1/caas-promo/v1/category/discounts',
        json=common.DISCOUNT_REQUEST,
    )
    assert response.status == 200
    assert [item['id'] for item in response.json()['items']] == [
        'group_category-group-1',
        'product_1',
        'product_2',
        'group_category-group-2',
        'product_3',
        'product_4',
    ]
    assert len(response.json()['products']) == 4
    assert len(response.json()['subcategories']) == 2
