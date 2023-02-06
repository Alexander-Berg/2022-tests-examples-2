import pytest

PARAMETRIZE = [
    pytest.param(
        {
            'hierarchy_name': 'menu_tags',
            'conditions': [
                {'condition_name': 'country', 'values': ['russia']},
                {'condition_name': 'city', 'values': ['Moscow']},
                {'condition_name': 'group', 'values': ['food']},
            ],
            'type': 'FETCH',
        },
        200,
        {
            'tag_data': {
                'tags': [
                    {
                        'tag': {
                            'description': 'Test',
                            'values_with_schedules': [
                                {
                                    'value': {
                                        'tag': 'some_tag_2',
                                        'kind': 'marketing',
                                    },
                                    'schedule': {
                                        'intervals': [
                                            {
                                                'day': [1, 2, 3, 4, 5, 6, 7],
                                                'exclude': False,
                                            },
                                        ],
                                        'timezone': 'LOCAL',
                                    },
                                },
                            ],
                        },
                        'match_path': [
                            {'condition_name': 'country', 'value': 'russia'},
                            {
                                'condition_name': 'city',
                                'exclusions': ['spb'],
                                'value_type': 'Any',
                            },
                            {'condition_name': 'depot', 'value_type': 'Other'},
                            {'condition_name': 'group', 'value': 'food'},
                            {'condition_name': 'product', 'value_type': 'Any'},
                            {
                                'condition_name': 'active_period',
                                'value': {
                                    'end': '2020-02-10T18:00:00+00:00',
                                    'is_start_utc': False,
                                    'is_end_utc': False,
                                    'start': '2020-01-01T10:00:00+00:00',
                                },
                            },
                            {
                                'condition_name': 'rule_id',
                                'value_type': 'Other',
                            },
                        ],
                        'meta_info': {
                            'create_draft_id': 'grocery_draft_id_test',
                        },
                    },
                ],
                'hierarchy_name': 'menu_tags',
            },
        },
        id='fetch_ok',
    ),
    pytest.param(
        {
            'hierarchy_name': 'menu_tags',
            'conditions': [
                {'condition_name': 'group', 'values': ['food']},
                {'condition_name': 'product', 'values': 'Any'},
            ],
            'type': 'WEAK_MATCH',
        },
        200,
        {
            'tag_data': {
                'tags': [
                    {
                        'tag': {
                            'description': 'Test',
                            'values_with_schedules': [
                                {
                                    'value': {
                                        'tag': 'some_tag_2',
                                        'kind': 'marketing',
                                    },
                                    'schedule': {
                                        'intervals': [
                                            {
                                                'day': [1, 2, 3, 4, 5, 6, 7],
                                                'exclude': False,
                                            },
                                        ],
                                        'timezone': 'LOCAL',
                                    },
                                },
                            ],
                        },
                        'match_path': [
                            {'condition_name': 'country', 'value': 'russia'},
                            {
                                'condition_name': 'city',
                                'exclusions': ['spb'],
                                'value_type': 'Any',
                            },
                            {'condition_name': 'depot', 'value_type': 'Other'},
                            {'condition_name': 'group', 'value': 'food'},
                            {'condition_name': 'product', 'value_type': 'Any'},
                            {
                                'condition_name': 'active_period',
                                'value': {
                                    'end': '2020-02-10T18:00:00+00:00',
                                    'is_start_utc': False,
                                    'is_end_utc': False,
                                    'start': '2020-01-01T10:00:00+00:00',
                                },
                            },
                            {
                                'condition_name': 'rule_id',
                                'value_type': 'Other',
                            },
                        ],
                        'meta_info': {
                            'create_draft_id': 'grocery_draft_id_test',
                        },
                    },
                ],
                'hierarchy_name': 'menu_tags',
            },
        },
        id='weak_match',
    ),
    pytest.param(
        {
            'hierarchy_name': 'menu_tags',
            'conditions': [
                {'condition_name': 'country', 'values': ['russia']},
                {'condition_name': 'city', 'values': ['Moscow']},
                {'condition_name': 'group', 'values': ['food']},
                {'condition_name': 'product', 'values': 'Any'},
            ],
            'type': 'FETCH',
        },
        400,
        {
            'code': 'Validation error',
            'message': 'Using Any/Other with \'FETCH\' type is forbidden',
        },
        id='fetch_with_any',
    ),
]


@pytest.mark.parametrize(
    'data, expected_status, expected_content', PARAMETRIZE,
)
@pytest.mark.pgsql(
    'grocery_marketing', files=['init_menu_tags.sql', 'fill_menu_tags.sql'],
)
async def test_admin_find_rules_v3(
        taxi_grocery_marketing,
        default_admin_rules_headers,
        data,
        expected_status,
        expected_content,
):
    response = await taxi_grocery_marketing.post(
        '/admin/v1/marketing/v1/match-tags/find-rules',
        json=data,
        headers=default_admin_rules_headers,
    )
    content = response.json()
    if response.status_code == 200:
        for item in content['tag_data']['tags']:
            item.pop('revision')
    assert response.status_code == expected_status, content
    assert content == expected_content
