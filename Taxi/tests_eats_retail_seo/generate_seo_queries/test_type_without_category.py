from .. import models


PERIODIC_NAME = 'generate-seo-queries-periodic'


async def test_type_without_category(
        assert_objects_lists,
        enable_periodic_in_config,
        get_seo_queries_from_db,
        save_product_brands_to_db,
        save_product_types_to_db,
        save_categories_to_db,
        generate_seo_query,
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
    ] = _generate_data(generate_seo_query)
    save_product_brands_to_db(product_brands)
    save_product_types_to_db(product_types)
    save_categories_to_db(categories)

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    assert_objects_lists(get_seo_queries_from_db(), expected_seo_queries)

    assert periodic_finished.times_called == 1


def _generate_data(generate_seo_query):
    product_brand_1 = models.ProductBrand('product_brand_1')
    product_brand_2 = models.ProductBrand('product_brand_2')
    product_brand_3_without_type = models.ProductBrand(
        'product_brand_3_without_type',
    )
    product_brands = [
        product_brand_1,
        product_brand_2,
        product_brand_3_without_type,
    ]

    product_type_1 = models.ProductType(name='product_type_1')
    product_type_1.set_product_brands([product_brand_1])
    product_type_without_category = models.ProductType(
        name='product_type_without_category',
    )
    product_type_without_category.set_product_brands([product_brand_2])
    product_types = [product_type_1, product_type_without_category]

    category_1 = models.Category(category_id='123', name='category_1')
    category_1.set_product_types([product_type_1])
    categories = [category_1]

    seo_query_1 = models.SeoQuery(
        product_type=product_type_1,
        generated_data=models.SeoQueryData(
            slug='product-type-1',
            query='product_type_1',
            title='product_type_1',
            description='product_type_1',
        ),
    )
    seo_query_2 = models.SeoQuery(
        product_type=product_type_1,
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='product-type-1-product-brand-1',
            query='product_type_1 product_brand_1',
            title='product_type_1 product_brand_1',
            description='product_type_1 product_brand_1',
        ),
    )
    seo_query_3 = models.SeoQuery(
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='product-brand-1',
            query='product_brand_1',
            title='product_brand_1',
            description='product_brand_1',
        ),
    )

    expected_seo_queries = [seo_query_1, seo_query_2, seo_query_3]

    return [product_brands, product_types, categories, expected_seo_queries]
