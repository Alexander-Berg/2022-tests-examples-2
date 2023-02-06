# pylint: disable=too-many-lines
import pytest


BRAND_ID = 1
ASSORTMENT_NAME = 'test_1'

QUEUE_NAME = 'eats_nomenclature_add_custom_assortment'
CATEGORIES_QUERY = """
    select name, assortment_id, is_custom, is_base, is_restaurant
    from eats_nomenclature.categories
"""
CATEGORIES_PICTURES_QUERY = """
    select cp.assortment_id, c.name, cp.picture_id
    from eats_nomenclature.category_pictures cp
    join eats_nomenclature.categories c
    on cp.category_id = c.id
"""
CATEGORIES_RELATIONS_QUERY = """
    select assortment_id, category_id, parent_category_id
    from eats_nomenclature.categories_relations
"""
CATEGORIES_PRODUCTS_QUERY = """
    select cp.assortment_id, c.name, cp.product_id, cp.sort_order
    from eats_nomenclature.categories_products cp
    join eats_nomenclature.categories c
    on cp.category_id = c.id
"""
PLACES_CATEGORIES_QUERY = """
    select pc.assortment_id, pc.place_id, c.name, pc.active_items_count
    from eats_nomenclature.places_categories pc
    join eats_nomenclature.categories c
    on pc.category_id = c.id
"""
PLACE_ASSORTMENT_ACTIVATION_QUERY = """
    select place_id, assortment_id
    from eats_nomenclature.place_assortments
"""


@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_brand_has_no_custom_categories(
        stq_runner,
        sql_fill_custom_assortment,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        sql_read_data,
):
    place_id = 1
    assortment_id = sql_fill_enrichment_status(place_id, False, False)
    sql_fill_products_and_pictures()
    sql_fill_custom_assortment(assortment_id)

    # Check that there was some data.
    assert sql_read_data(CATEGORIES_QUERY)
    assert sql_read_data(CATEGORIES_PICTURES_QUERY)
    assert sql_read_data(CATEGORIES_RELATIONS_QUERY)
    assert sql_read_data(CATEGORIES_PRODUCTS_QUERY)
    assert sql_read_data(PLACES_CATEGORIES_QUERY)

    # Call stq-task for brand that doesn't have custom categories.
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id},
        expect_fail=False,
    )

    # Check that previous data was deleted.
    assert not sql_read_data(CATEGORIES_QUERY)
    assert not sql_read_data(CATEGORIES_PICTURES_QUERY)
    assert not sql_read_data(CATEGORIES_RELATIONS_QUERY)
    assert not sql_read_data(CATEGORIES_PRODUCTS_QUERY)
    assert not sql_read_data(PLACES_CATEGORIES_QUERY)


@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_categories_merge_partner_only(
        stq_runner,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        sql_read_data,
):
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(assortment_name=None)

    place_id = 1
    assortment_id = sql_fill_enrichment_status(place_id, False, False)
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    assert sql_read_data(CATEGORIES_QUERY) == {
        ('category_1', assortment_id, True, False, False),
        ('category_2', assortment_id, True, False, False),
        ('category_3', assortment_id, True, False, False),
        ('category_4', assortment_id, False, True, False),
        ('category_5', assortment_id, False, True, False),
    }

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': None},
        expect_fail=False,
    )

    # only non-custom categories must remain
    assert sql_read_data(CATEGORIES_QUERY) == {
        ('category_4', assortment_id, False, True, False),
        ('category_5', assortment_id, False, True, False),
    }


@pytest.mark.parametrize('is_base', [True, False])
@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.parametrize(
    'use_only_custom_categories',
    [
        pytest.param(True, id='remove partner categories'),
        pytest.param(False, id='keep partner categories'),
    ],
)
@pytest.mark.parametrize('is_restaurant', [True, False])
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_categories_merge(
        fill_brand_custom_categories,
        pgsql,
        sql_fill_custom_assortment,
        sql_fill_enrichment_status,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_read_data,
        sql_get_assortment_trait_id,
        stq_runner,
        is_base,
        use_assortment_name,
        use_only_custom_categories,
        is_restaurant,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )

    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(
        assortment_name=ASSORTMENT_NAME if use_assortment_name else None,
        is_base=is_base,
        is_restaurant=is_restaurant,
    )

    place_id = 1
    assortment_id = sql_fill_enrichment_status(place_id, False, False)
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    sql_set_use_only_custom_flag(pgsql, use_only_custom_categories, trait_id)

    assert sql_read_data(CATEGORIES_QUERY) == {
        ('category_1', assortment_id, True, False, False),
        ('category_2', assortment_id, True, False, False),
        ('category_3', assortment_id, True, False, False),
        ('category_4', assortment_id, False, True, False),
        ('category_5', assortment_id, False, True, False),
    }

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
        expect_fail=False,
    )

    if use_only_custom_categories:
        assert sql_read_data(CATEGORIES_QUERY) == {
            ('custom_category_1', assortment_id, True, is_base, is_restaurant),
            ('custom_category_2', assortment_id, True, is_base, is_restaurant),
            ('custom_category_3', assortment_id, True, is_base, is_restaurant),
        }
    else:
        assert sql_read_data(CATEGORIES_QUERY) == {
            ('custom_category_1', assortment_id, True, is_base, is_restaurant),
            ('custom_category_2', assortment_id, True, is_base, is_restaurant),
            ('custom_category_3', assortment_id, True, is_base, is_restaurant),
            ('category_4', assortment_id, False, True, False),
            ('category_5', assortment_id, False, True, False),
        }


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_disabled_custom_groups(
        pgsql,
        stq_runner,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        sql_read_data,
        use_assortment_name,
        sql_get_assortment_trait_id,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )

    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(
        assortment_name=ASSORTMENT_NAME if use_assortment_name else None,
    )

    # Disable all groups of custom categories.
    sql_disable_custom_groups(pgsql)

    # Fill old assortment.
    place_id = 1
    assortment_id = sql_fill_enrichment_status(place_id, False, False)
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    # Check old categories.
    assert sql_read_data(CATEGORIES_QUERY) == {
        ('category_1', assortment_id, True, False, False),
        ('category_2', assortment_id, True, False, False),
        ('category_3', assortment_id, True, False, False),
        ('category_4', assortment_id, False, True, False),
        ('category_5', assortment_id, False, True, False),
    }

    # Call stq-task.
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
        expect_fail=False,
    )

    # Only not custom categories should be in assortment.
    assert sql_read_data(CATEGORIES_QUERY) == {
        ('category_4', assortment_id, False, True, False),
        ('category_5', assortment_id, False, True, False),
    }


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.parametrize(
    'use_only_custom_categories',
    [
        pytest.param(True, id='remove partner categories'),
        pytest.param(False, id='keep partner categories'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_categories_pictures_merge(
        pgsql,
        stq_runner,
        use_only_custom_categories,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        sql_read_data,
        use_assortment_name,
        sql_get_assortment_trait_id,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )

    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(
        assortment_name=ASSORTMENT_NAME if use_assortment_name else None,
    )

    # Fill old assortment.
    place_id = 1
    assortment_id = sql_fill_enrichment_status(place_id, False, False)
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    sql_set_use_only_custom_flag(pgsql, use_only_custom_categories, trait_id)

    # Check old categories pictures.
    assert sql_read_data(CATEGORIES_PICTURES_QUERY) == {
        (assortment_id, 'category_1', 1),
        (assortment_id, 'category_2', 1),
        (assortment_id, 'category_3', 1),
        (assortment_id, 'category_4', 1),
        (assortment_id, 'category_5', 1),
    }

    # Call stq-task.
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
        expect_fail=False,
    )

    # Check new categories pictures.
    if use_only_custom_categories:
        assert sql_read_data(CATEGORIES_PICTURES_QUERY) == {
            (assortment_id, 'custom_category_1', 1),
            (assortment_id, 'custom_category_2', 2),
            (assortment_id, 'custom_category_2', 1),
            (assortment_id, 'custom_category_3', 3),
        }
    else:
        assert sql_read_data(CATEGORIES_PICTURES_QUERY) == {
            (assortment_id, 'custom_category_1', 1),
            (assortment_id, 'custom_category_2', 2),
            (assortment_id, 'custom_category_2', 1),
            (assortment_id, 'custom_category_3', 3),
            (assortment_id, 'category_4', 1),
            (assortment_id, 'category_5', 1),
        }


@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_categories_pictures_with_null_pic(
        pgsql,
        stq_runner,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        sql_read_data,
        sql_get_assortment_trait_id,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID, ASSORTMENT_NAME, insert_if_missing=True,
    )

    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(assortment_name=ASSORTMENT_NAME)
    sql_reset_custom_category_pic(pgsql, 'custom_category_1')

    # Fill old assortment.
    place_id = 1
    assortment_id = sql_fill_enrichment_status(place_id, False, False)
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    # Call stq-task.
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
        expect_fail=False,
    )

    # Check new categories pictures.
    assert sql_read_data(CATEGORIES_PICTURES_QUERY) == {
        (assortment_id, 'custom_category_2', 2),
        (assortment_id, 'custom_category_2', 1),
        (assortment_id, 'custom_category_3', 3),
        (assortment_id, 'category_4', 1),
        (assortment_id, 'category_5', 1),
    }


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.parametrize(
    'use_only_custom_categories',
    [
        pytest.param(True, id='remove partner categories'),
        pytest.param(False, id='keep partner categories'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_categories_relations_merge(
        pgsql,
        stq_runner,
        use_only_custom_categories,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        sql_read_data,
        use_assortment_name,
        sql_get_assortment_trait_id,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )

    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(
        assortment_name=ASSORTMENT_NAME if use_assortment_name else None,
    )

    # Fill old assortment.
    place_id = 1
    assortment_id = sql_fill_enrichment_status(place_id, False, False)
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    sql_set_use_only_custom_flag(pgsql, use_only_custom_categories, trait_id)

    # Check old categories relations.
    assert sql_read_categories_relations(pgsql, sql_read_data) == {
        (assortment_id, 'category_1', None),
        (assortment_id, 'category_2', 'category_1'),
        (assortment_id, 'category_3', 'category_1'),
        (assortment_id, 'category_4', None),
        (assortment_id, 'category_5', None),
    }

    # Call stq-task.
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
        expect_fail=False,
    )

    # Check new categories relations.
    if use_only_custom_categories:
        assert sql_read_categories_relations(pgsql, sql_read_data) == {
            (assortment_id, 'custom_category_1', None),
            (assortment_id, 'custom_category_2', 'custom_category_1'),
            (assortment_id, 'custom_category_2', None),
            (assortment_id, 'custom_category_3', 'custom_category_1'),
        }
    else:
        assert sql_read_categories_relations(pgsql, sql_read_data) == {
            (assortment_id, 'custom_category_1', None),
            (assortment_id, 'custom_category_2', 'custom_category_1'),
            (assortment_id, 'custom_category_2', None),
            (assortment_id, 'custom_category_3', 'custom_category_1'),
            (assortment_id, 'category_4', None),
            (assortment_id, 'category_5', None),
        }


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.parametrize(
    'use_only_custom_categories',
    [
        pytest.param(True, id='remove partner categories'),
        pytest.param(False, id='keep partner categories'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_categories_products_merge(
        pgsql,
        stq_runner,
        load_json,
        use_only_custom_categories,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        sql_read_data,
        use_assortment_name,
        sql_get_assortment_trait_id,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )

    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    sql_fill_product_types(pgsql)

    product_types_to_request = ['value_uuid1', 'value_uuid2']
    request = load_json('custom_categories_request.json')
    request['categories'][0]['product_type_ids'] = product_types_to_request

    await fill_brand_custom_categories(
        assortment_name=ASSORTMENT_NAME if use_assortment_name else None,
        request_json=request,
    )

    # Fill old assortment.
    place_id = 1
    assortment_id = sql_fill_enrichment_status(place_id, False, False)
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)
    sql_insert_categories_products(
        pgsql, assortment_id, [(4, 4, 4), (5, 5, 5)],
    )

    sql_set_use_only_custom_flag(pgsql, use_only_custom_categories, trait_id)

    # Check old categories products.
    assert sql_read_data(CATEGORIES_PRODUCTS_QUERY) == {
        (assortment_id, 'category_2', 1, 1),
        (assortment_id, 'category_2', 2, 2),
        (assortment_id, 'category_3', 3, 3),
        (assortment_id, 'category_4', 1, 3),
        (assortment_id, 'category_4', 2, 3),
        (assortment_id, 'category_4', 3, 3),
        (assortment_id, 'category_4', 4, 4),
        (assortment_id, 'category_5', 5, 5),
    }

    # Call stq-task.
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
        expect_fail=False,
    )

    # Check new categories products.
    if use_only_custom_categories:
        assert sql_read_data(CATEGORIES_PRODUCTS_QUERY) == {
            (assortment_id, 'custom_category_2', 1, 100),
            (assortment_id, 'custom_category_2', 3, 100),
            (assortment_id, 'custom_category_3', 2, 100),
            (assortment_id, 'custom_category_3', 3, 100),
            (assortment_id, 'custom_category_1', 4, 100),
            (assortment_id, 'custom_category_1', 5, 100),
        }
    else:
        assert sql_read_data(CATEGORIES_PRODUCTS_QUERY) == {
            (assortment_id, 'custom_category_2', 1, 100),
            (assortment_id, 'custom_category_2', 3, 100),
            (assortment_id, 'custom_category_3', 2, 100),
            (assortment_id, 'custom_category_3', 3, 100),
            (assortment_id, 'category_4', 1, 3),
            (assortment_id, 'category_4', 2, 3),
            (assortment_id, 'category_4', 3, 3),
            (assortment_id, 'custom_category_1', 4, 100),
            (assortment_id, 'custom_category_1', 5, 100),
            (assortment_id, 'category_4', 4, 4),
            (assortment_id, 'category_5', 5, 5),
        }


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_product_types(
        pgsql,
        stq_runner,
        load_json,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        sql_read_data,
        use_assortment_name,
        sql_get_assortment_trait_id,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )

    # Fill products.
    sql_fill_products_and_pictures()
    sql_fill_product_types(pgsql)
    sql_fill_sku_product_types(pgsql)

    # Fill brand custom categories.
    request = load_json('custom_categories_request.json')
    request['categories'][0]['product_type_ids'] = ['value_uuid1']
    request['categories'][1]['product_type_ids'] = ['value_uuid2']
    await fill_brand_custom_categories(
        assortment_name=ASSORTMENT_NAME if use_assortment_name else None,
        request_json=request,
    )

    # Fill old assortment.
    place_id = 1
    assortment_id = sql_fill_enrichment_status(place_id, False, False)
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)
    sql_insert_categories_products(
        pgsql,
        assortment_id,
        [(4, 4, 4), (5, 5, 5), (4, 6, 6), (4, 7, 7), (4, 8, 8), (4, 9, 9)],
    )
    sql_set_use_only_custom_flag(
        pgsql, use_only_custom_categories=True, trait_id=trait_id,
    )

    sql_add_product_with_unused_type(pgsql, assortment_id)
    sql_add_product_with_unused_overriden_type(pgsql, assortment_id)
    sql_add_products_with_overriden_sku(pgsql, assortment_id)

    # Call stq-task.
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
        expect_fail=False,
    )

    # Check new categories products.
    assert sql_read_data(CATEGORIES_PRODUCTS_QUERY) == {
        (assortment_id, 'custom_category_2', 1, 100),
        (assortment_id, 'custom_category_2', 3, 100),
        (assortment_id, 'custom_category_3', 2, 100),
        (assortment_id, 'custom_category_3', 3, 100),
        (assortment_id, 'custom_category_1', 4, 100),
        (assortment_id, 'custom_category_1', 5, 100),
        # product 6 has only sku product_type
        (assortment_id, 'custom_category_2', 6, 100),
        # product 7 has product_type and sku product_type,
        # but sku product_type should be chosen
        (assortment_id, 'custom_category_2', 7, 100),
        # product 8 has sku_id, but sku has no product_type
        # product 9 has sku product_type, but it is overriden
        (assortment_id, 'custom_category_1', 9, 100),
        # product 10 has product_type not in custom_categories_product_types
        # so we filter it out
        # product 11 has sku product_type in custom_categories_product_types,
        # but overriden product_type not in custom_categories_product_types
        # so we filter it out
        (assortment_id, 'custom_category_2', 12, 100),
        (assortment_id, 'custom_category_2', 13, 100),
        # product 14 has sku product_type in custom_categories_product_types,
        # but its sku had overriden to null in overriden_product_sku
        # so we filter it out
        (assortment_id, 'custom_category_2', 15, 100),
    }


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.parametrize(
    'use_only_custom_categories',
    [
        pytest.param(True, id='remove partner categories'),
        pytest.param(False, id='keep partner categories'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_places_categories_merge(
        pgsql,
        stq_runner,
        use_only_custom_categories,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        sql_read_data,
        use_assortment_name,
        sql_get_assortment_trait_id,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )

    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(
        assortment_name=ASSORTMENT_NAME if use_assortment_name else None,
    )

    # Fill old assortment.
    place_id = 1
    assortment_id = sql_fill_enrichment_status(place_id, False, False)
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    sql_set_use_only_custom_flag(pgsql, use_only_custom_categories, trait_id)

    # Check old places categories.
    assert sql_read_data(PLACES_CATEGORIES_QUERY) == {
        (assortment_id, 1, 'category_1', 0),
        (assortment_id, 1, 'category_2', 2),
        (assortment_id, 1, 'category_3', 1),
        (assortment_id, 1, 'category_4', 10),
        (assortment_id, 1, 'category_5', 20),
    }

    # Call stq-task.
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
        expect_fail=False,
    )

    # Check new places categories.
    if use_only_custom_categories:
        assert sql_read_data(PLACES_CATEGORIES_QUERY) == {
            (assortment_id, 1, 'custom_category_1', 0),
            (assortment_id, 1, 'custom_category_2', 0),
            (assortment_id, 1, 'custom_category_3', 0),
        }
    else:
        assert sql_read_data(PLACES_CATEGORIES_QUERY) == {
            (assortment_id, 1, 'custom_category_1', 0),
            (assortment_id, 1, 'custom_category_2', 0),
            (assortment_id, 1, 'custom_category_3', 0),
            (assortment_id, 1, 'category_4', 10),
            (assortment_id, 1, 'category_5', 20),
        }


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_categories_sort_order(
        pgsql,
        stq_runner,
        taxi_eats_nomenclature,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_custom_categories_group,
        sql_read_data,
        use_assortment_name,
        sql_get_assortment_trait_id,
):
    assortment_query = (
        f'&assortment_name={ASSORTMENT_NAME}' if use_assortment_name else ''
    )

    trait_id = sql_get_assortment_trait_id(
        BRAND_ID,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )

    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    group_id_1 = await fill_custom_categories_group(
        'custom_categories_request.json',
    )
    group_id_2 = await fill_custom_categories_group(
        'additional_custom_categories_request.json',
    )
    request = {
        'categories_groups': [
            {'id': group_id_1, 'sort_order': 2},
            {'id': group_id_2, 'sort_order': 1},
        ],
        'use_only_custom_categories': False,
    }
    await taxi_eats_nomenclature.post(
        '/v1/manage/brand/custom_categories_groups?brand_id=1'
        + assortment_query,
        json=request,
    )

    # Fill old assortment.
    place_id = 1
    assortment_id = sql_fill_enrichment_status(place_id, False, False)
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    # Call stq-task.
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
        expect_fail=False,
    )

    query = """select c.name, cr.sort_order
               from eats_nomenclature.categories_relations cr
               join eats_nomenclature.categories c
               on cr.category_id = c.id"""
    category_to_sort_order = {c[0]: c[1] for c in sql_read_data(query)}

    # Check not custom categories sort_order.
    assert category_to_sort_order['category_4'] == 100
    assert category_to_sort_order['category_5'] == 150

    # Check that custom categories have sort_order
    # less than not custom categories.
    custom_categories_names = [
        'custom_category_1',
        'custom_category_2',
        'custom_category_3',
        'custom_category_10',
    ]
    for custom_category in custom_categories_names:
        assert category_to_sort_order[custom_category] < 100

    # Check that relative sort order of custom categories didn't change.
    del category_to_sort_order['category_4']
    del category_to_sort_order['category_5']
    sorted_custom_categories = sorted(
        category_to_sort_order.items(), key=lambda c: c[1],
    )
    assert [c[0] for c in sorted_custom_categories] == [
        'custom_category_10',
        'custom_category_2',
        'custom_category_3',
        'custom_category_1',
    ]


def sql_read_categories_relations(pgsql, sql_read_data):
    query = """select id, name from eats_nomenclature.categories"""
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(query)
    id_to_name = {row[0]: row[1] for row in cursor}
    id_to_name[None] = None

    categories_relations = sql_read_data(CATEGORIES_RELATIONS_QUERY)

    return {
        (cr[0], id_to_name[cr[1]], id_to_name[cr[2]])
        for cr in categories_relations
    }


def sql_fill_product_types(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.products
        (origin_id, name, brand_id, public_id)
        values ('item_origin_4', 'item_4', 1,
                '44444444444444444444444444444444'),
               ('item_origin_5', 'item_5', 1,
                '55555555555555555555555555555555');

        insert into eats_nomenclature.places_products
        (place_id, product_id, origin_id, available_from)
        values (1, 4, 'item_origin_4', '2017-01-08 04:05:06'),
               (1, 5, 'item_origin_5', '2017-01-08 04:05:06');

        insert into eats_nomenclature.product_types
        (value_uuid, value)
        values ('value_uuid1', 'value1'),
               ('value_uuid2', 'value2');

        insert into eats_nomenclature.product_brands
        (value_uuid, value)
        values ('brand_value_uuid1', 'brand_value_1');

        insert into eats_nomenclature.product_attributes
        (product_id, product_brand_id, product_type_id)
        values (4, 1, 1),
               (5, 1, 1);
        """,
    )


def sql_fill_sku_product_types(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.sku (id, uuid, alternate_name)
        values (1, '11111111-1111-1111-1111-111111111111', 'name1'),
               (2, '22222222-2222-2222-2222-222222222222', 'name2');

        insert into eats_nomenclature.products
        (origin_id, name, brand_id, public_id, sku_id)
        values ('item_origin_6', 'item_6', 1,
                '66666666666666666666666666666666', 1),
               ('item_origin_7', 'item_7', 1,
                '77777777777777777777777777777777', 1),
               ('item_origin_8', 'item_8', 1,
                '88888888888888888888888888888888', 2),
               ('item_origin_9', 'item_9', 1,
                '99999999999999999999999999999999', 1);

        insert into eats_nomenclature.product_attributes
        (product_id, product_brand_id, product_type_id)
        values (7, 1, 1);

        insert into eats_nomenclature.sku_attributes
        (sku_id, product_brand_id, product_type_id)
        values (1, 1, 2);

        insert into eats_nomenclature.overriden_product_attributes
        (product_id, product_brand_id, product_type_id)
        values (9, 1, 1);
        """,
    )


# pylint: disable=invalid-name
def sql_add_product_with_unused_type(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.products
        (origin_id, name, brand_id, public_id, sku_id)
        values ('item_origin_10', 'item_10', 1,
                '10101010101010101010101010101010', null);

        insert into eats_nomenclature.categories_products
        (assortment_id, category_id, product_id, sort_order)
        values ({assortment_id}, 4, 10, 10);

        insert into eats_nomenclature.product_types
        (value_uuid, value)
        values ('value_uuid3', 'value3');

        insert into eats_nomenclature.overriden_product_attributes
        (product_id, product_brand_id, product_type_id)
        values (10, 1, 3);
        """,
    )


# pylint: disable=invalid-name
def sql_add_product_with_unused_overriden_type(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.sku (id, uuid, alternate_name)
        values (3, '33333333-3333-3333-3333-333333333333', 'name3');

        insert into eats_nomenclature.products
        (origin_id, name, brand_id, public_id, sku_id)
        values ('item_origin_11', 'item_11', 1,
                '11111111101010101010101010101010', 3);

        insert into eats_nomenclature.sku_attributes
        (sku_id, product_brand_id, product_type_id)
        values (3, 1, 2);

        insert into eats_nomenclature.categories_products
        (assortment_id, category_id, product_id, sort_order)
        values ({assortment_id}, 4, 11, 10);

        insert into eats_nomenclature.product_types
        (value_uuid, value)
        values ('value_uuid4', 'value4');

        insert into eats_nomenclature.overriden_product_attributes
        (product_id, product_brand_id, product_type_id)
        values (11, 1, 4);
        """,
    )


def sql_add_products_with_overriden_sku(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.products
        (origin_id, name, brand_id, public_id, sku_id)
        values ('item_origin_12', 'item_12', 1,
                '00000000000000000000000000000012', 2),
               ('item_origin_13', 'item_13', 1,
                '00000000000000000000000000000013', null),
               ('item_origin_14', 'item_14', 1,
                '00000000000000000000000000000014', 1),
               ('item_origin_15', 'item_15', 1,
                '00000000000000000000000000000015', null);

        insert into eats_nomenclature.overriden_product_sku
        (product_id, sku_id)
        values (12, 1),
               (13, 1),
               (14, null),
               (15, 2);

        insert into eats_nomenclature.categories_products
        (assortment_id, category_id, product_id, sort_order)
        values
            ({assortment_id}, 2, 12, 10),
            ({assortment_id}, 2, 13, 10),
            ({assortment_id}, 2, 14, 10),
            ({assortment_id}, 2, 15, 10);

        insert into eats_nomenclature.overriden_product_attributes
        (product_id, product_brand_id, product_type_id)
        values (15, 1, 2);
        """,
    )


def sql_insert_categories_products(pgsql, assortment_id, category_products):
    cursor = pgsql['eats_nomenclature'].cursor()
    for category_product in category_products:
        cursor.execute(
            f"""
            insert into eats_nomenclature.categories_products
            (assortment_id, category_id, product_id, sort_order)
            values (
                {assortment_id},
                {category_product[0]},
                {category_product[1]},
                {category_product[2]}
            );""",
        )


def sql_set_use_only_custom_flag(pgsql, use_only_custom_categories, trait_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature.assortment_traits
        set is_full_custom = {use_only_custom_categories}
        where id = {trait_id}
        """,
    )


def sql_disable_custom_groups(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature.brands_custom_categories_groups
        set is_enabled = false
        """,
    )


@pytest.fixture(name='fill_custom_categories_group')
async def _fill_custom_categories_group(taxi_eats_nomenclature, load_json):
    async def do_smth(request_file):
        response = await taxi_eats_nomenclature.post(
            '/v1/manage/custom_categories_groups',
            json=load_json(request_file),
        )
        group_id = response.json()['group_id']
        return group_id

    return do_smth


def sql_reset_custom_category_pic(pgsql, custom_category_name):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature.custom_categories
        set picture_id = null
        where name = '{custom_category_name}'
        """,
    )
