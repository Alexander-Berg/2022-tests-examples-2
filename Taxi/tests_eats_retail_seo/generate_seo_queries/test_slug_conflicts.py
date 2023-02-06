from .. import models


PERIODIC_NAME = 'generate-seo-queries-periodic'


async def test_slug_conflicts(
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
    ] = _generate_data()
    save_product_brands_to_db(product_brands)
    save_product_types_to_db(product_types)
    save_categories_to_db(categories)
    save_seo_queries_to_db(initial_seo_queries)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    assert_objects_lists(get_seo_queries_from_db(), expected_seo_queries)

    assert periodic_finished.times_called == 1


def _generate_data():
    product_brand_1 = models.ProductBrand('Домик в деревне')
    product_brand_2_slug_conflict = models.ProductBrand(
        'Молоко Домик в деревне',
    )
    product_brands = [product_brand_1, product_brand_2_slug_conflict]

    product_type_1 = models.ProductType(name=' Молоко ')
    product_type_1.set_product_brands(product_brands)
    product_types = [product_type_1]

    category_1 = models.Category(category_id='123', name='Молоко и яйца')
    category_1.set_product_types(product_types)
    categories = [category_1]

    seo_query_1_old_by_type_brand = models.SeoQuery(
        product_type=product_type_1,
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='moloko-domik-v-derevne',
            query='Молоко Домик в деревне',
            title='Молоко Домик в деревне',
            description='Молоко Домик в деревне',
        ),
    )
    initial_seo_queries = [seo_query_1_old_by_type_brand]

    seo_query_2_new_by_brand = models.SeoQuery(
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='domik-v-derevne',
            query='Домик в деревне',
            title='Домик в деревне',
            description='Домик в деревне',
        ),
    )
    seo_query_3_new_by_type = models.SeoQuery(
        product_type=product_type_1,
        generated_data=models.SeoQueryData(
            slug='moloko',
            query='Молоко',
            title='Молоко',
            description='Молоко',
        ),
    )
    seo_query_4_conflict = models.SeoQuery(
        product_brand=product_brand_2_slug_conflict,
    )  # conflicts with seo_query_1 by slug
    seo_query_5_new_by_type_brand = models.SeoQuery(
        product_type=product_type_1,
        product_brand=product_brand_2_slug_conflict,
        generated_data=models.SeoQueryData(
            slug='moloko-moloko-domik-v-derevne',
            query='Молоко Молоко Домик в деревне',
            title='Молоко Молоко Домик в деревне',
            description='Молоко Молоко Домик в деревне',
        ),
    )
    expected_seo_queries = [
        seo_query_1_old_by_type_brand,
        seo_query_2_new_by_brand,
        seo_query_3_new_by_type,
        seo_query_4_conflict,
        seo_query_5_new_by_type_brand,
    ]

    return [
        product_brands,
        product_types,
        categories,
        initial_seo_queries,
        expected_seo_queries,
    ]
