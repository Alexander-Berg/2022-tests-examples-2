import pytest

from tests_eats_products import experiments
from tests_eats_products import utils


CATEGORY_ID = '123'
INTEGER_ID = {'id': int(CATEGORY_ID)}

PUBLIC_IDS = [
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
]

CATEGORIES_BASE_REQUEST = {
    'slug': 'slug',
    'categories': [{'id': 1, 'min_items_count': 1, 'max_items_count': 4}],
}


@utils.PARAMETRIZE_GET_CATEGORIES_PRODUCTS_INFO_VERSION
@experiments.products_scoring()
@pytest.mark.redis_store(
    [
        'zadd',
        f'scores:top:yt_table_v3:1:{CATEGORY_ID}',
        '0.00001',
        'item_id_1',
        '0.00003',
        'item_id_2',
    ],
    [
        'zadd',
        f'scores:top:yt_table_v3:1:{utils.DISCOUNT_CATEGORY_ID}',
        '0.00001',
        'item_id_2',
    ],
)
@pytest.mark.config(
    EATS_PRODUCTS_SETTINGS={'discount_promo': {'enabled': True}},
    EATS_PRODUCTS_BADGES=utils.EATS_PRODUCTS_BADGES,
    EATS_PRODUCTS_DYNAMIC_CATEGORIES=utils.dynamic_categories_config(
        discount_enabled=True,
    ),
)
async def test_get_categories_badges_discount(
        taxi_eats_products,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
        handlers_version,
        add_default_product_mapping,
        cache_add_discount_product,
        mock_nomenclature_v2_details,
        mock_nomenclature_v1_categories_context,
):
    """
    Тест проверяет выставление цветов для бейджа со скидкой (get_categories)
    """
    add_default_product_mapping()

    for i in range(2):
        mock_nomenclature_static_info_context.add_product(PUBLIC_IDS[i])
        mock_nomenclature_dynamic_info_context.add_product(
            PUBLIC_IDS[i], old_price=1000,
        )

    mock_nomenclature_get_parent_context.add_category(CATEGORY_ID)
    mock_nomenclature_v1_categories_context.add_category(
        public_id=CATEGORY_ID, name='Category',
    )

    response = await taxi_eats_products.post(
        utils.Handlers.GET_CATEGORIES,
        json={
            'slug': 'slug',
            'categories': [
                {
                    'id': int(CATEGORY_ID),
                    'min_items_count': 1,
                    'max_items_count': 10,
                },
                {
                    'id': utils.DISCOUNT_CATEGORY_ID,
                    'min_items_count': 1,
                    'max_items_count': 10,
                },
            ],
        },
    )
    assert response.status_code == 200

    resp_cat_1 = response.json()['categories'][0]['items'][0]
    expected = utils.create_expected_badges(
        utils.EATS_PRODUCTS_BADGES['discount_badges'],
    )
    utils.compare_badges(resp_cat_1, expected)

    resp_cat_2 = response.json()['categories'][1]['items'][0]
    expected = utils.create_expected_badges(
        utils.EATS_PRODUCTS_BADGES['discount_badges'],
    )
    utils.compare_badges(resp_cat_2, expected)
