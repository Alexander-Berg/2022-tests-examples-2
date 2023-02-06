from typing import List

import pytest

from .. import models
from .. import utils


HANDLER = '/eats/v1/retail-seo/v1/product-seo-queries'
BRAND_1_ID = '771'
PLACE_1_ID = '1001'
PRODUCT_NOMENCLATURE_ID_1 = '12331b95-1ff2-4bc4-b78d-dcaa1f69b006'


@pytest.mark.parametrize(**utils.gen_bool_params('has_type'))
@pytest.mark.parametrize(**utils.gen_bool_params('has_brand'))
async def test_product_seo_queries(
        save_brands_to_db,
        save_products_to_db,
        save_seo_queries_to_db,
        taxi_eats_retail_seo,
        # parametrize params
        has_type,
        has_brand,
):
    brand = _generate_brand()
    save_brands_to_db([brand])

    [products, seo_queries] = _generate_data(brand, has_type, has_brand)
    save_products_to_db(products)
    save_seo_queries_to_db(seo_queries)

    response = await taxi_eats_retail_seo.get(
        HANDLER + f'?product_id={PRODUCT_NOMENCLATURE_ID_1}',
    )
    assert response.status == 200
    assert response.json() == _generate_expected_response(
        seo_queries, has_type, has_brand,
    )


@pytest.mark.parametrize(
    'has_seo_queries, is_enabled',
    [
        pytest.param(False, True, id='no_seo_queries'),
        pytest.param(True, False, id='all_disabled'),
    ],
)
async def test_empty_response(
        save_brands_to_db,
        save_products_to_db,
        save_seo_queries_to_db,
        taxi_eats_retail_seo,
        # parametrize params
        has_seo_queries,
        is_enabled,
):
    brand = _generate_brand()
    save_brands_to_db([brand])

    product_type_1 = models.ProductType(name='Молоко')
    product_brand_1 = models.ProductBrand('Мираторг')
    product_1 = models.Product(
        nomenclature_id=PRODUCT_NOMENCLATURE_ID_1,
        name='Товар 1',
        brand=brand,
        origin_id='item-origin-id-1',
        product_type=product_type_1,
        product_brand=product_brand_1,
    )
    save_products_to_db([product_1])

    if has_seo_queries:
        seo_query_1 = models.SeoQuery(
            product_type=product_type_1,
            product_brand=product_brand_1,
            is_enabled=is_enabled,
            generated_data=models.SeoQueryData(
                slug='generated-data-1',
                query='Generated Data 1',
                title='Generated Data 1',
                description='Generated Data 1',
            ),
        )
        save_seo_queries_to_db([seo_query_1])

    response = await taxi_eats_retail_seo.get(
        HANDLER + f'?product_id={PRODUCT_NOMENCLATURE_ID_1}',
    )
    assert response.status == 200
    response_json = response.json()
    assert not response_json['seo_queries']


async def test_404_product_not_found(taxi_eats_retail_seo):
    product_id = '99999999-9999-9999-9999-999999999999'
    response = await taxi_eats_retail_seo.get(
        HANDLER + f'?product_id={product_id}',
    )
    assert response.status == 404


def _generate_brand():
    brand = models.Brand(brand_id=BRAND_1_ID, slug='magnit', name='Магнит')
    brand.places = {
        PLACE_1_ID: models.Place(
            place_id=PLACE_1_ID, slug='place1001', brand_id=brand.brand_id,
        ),
    }
    return brand


def _generate_data(brand, has_type, has_brand):
    product_type_1 = models.ProductType(name='Молоко')
    product_brand_1 = models.ProductBrand('Мираторг')
    product_1 = models.Product(
        nomenclature_id=PRODUCT_NOMENCLATURE_ID_1,
        name='Товар 1',
        brand=brand,
        origin_id='item-origin-id-1',
    )
    if has_type:
        product_1.product_type = product_type_1
    if has_brand:
        product_1.product_brand = product_brand_1
    products = [product_1]

    seo_query_1 = models.SeoQuery(
        product_type=product_type_1,
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='generated-data-1',
            query='Generated Data 1',
            title='Generated Data 1',
            description='Generated Data 1',
            priority=100,
        ),
        manual_data=models.SeoQueryData(
            slug='manual-data-1',
            query='Manual Data 1',
            title='Manual Data 1',
            description='Manual Data 1',
            priority=200,
        ),
    )
    seo_query_2 = models.SeoQuery(
        product_type=product_type_1,
        generated_data=models.SeoQueryData(
            slug='generated-data-2',
            query='Generated Data 2',
            title='Generated Data 2',
            description='Generated Data 2',
            priority=150,
        ),
    )
    seo_query_3 = models.SeoQuery(
        product_brand=product_brand_1,
        generated_data=models.SeoQueryData(
            slug='generated-data-3',
            query='Generated Data 3',
            title='Generated Data 3',
            description='Generated Data 3',
            priority=100,
        ),
    )
    seo_queries = [seo_query_1, seo_query_2, seo_query_3]

    return [products, seo_queries]


def _generate_expected_response(
        seo_queries: List[models.SeoQuery], has_type, has_brand,
):
    def should_include(x: models.SeoQuery):
        if has_type and not has_brand:
            return x.product_type and not x.product_brand
        if not has_type and has_brand:
            return not x.product_type and x.product_brand
        if has_type and has_brand:
            return x.product_type or x.product_brand
        return False

    items = []
    for seo_query in seo_queries:
        if not should_include(seo_query):
            continue
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
    return {'seo_queries': items}
