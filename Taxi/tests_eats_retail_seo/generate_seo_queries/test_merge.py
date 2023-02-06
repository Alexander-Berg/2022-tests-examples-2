from .. import models


PERIODIC_NAME = 'generate-seo-queries-periodic'


async def test_merge(
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
    product_brand_1 = models.ProductBrand('Простоквашино')
    product_brand_2 = models.ProductBrand('Домик в деревне')
    product_brands = [product_brand_1, product_brand_2]

    product_type_1 = models.ProductType(name='Молоко')
    product_type_1.set_product_brands([product_brand_1, product_brand_2])
    product_types = [product_type_1]

    category_1 = models.Category(category_id='123', name='Молоко и яйца')
    category_1.set_product_types(product_types)
    categories = [category_1]

    seo_query_1_not_changed = models.SeoQuery(
        product_type=product_type_1,
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='moloko-prostokvashino',
            query='Молоко Простоквашино',
            title='Молоко Простоквашино',
            description='Молоко Простоквашино',
        ),
    )
    seo_query_2_will_be_changed = models.SeoQuery(
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='old-prostokvashino',
            query='Старое Простоквашино',
            title='Старое Простоквашино',
            description='Старое Простоквашино',
            priority=50,
        ),
    )
    initial_seo_queries = [
        seo_query_1_not_changed,
        seo_query_2_will_be_changed,
    ]

    seo_query_2_changed = models.SeoQuery(
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='prostokvashino',
            query='Простоквашино',
            title='Простоквашино',
            description='Простоквашино',
            priority=100,
        ),
    )
    seo_query_3_new_by_brand = models.SeoQuery(
        product_brand=product_brand_2,
        generated_data=models.SeoQueryData(
            slug='domik-v-derevne',
            query='Домик в деревне',
            title='Домик в деревне',
            description='Домик в деревне',
        ),
    )
    seo_query_4_new_by_type = models.SeoQuery(
        product_type=product_type_1,
        generated_data=models.SeoQueryData(
            slug='moloko',
            query='Молоко',
            title='Молоко',
            description='Молоко',
        ),
    )
    seo_query_5_new_by_type_and_brand = (  # pylint: disable=C0103
        models.SeoQuery(
            product_type=product_type_1,
            product_brand=product_brand_2,
            generated_data=models.SeoQueryData(
                slug='moloko-domik-v-derevne',
                query='Молоко Домик в деревне',
                title='Молоко Домик в деревне',
                description='Молоко Домик в деревне',
            ),
        )
    )
    expected_seo_queries = [
        seo_query_1_not_changed,
        seo_query_2_changed,
        seo_query_3_new_by_brand,
        seo_query_4_new_by_type,
        seo_query_5_new_by_type_and_brand,
    ]

    return [
        product_brands,
        product_types,
        categories,
        initial_seo_queries,
        expected_seo_queries,
    ]
