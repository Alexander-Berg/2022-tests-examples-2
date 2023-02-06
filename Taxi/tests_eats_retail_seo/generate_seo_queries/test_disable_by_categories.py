# pylint: disable=C0103
import copy

import pytest

from .. import models
from .. import utils


PERIODIC_NAME = 'generate-seo-queries-periodic'
SOME_PARENT_CATEGORY_EXCLUDED_BY_ID = '123'
SOME_CHILD_CATEGORY_EXCLUDED_BY_ID = '456'
SOME_PARENT_CATEGORY_EXCLUDED_BY_TAG = '321'
SOME_CHILD_CATEGORY_EXCLUDED_BY_TAG = '654'
TAG_TO_EXCLUDE_BY = 'Тег 1'


@pytest.mark.parametrize(**utils.gen_bool_params('should_shuffle_is_enabled'))
async def test_disable_by_categories(
        assert_objects_lists,
        enable_periodic_in_config,
        generate_seo_query,
        get_seo_queries_from_db,
        save_categories_to_db,
        save_product_brands_to_db,
        save_product_types_to_db,
        save_seo_queries_to_db,
        save_tags_to_db,
        taxi_eats_retail_seo,
        testpoint,
        update_taxi_config,
        # parametrize params
        should_shuffle_is_enabled,
):
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(PERIODIC_NAME)
    update_taxi_config(
        'EATS_RETAIL_SEO_FEEDS_SETTINGS',
        {
            '__default__': {
                'allowed_countries': [],
                'feed_expiration_threshold_in_hours': 336,
                'categories_ids_to_exclude': [
                    SOME_PARENT_CATEGORY_EXCLUDED_BY_ID,
                    SOME_CHILD_CATEGORY_EXCLUDED_BY_ID,
                ],
                'categories_tags_to_exclude': [TAG_TO_EXCLUDE_BY],
            },
        },
    )

    [
        product_brands,
        product_types,
        categories,
        initial_seo_queries,
        expected_seo_queries,
        tag_to_exclude_by,
    ] = _generate_data(generate_seo_query, should_shuffle_is_enabled)
    save_product_brands_to_db(product_brands)
    save_product_types_to_db(product_types)
    save_categories_to_db(categories)
    save_seo_queries_to_db(initial_seo_queries)
    save_tags_to_db([tag_to_exclude_by])

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)
    assert_objects_lists(get_seo_queries_from_db(), expected_seo_queries)

    # check that rerun doesn't affect data
    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)
    assert_objects_lists(get_seo_queries_from_db(), expected_seo_queries)

    assert periodic_finished.times_called == 2


def _generate_data(generate_seo_query, should_shuffle_is_enabled):
    product_brand_1_excluded_by_parent_category_by_id = models.ProductBrand(
        'pb1',
    )
    product_brand_2_excluded_by_child_category_by_id = models.ProductBrand(
        'pb2',
    )
    product_brand_3 = models.ProductBrand('pb3')
    product_brand_4_without_type = models.ProductBrand('pb4')
    product_brand_5_excluded_by_parent_category_by_tag = models.ProductBrand(
        'pb5',
    )
    product_brand_6_excluded_by_child_category_by_tag = models.ProductBrand(
        'pb6',
    )
    product_brands_excluded = [
        product_brand_1_excluded_by_parent_category_by_id,
        product_brand_2_excluded_by_child_category_by_id,
        product_brand_4_without_type,
        product_brand_5_excluded_by_parent_category_by_tag,
        product_brand_6_excluded_by_child_category_by_tag,
    ]
    product_brands = [
        product_brand_1_excluded_by_parent_category_by_id,
        product_brand_2_excluded_by_child_category_by_id,
        product_brand_3,
        product_brand_5_excluded_by_parent_category_by_tag,
        product_brand_6_excluded_by_child_category_by_tag,
    ]

    product_type_1_excluded_by_parent_category_by_id = models.ProductType(
        name='pt1',
    )
    product_type_1_excluded_by_parent_category_by_id.set_product_brands(
        [product_brand_1_excluded_by_parent_category_by_id],
    )
    product_type_2_excluded_by_child_category_by_id = models.ProductType(
        name='pt2',
    )
    product_type_2_excluded_by_child_category_by_id.set_product_brands(
        [product_brand_2_excluded_by_child_category_by_id],
    )
    product_type_3 = models.ProductType(name='pt3')
    product_type_3.set_product_brands([product_brand_3])
    product_type_4_excluded_by_parent_category_tag = models.ProductType(
        name='pt4',
    )
    product_type_4_excluded_by_parent_category_tag.set_product_brands(
        [product_brand_5_excluded_by_parent_category_by_tag],
    )
    product_type_5_excluded_by_child_category_tag = models.ProductType(
        name='pt5',
    )
    product_type_5_excluded_by_child_category_tag.set_product_brands(
        [product_brand_6_excluded_by_child_category_by_tag],
    )
    product_types_excluded = [
        product_type_1_excluded_by_parent_category_by_id,
        product_type_2_excluded_by_child_category_by_id,
        product_type_4_excluded_by_parent_category_tag,
        product_type_5_excluded_by_child_category_tag,
    ]
    product_types = [
        product_type_1_excluded_by_parent_category_by_id,
        product_type_2_excluded_by_child_category_by_id,
        product_type_3,
        product_type_4_excluded_by_parent_category_tag,
        product_type_5_excluded_by_child_category_tag,
    ]

    category_1_excluded_by_parent_by_id = models.Category(
        category_id='1234', name='cat_1234',
    )
    category_1_excluded_by_parent_by_id.set_product_types(
        [product_type_1_excluded_by_parent_category_by_id],
    )
    category_2_excluded_parent_by_id = models.Category(
        category_id=SOME_PARENT_CATEGORY_EXCLUDED_BY_ID,
        name=f'cat_{SOME_PARENT_CATEGORY_EXCLUDED_BY_ID}',
    )
    category_2_excluded_parent_by_id.set_child_categories(
        [category_1_excluded_by_parent_by_id],
    )
    category_3_excluded_child_by_id = models.Category(
        category_id=SOME_CHILD_CATEGORY_EXCLUDED_BY_ID,
        name=f'cat_{SOME_CHILD_CATEGORY_EXCLUDED_BY_ID}',
    )
    category_3_excluded_child_by_id.set_product_types(
        [product_type_2_excluded_by_child_category_by_id],
    )
    category_4 = models.Category(category_id='789', name='cat_789')
    category_4.set_product_types([product_type_3])
    category_5_excluded_by_parent_by_tag = models.Category(
        category_id='5678', name='cat_5678',
    )
    category_5_excluded_by_parent_by_tag.set_product_types(
        [product_type_4_excluded_by_parent_category_tag],
    )
    tag_to_exclude_by = models.Tag(TAG_TO_EXCLUDE_BY)
    category_6_excluded_parent_by_tag = models.Category(
        category_id=SOME_PARENT_CATEGORY_EXCLUDED_BY_TAG,
        name=f'cat_{SOME_PARENT_CATEGORY_EXCLUDED_BY_TAG}',
    )
    category_6_excluded_parent_by_tag.add_tag(tag_to_exclude_by)
    category_6_excluded_parent_by_tag.set_child_categories(
        [category_5_excluded_by_parent_by_tag],
    )
    category_7_excluded_child_by_tag = models.Category(
        category_id=SOME_CHILD_CATEGORY_EXCLUDED_BY_TAG,
        name=f'cat_{SOME_CHILD_CATEGORY_EXCLUDED_BY_TAG}',
    )
    category_7_excluded_child_by_tag.set_product_types(
        [product_type_5_excluded_by_child_category_tag],
    )
    category_7_excluded_child_by_tag.add_tag(tag_to_exclude_by)
    categories = [
        category_1_excluded_by_parent_by_id,
        category_2_excluded_parent_by_id,
        category_3_excluded_child_by_id,
        category_4,
        category_5_excluded_by_parent_by_tag,
        category_6_excluded_parent_by_tag,
        category_7_excluded_child_by_tag,
    ]

    is_enabled = True
    initial_seo_queries = []
    for product_brand in product_brands:
        initial_seo_queries.append(
            generate_seo_query(
                product_brand=product_brand,
                is_enabled=_get_is_enabled(
                    is_enabled, should_shuffle_is_enabled,
                ),
            ),
        )
    for product_type in product_types:
        initial_seo_queries.append(
            generate_seo_query(
                product_type=product_type,
                is_enabled=_get_is_enabled(
                    is_enabled, should_shuffle_is_enabled,
                ),
            ),
        )
        for product_brand in list(product_type.get_product_brands()):
            initial_seo_queries.append(
                generate_seo_query(
                    product_type=product_type,
                    product_brand=product_brand,
                    is_enabled=_get_is_enabled(
                        is_enabled, should_shuffle_is_enabled,
                    ),
                ),
            )

    expected_seo_queries = []
    for seo_query in initial_seo_queries:
        expected_seo_query = copy.deepcopy(seo_query)
        if (
                (
                    seo_query.product_type
                    and seo_query.product_type in product_types_excluded
                )
                or (
                    seo_query.product_brand
                    and seo_query.product_brand in product_brands_excluded
                )
        ):
            expected_seo_query.is_enabled = False
        else:
            expected_seo_query.is_enabled = True
        expected_seo_queries.append(expected_seo_query)

    return [
        product_brands,
        product_types,
        categories,
        initial_seo_queries,
        expected_seo_queries,
        tag_to_exclude_by,
    ]


def _get_is_enabled(is_enabled, should_shuffle_is_enabled):
    if should_shuffle_is_enabled:
        is_enabled = not is_enabled
    return is_enabled
