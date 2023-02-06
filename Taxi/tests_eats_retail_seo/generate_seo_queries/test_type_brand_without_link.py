from .. import models


PERIODIC_NAME = 'generate-seo-queries-periodic'


async def test_type_brand_without_link(
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
    product_brand_1_without_type = models.ProductBrand('Heinz')
    product_brands = [product_brand_1_without_type]

    product_type_1_without_brands = models.ProductType('Мясо')
    product_types = [product_type_1_without_brands]

    category_1 = models.Category(category_id='123', name='Сладости')
    category_1.set_product_types(product_types)
    categories = [category_1]

    seo_query_1_new_by_type = models.SeoQuery(
        product_type=product_type_1_without_brands,
        generated_data=models.SeoQueryData(
            slug='myaso', query='Мясо', title='Мясо', description='Мясо',
        ),
    )
    expected_seo_queries = [seo_query_1_new_by_type]

    return [product_brands, product_types, categories, expected_seo_queries]
