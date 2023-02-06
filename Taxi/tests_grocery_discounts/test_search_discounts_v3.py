import pytest

from tests_grocery_discounts import common


@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
async def test_admin_search_rules_v3(taxi_grocery_discounts):
    request = {
        'hierarchy_name': 'menu_discounts',
        'conditions': [
            {'condition_name': 'country', 'values': ['russia']},
            {'condition_name': 'city', 'values': []},
            {'condition_name': 'depot', 'values': []},
            {'condition_name': 'group', 'values': ['food']},
            {'condition_name': 'product', 'values': []},
            {
                'condition_name': 'active_period',
                'values': [
                    {
                        'start': '2020-01-01T10:00:00+00:00',
                        'is_start_utc': False,
                        'is_end_utc': False,
                        'end': '2021-02-10T18:00:00+00:00',
                    },
                ],
            },
        ],
    }

    response = await taxi_grocery_discounts.post(
        '/v3/admin/match-discounts/search-rules',
        request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'discount_data' in response_json
    rules = response_json['discount_data']
    assert rules['hierarchy_name'] == 'menu_discounts'
    assert len(rules['discounts']) == 2
    item = rules['discounts'][0]
    assert item['meta_info']['create_draft_id'] == 'grocery_draft_id_test'
    assert item['match_path'] == [
        {'condition_name': 'class', 'value': 'No class'},
        {'condition_name': 'experiment', 'value_type': 'Other'},
        {'condition_name': 'tag', 'value_type': 'Other'},
        {'condition_name': 'has_yaplus', 'value_type': 'Other'},
        {'condition_name': 'country', 'value': 'russia'},
        {'condition_name': 'city', 'exclusions': ['spb'], 'value_type': 'Any'},
        {'condition_name': 'depot', 'value_type': 'Other'},
        {'condition_name': 'master_group', 'value_type': 'Other'},
        {'condition_name': 'group', 'value': 'food'},
        {'condition_name': 'product', 'value_type': 'Any'},
        {'condition_name': 'orders_restriction', 'value_type': 'Other'},
        {
            'condition_name': 'active_period',
            'value': {
                'end': '2020-02-10T18:00:00+00:00',
                'is_start_utc': False,
                'is_end_utc': False,
                'start': '2020-01-01T10:00:00+00:00',
            },
        },
    ]
    assert item['discount'] == {
        'active_with_surge': True,
        'description': 'Test',
        'values_with_schedules': [
            {
                'money_value': {
                    'menu_value': {'value_type': 'absolute', 'value': '1.0'},
                },
                'schedule': {
                    'timezone': 'LOCAL',
                    'intervals': [
                        {'exclude': False, 'day': [1, 2, 3, 4, 5, 6, 7]},
                    ],
                },
            },
        ],
    }
