from .. import models

HANDLER = '/eats/v1/retail-seo/v1/seo-queries/count'


async def test_seo_queries_count(save_seo_queries_to_db, taxi_eats_retail_seo):
    seo_queries = _generate_seo_queries()
    save_seo_queries_to_db(seo_queries)

    expected_count = len(list(filter(lambda x: x.is_enabled, seo_queries)))

    response = await taxi_eats_retail_seo.get(HANDLER)
    assert response.status == 200
    assert response.json()['seo_queries_count'] == expected_count


def _generate_seo_queries():
    product_brand_1 = models.ProductBrand('product_brand_1')
    product_brand_2 = models.ProductBrand('product_brand_2')
    product_brand_3 = models.ProductBrand('product_brand_3')

    product_type_1 = models.ProductType(name='product_type_1')
    product_type_1.set_product_brands([product_brand_1])
    product_type_2 = models.ProductType(name='product_type_2')
    product_type_2.set_product_brands([product_brand_2, product_brand_3])
    product_type_3 = models.ProductType(name='product_type_3')
    product_type_3.set_product_brands([product_brand_3])
    product_type_4 = models.ProductType(name='product_type_4')
    product_type_5 = models.ProductType(name='product_type_5')

    seo_query_1 = models.SeoQuery(
        product_type=product_type_1,
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='generated-data-1',
            query='Generated Data 1',
            title='Generated Data 1',
            description='Generated Data 1',
        ),
        manual_data=models.SeoQueryData(
            slug='manual-data-1',
            query='Manual Data 1',
            title='Manual Data 1',
            description='Manual Data 1',
        ),
    )
    seo_query_2 = models.SeoQuery(
        product_type=product_type_2,
        product_brand=product_brand_2,
        generated_data=models.SeoQueryData(
            slug='generated-data-2',
            query='Generated Data 2',
            title='Generated Data 2',
            description='Generated Data 2',
        ),
    )
    seo_query_3 = models.SeoQuery(
        product_type=product_type_3,
        product_brand=product_brand_3,
        generated_data=models.SeoQueryData(
            slug='generated-data-3',
            query='Generated Data 3',
            title='Generated Data 3',
            description='Generated Data 3',
        ),
    )
    seo_query_4_only_type = models.SeoQuery(
        product_type=product_type_3,
        generated_data=models.SeoQueryData(
            slug='generated-data-4',
            query='Generated Data 4',
            title='Generated Data 4',
            description='Generated Data 4',
        ),
    )
    seo_query_5_only_brand = models.SeoQuery(
        product_brand=product_brand_3,
        generated_data=models.SeoQueryData(
            slug='generated-data-5',
            query='Generated Data 5',
            title='Generated Data 5',
            description='Generated Data 5',
        ),
    )
    seo_query_6_disabled = models.SeoQuery(
        product_brand=product_brand_1,
        is_enabled=False,
        generated_data=models.SeoQueryData(
            slug='generated-data-6',
            query='Generated Data 6',
            title='Generated Data 6',
            description='Generated Data 6',
        ),
    )
    seo_query_7 = models.SeoQuery(
        product_type=product_type_4,
        generated_data=models.SeoQueryData(
            slug='generated-data-7',
            query='Generated Data 7',
            title='Generated Data 7',
            description='Generated Data 7',
        ),
    )
    seo_query_8_disabled = models.SeoQuery(
        product_type=product_type_5,
        is_enabled=False,
        generated_data=models.SeoQueryData(
            slug='generated-data-8',
            query='Generated Data 8',
            title='Generated Data 8',
            description='Generated Data 8',
        ),
    )
    return [
        seo_query_1,
        seo_query_2,
        seo_query_3,
        seo_query_4_only_type,
        seo_query_5_only_brand,
        seo_query_6_disabled,
        seo_query_7,
        seo_query_8_disabled,
    ]
