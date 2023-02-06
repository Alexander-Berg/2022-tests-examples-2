import copy

from .. import models


PERIODIC_NAME = 'generate-seo-queries-periodic'


async def test_type_brand_changed(
        assert_objects_lists,
        enable_periodic_in_config,
        get_seo_queries_from_db,
        save_product_brands_to_db,
        save_product_types_to_db,
        save_categories_to_db,
        save_seo_queries_to_db,
        taxi_eats_retail_seo,
        testpoint,
):
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(PERIODIC_NAME)

    [
        product_brands,
        product_types,
        categories,
        initial_seo_queries,
        expected_seo_queries,
        expected_next_time_seo_queries,
    ] = _generate_data()
    save_product_brands_to_db(product_brands)
    save_product_types_to_db(product_types)
    save_categories_to_db(categories)
    save_seo_queries_to_db(initial_seo_queries)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)
    assert_objects_lists(get_seo_queries_from_db(), expected_seo_queries)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)
    assert_objects_lists(
        get_seo_queries_from_db(), expected_next_time_seo_queries,
    )

    assert periodic_finished.times_called == 2


def _generate_data():
    product_brand_1_old = models.ProductBrand('Annas')
    product_brand_1_new = models.ProductBrand('Anna\'s')
    product_brands = [product_brand_1_old, product_brand_1_new]

    product_type_1 = models.ProductType(name='Песочное печенье')
    product_type_1.set_product_brands([product_brand_1_new])
    product_types = [product_type_1]

    category_1 = models.Category(category_id='123', name='Печенье и вафли')
    category_1.set_product_types(product_types)
    categories = [category_1]

    seo_query_1_will_be_reset = models.SeoQuery(
        product_type=product_type_1,
        product_brand=product_brand_1_old,
        generated_data=models.SeoQueryData(
            slug='pesochnoe-pechene-annas',
            query='Песочное печенье Annas',
            title='Песочное печенье Annas',
            description='Песочное печенье Annas',
        ),
    )
    seo_query_2_old_brand = models.SeoQuery(
        product_brand=product_brand_1_old,
        generated_data=models.SeoQueryData(
            slug='annas', query='Annas', title='Annas', description='Annas',
        ),
    )
    initial_seo_queries = [seo_query_1_will_be_reset, seo_query_2_old_brand]

    seo_query_1_reset = copy.deepcopy(seo_query_1_will_be_reset)
    seo_query_1_reset.generated_data = None
    seo_query_2_reset = copy.deepcopy(seo_query_2_old_brand)
    seo_query_2_reset.generated_data = None
    seo_query_3_new_by_type = models.SeoQuery(
        product_type=product_type_1,
        generated_data=models.SeoQueryData(
            slug='pesochnoe-pechene',
            query='Песочное печенье',
            title='Песочное печенье',
            description='Песочное печенье',
        ),
    )
    # conflicts with seo_query_2 by slug currently
    # but will be filled next time
    seo_query_4_conflict = models.SeoQuery(product_brand=product_brand_1_new)
    # conflicts with seo_query_1 by slug currently
    # but will be filled next time
    seo_query_5_conflict = models.SeoQuery(
        product_type=product_type_1, product_brand=product_brand_1_new,
    )
    expected_seo_queries = [
        seo_query_1_reset,
        seo_query_2_reset,
        seo_query_3_new_by_type,
        seo_query_4_conflict,
        seo_query_5_conflict,
    ]

    seo_query_4_filled = models.SeoQuery(
        product_brand=product_brand_1_new,
        generated_data=models.SeoQueryData(
            slug='annas',
            query='Anna\'s',
            title='Anna\'s',
            description='Anna\'s',
        ),
    )
    seo_query_5_filled = models.SeoQuery(
        product_type=product_type_1,
        product_brand=product_brand_1_new,
        generated_data=models.SeoQueryData(
            slug='pesochnoe-pechene-annas',
            query='Песочное печенье Anna\'s',
            title='Песочное печенье Anna\'s',
            description='Песочное печенье Anna\'s',
        ),
    )
    expected_next_time_seo_queries = [
        seo_query_1_reset,
        seo_query_2_reset,
        seo_query_3_new_by_type,
        seo_query_4_filled,
        seo_query_5_filled,
    ]

    return [
        product_brands,
        product_types,
        categories,
        initial_seo_queries,
        expected_seo_queries,
        expected_next_time_seo_queries,
    ]
