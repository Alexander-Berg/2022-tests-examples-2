from .. import models


PERIODIC_NAME = 'generate-seo-queries-periodic'


async def test_data_generation(
        assert_objects_lists,
        enable_periodic_in_config,
        get_seo_queries_from_db,
        save_product_brands_to_db,
        save_product_types_to_db,
        save_categories_to_db,
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
        expected_seo_queries,
    ] = _generate_data()
    save_product_brands_to_db(product_brands)
    save_product_types_to_db(product_types)
    save_categories_to_db(categories)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    assert_objects_lists(get_seo_queries_from_db(), expected_seo_queries)

    assert periodic_finished.times_called == 1


def _generate_data():
    product_brand_1 = models.ProductBrand('   "M&M\'s"   ')
    product_brands = [product_brand_1]

    product_type_1 = models.ProductType(name='Конфет\'ы   ')
    product_type_1.set_product_brands([product_brand_1])
    product_types = [product_type_1]

    category_1 = models.Category(category_id='123', name='Сладости')
    category_1.set_product_types(product_types)
    categories = [category_1]

    seo_query_1 = models.SeoQuery(
        product_type=product_type_1,
        generated_data=models.SeoQueryData(
            slug='konfety',
            query='Конфет\'ы',
            title='Конфет\'ы',
            description='Конфет\'ы',
        ),
    )
    seo_query_2 = models.SeoQuery(
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='mms',
            query='"M&M\'s"',
            title='"M&M\'s"',
            description='"M&M\'s"',
        ),
    )
    seo_query_3 = models.SeoQuery(
        product_type=product_type_1,
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='konfety-mms',
            query='Конфет\'ы "M&M\'s"',
            title='Конфет\'ы "M&M\'s"',
            description='Конфет\'ы "M&M\'s"',
        ),
    )
    expected_seo_queries = [seo_query_1, seo_query_2, seo_query_3]

    return [product_brands, product_types, categories, expected_seo_queries]
