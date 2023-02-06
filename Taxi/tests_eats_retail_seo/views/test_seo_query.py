import pytest

HANDLER = '/eats/v1/retail-seo/v1/seo-query'


@pytest.mark.pgsql('eats_retail_seo', files=['fill_data.sql'])
async def test_404_slug_not_found(taxi_eats_retail_seo):
    not_found_slugs = ['unknown_slug', 'old_slug_1', 'slug_6_disabled']
    for not_found_slug in not_found_slugs:
        response = await taxi_eats_retail_seo.get(
            HANDLER + f'?slug={not_found_slug}',
        )
        assert response.status == 404


@pytest.mark.pgsql('eats_retail_seo', files=['fill_data.sql'])
async def test_seo_query(taxi_eats_retail_seo):
    seo_slugs = [
        'new_slug_1',
        'new_slug_2',
        'slug_3',
        'slug_4',
        'slug_5',
        'slug_7',
        'slug_8',
    ]
    expected_slug_to_seo_query = _get_expected_slug_to_seo_query()
    for seo_slug in seo_slugs:
        response = await taxi_eats_retail_seo.get(
            HANDLER + f'?slug={seo_slug}',
        )
        assert response.status == 200
        assert response.json() == expected_slug_to_seo_query[seo_slug]


def _get_expected_slug_to_seo_query():
    return {
        'new_slug_1': {
            'slug': 'new_slug_1',
            'query': 'new_query_1',
            'title': 'new_title_1',
            'description': 'new_description_1',
            'product_type': 'product_type_1',
            'product_brand': 'product_brand_1',
        },
        'new_slug_2': {
            'slug': 'new_slug_2',
            'query': 'new_query_2',
            'title': 'new_title_2',
            'description': 'new_description_2',
            'product_type': 'product_type_2',
            'product_brand': 'product_brand_2',
        },
        'slug_3': {
            'slug': 'slug_3',
            'query': 'query_3',
            'title': 'title_3',
            'description': 'description_3',
            'product_type': 'product_type_3',
            'product_brand': 'product_brand_3',
        },
        'slug_4': {
            'slug': 'slug_4',
            'query': 'query_4',
            'title': 'title_4',
            'description': 'description_4',
            'product_type': 'product_type_3',
        },
        'slug_5': {
            'slug': 'slug_5',
            'query': 'query_5',
            'title': 'title_5',
            'description': 'description_5',
            'product_brand': 'product_brand_3',
        },
        'slug_7': {
            'slug': 'slug_7',
            'query': 'query_7',
            'title': 'title_7',
            'description': 'description_7',
            'product_brand': 'product_brand_3',
            'product_type': 'product_type_2',
        },
        'slug_8': {
            'slug': 'slug_8',
            'query': 'query_8',
            'title': 'title_8',
            'description': 'description_8',
            'product_type': 'product_type_4',
        },
    }
