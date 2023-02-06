import pytest

HANDLER = '/eats/v1/retail-seo/v1/category-seo-queries'


@pytest.mark.pgsql('eats_retail_seo', files=['fill_data.sql'])
async def test_404_category_not_found(taxi_eats_retail_seo):
    category_id = 11
    response = await taxi_eats_retail_seo.get(
        HANDLER + f'?category_id={category_id}',
    )
    assert response.status == 404


@pytest.mark.parametrize('limit', [1, 3, 7])
@pytest.mark.pgsql('eats_retail_seo', files=['fill_data.sql'])
async def test_category_seo_queries(taxi_eats_retail_seo, limit):
    expected_seo_queries_ids_dict = {
        1: [1, 5, 2, 6],
        2: [5, 4, 3],
        3: [5, 4, 3],
        4: [1, 5, 2, 4, 3, 6],
        5: [7],
        6: [7],
    }
    for category_id in expected_seo_queries_ids_dict:
        response = await taxi_eats_retail_seo.get(
            HANDLER + f'?category_id={category_id}&limit={limit}',
        )
        assert response.status == 200
        response_json = response.json()
        assert 'seo_queries' in response_json
        handle_seo_queries = response_json['seo_queries']
        expected_seo_queries_ids = expected_seo_queries_ids_dict[category_id]
        expected_seo_queries = _get_expected_seo_queries(
            expected_seo_queries_ids,
        )[:limit]
        assert handle_seo_queries == expected_seo_queries


def _get_expected_seo_queries(ids):
    expected_seo_queries_list = [
        {
            'slug': 'new_slug_1',
            'query': 'new_query_1',
            'title': 'new_title_1',
            'description': 'new_description_1',
            'product_type': 'product_type_1',
            'product_brand': 'product_brand_1',
        },
        {
            'slug': 'new_slug_2',
            'query': 'new_query_2',
            'title': 'new_title_2',
            'description': 'new_description_2',
            'product_type': 'product_type_2',
            'product_brand': 'product_brand_2',
        },
        {
            'slug': 'slug_3',
            'query': 'query_3',
            'title': 'title_3',
            'description': 'description_3',
            'product_type': 'product_type_3',
            'product_brand': 'product_brand_3',
        },
        {
            'slug': 'slug_4',
            'query': 'query_4',
            'title': 'title_4',
            'description': 'description_4',
            'product_type': 'product_type_3',
        },
        {
            'slug': 'slug_5',
            'query': 'query_5',
            'title': 'title_5',
            'description': 'description_5',
            'product_brand': 'product_brand_3',
        },
        {
            'slug': 'slug_7',
            'query': 'query_7',
            'title': 'title_7',
            'description': 'description_7',
            'product_brand': 'product_brand_3',
            'product_type': 'product_type_2',
        },
        {
            'slug': 'slug_8',
            'query': 'query_8',
            'title': 'title_8',
            'description': 'description_8',
            'product_type': 'product_type_4',
        },
    ]
    expected_seo_queries = []
    for seo_query_id in ids:
        expected_seo_queries.append(
            expected_seo_queries_list[seo_query_id - 1],
        )
    return expected_seo_queries
