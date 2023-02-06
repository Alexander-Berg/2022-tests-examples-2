from typing import List

import pytest

from .. import models

HANDLER = '/eats/v1/retail-seo/v1/seo-queries/list'
MAX_LIMIT = 5


@pytest.mark.config(
    EATS_RETAIL_SEO_SEO_QUERIES_LIST_HANDLER_SETTINGS={'max_limit': MAX_LIMIT},
)
@pytest.mark.parametrize('handler_limit', [1, 2, 3, 7])
async def test_seo_queries_list(
        save_seo_queries_to_db,
        taxi_eats_retail_seo,
        # parametrize params
        handler_limit,
):
    seo_queries = _generate_seo_queries()
    save_seo_queries_to_db(seo_queries)

    limit = min(handler_limit, MAX_LIMIT)
    start_idx = 0
    end_idx = limit

    expected_items = _generate_expected_items(seo_queries)
    total_response_items = []
    while True:
        response = await taxi_eats_retail_seo.get(
            f'{HANDLER}?limit={handler_limit}&offset={start_idx}',
        )
        assert response.status_code == 200

        expected_json = {'seo_queries': expected_items[start_idx:end_idx]}
        response_json = response.json()
        assert response_json == expected_json

        total_response_items += response_json['seo_queries']

        start_idx = end_idx
        end_idx += limit
        if start_idx >= len(expected_items):
            break

    assert total_response_items == expected_items


@pytest.mark.config(
    EATS_RETAIL_SEO_SEO_QUERIES_LIST_HANDLER_SETTINGS={'max_limit': MAX_LIMIT},
)
async def test_seo_queries_list_no_limit_offset(
        save_seo_queries_to_db, taxi_eats_retail_seo,
):
    seo_queries = _generate_seo_queries()
    save_seo_queries_to_db(seo_queries)

    response = await taxi_eats_retail_seo.get(HANDLER)
    assert response.status_code == 200
    expected_items = _generate_expected_items(seo_queries)
    assert response.json() == {'seo_queries': expected_items[:MAX_LIMIT]}


def _generate_expected_items(seo_queries: List[models.SeoQuery]):
    items = []
    for seo_query in seo_queries:
        seo_query_data = seo_query.get_data()
        if not seo_query.is_enabled or not seo_query_data:
            continue
        item = {
            'slug': seo_query_data.slug,
            'query': seo_query_data.query,
            'title': seo_query_data.title,
            'description': seo_query_data.description,
        }
        if seo_query.product_type:
            item['product_type'] = seo_query.product_type.name
        if seo_query.product_brand:
            item['product_brand'] = seo_query.product_brand.name
        items.append(item)

    return items


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
