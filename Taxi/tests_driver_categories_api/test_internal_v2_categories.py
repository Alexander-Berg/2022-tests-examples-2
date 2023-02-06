import pytest


_PG_QUERIES = [
    'INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES '
    '(\'category1\',\'type1\',\'2020-01-01 00:00:00+00\',\'{}\'), '
    '(\'category2\',\'type2\',\'2020-01-02 00:00:00+00\',\'{'
    '  "taximeter_value":1,'
    '  "restriction_value":2,'
    '  "taximeter_sort_order":3,'
    '  "taximeter_name":"category22",'
    '  "old_client_name":"category222",'
    '  "db_cars_name":"category2222",'
    '  "is_hidden":true,'
    '  "park_feature_config":"config2",'
    '  "park_city_country_feature_config":"config22"'
    '}\')',
]


@pytest.mark.config(
    DRIVER_CATEGORIES_API_CATEGORIES_DESCRIPTIONS={
        'category2': {
            '__default__': {
                'name_key': 'tanker1',
                'short_name_key': 'tanker2',
            },
        },
    },
)
@pytest.mark.pgsql('driver-categories-api', queries=_PG_QUERIES)
@pytest.mark.parametrize(
    'body, http_code, expected_response',
    [
        pytest.param(
            {},
            200,
            {
                'categories': [
                    {
                        'name': 'category1',
                        'type': 'type1',
                        'tanker_key_name': '',
                        'tanker_key_short_name': '',
                        'bit_mask': 0,
                        'taximeter_sort_order': 9223372036854775807,
                        'is_hidden': False,
                    },
                    {
                        'name': 'category2',
                        'type': 'type2',
                        'tanker_key_name': 'tanker1',
                        'tanker_key_short_name': 'tanker2',
                        'bit_mask': 1,
                        'restriction_bit_mask': 2,
                        'taximeter_sort_order': 3,
                        'is_hidden': True,
                        'taximeter_name': 'category22',
                        'old_client_name': 'category222',
                        'db_cars_name': 'category2222',
                    },
                ],
                'updated_at': '2020-01-02T00:00:00+00:00',
            },
            id='empty_body',
        ),
        pytest.param(
            {'categories': ['category1']},
            200,
            {
                'categories': [
                    {
                        'name': 'category1',
                        'type': 'type1',
                        'tanker_key_name': '',
                        'tanker_key_short_name': '',
                        'bit_mask': 0,
                        'taximeter_sort_order': 9223372036854775807,
                        'is_hidden': False,
                    },
                ],
                'updated_at': '2020-01-01T00:00:00+00:00',
            },
            id='fetch_category1',
        ),
        pytest.param(
            {'categories': ['category1', 'unknown']},
            200,
            {
                'categories': [
                    {
                        'name': 'category1',
                        'type': 'type1',
                        'tanker_key_name': '',
                        'tanker_key_short_name': '',
                        'bit_mask': 0,
                        'taximeter_sort_order': 9223372036854775807,
                        'is_hidden': False,
                    },
                ],
                'updated_at': '2020-01-01T00:00:00+00:00',
            },
            id='fetch_category1_and_unknown',
        ),
        pytest.param(
            {'categories': ['category1', 'category2']},
            200,
            {
                'categories': [
                    {
                        'name': 'category1',
                        'type': 'type1',
                        'tanker_key_name': '',
                        'tanker_key_short_name': '',
                        'bit_mask': 0,
                        'taximeter_sort_order': 9223372036854775807,
                        'is_hidden': False,
                    },
                    {
                        'name': 'category2',
                        'type': 'type2',
                        'tanker_key_name': 'tanker1',
                        'tanker_key_short_name': 'tanker2',
                        'bit_mask': 1,
                        'restriction_bit_mask': 2,
                        'taximeter_sort_order': 3,
                        'is_hidden': True,
                        'taximeter_name': 'category22',
                        'old_client_name': 'category222',
                        'db_cars_name': 'category2222',
                    },
                ],
                'updated_at': '2020-01-02T00:00:00+00:00',
            },
            id='fetch_all',
        ),
        pytest.param(
            {'categories': []},
            200,
            {'categories': [], 'updated_at': '1970-01-01T00:00:00+00:00'},
            id='empty_categories',
        ),
    ],
)
async def test_post(
        taxi_driver_categories_api, body, http_code, expected_response,
):
    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        '/internal/v2/categories', json=body,
    )

    assert response.status_code == http_code

    got_response = response.json()
    got_response['categories'].sort(key=lambda x: x['name'])
    assert got_response == expected_response
