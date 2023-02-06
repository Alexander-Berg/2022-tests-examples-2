from typing import Optional

import pytest

PARAMETRIZE = [
    pytest.param(
        {
            'hierarchy_name': 'menu_discounts',
            'conditions': [
                {'condition_name': 'class', 'values': ['No class']},
                {'condition_name': 'experiment', 'values': ['example']},
                {'condition_name': 'country', 'values': ['russia']},
                {'condition_name': 'city', 'values': ['Moscow']},
                {'condition_name': 'group', 'values': ['food']},
            ],
            'type': 'FETCH',
        },
        200,
        {
            'discount_data': {
                'discounts': [
                    {
                        'discount': {
                            'active_with_surge': True,
                            'description': 'Test',
                            'values_with_schedules': [
                                {
                                    'money_value': {
                                        'menu_value': {
                                            'value': '1.0',
                                            'value_type': 'absolute',
                                        },
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
                            {'condition_name': 'class', 'value': 'No class'},
                            {
                                'condition_name': 'experiment',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'tag', 'value_type': 'Other'},
                            {
                                'condition_name': 'has_yaplus',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'country', 'value': 'russia'},
                            {
                                'condition_name': 'city',
                                'exclusions': ['spb'],
                                'value_type': 'Any',
                            },
                            {'condition_name': 'depot', 'value_type': 'Other'},
                            {
                                'condition_name': 'master_group',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'group', 'value': 'food'},
                            {'condition_name': 'product', 'value_type': 'Any'},
                            {
                                'condition_name': 'orders_restriction',
                                'value_type': 'Other',
                            },
                            {
                                'condition_name': 'active_period',
                                'value': {
                                    'end': '2020-02-10T18:00:00+00:00',
                                    'is_start_utc': False,
                                    'is_end_utc': False,
                                    'start': '2020-01-01T10:00:00+00:00',
                                },
                            },
                        ],
                        'meta_info': {
                            'create_draft_id': 'grocery_draft_id_test',
                            'create_multidraft_id': 'create_multidraft_id',
                            'create_author': 'create_author',
                        },
                    },
                ],
                'hierarchy_name': 'menu_discounts',
            },
        },
        id='fetch_ok',
    ),
    pytest.param(
        {
            'hierarchy_name': 'menu_discounts',
            'conditions': [],
            'type': 'FETCH',
            'draft_ids': ['invalid'],
        },
        200,
        {
            'discount_data': {
                'discounts': [],
                'hierarchy_name': 'menu_discounts',
            },
        },
        id='fetch_with_invalid_draft_id',
    ),
    pytest.param(
        {
            'hierarchy_name': 'menu_discounts',
            'conditions': [],
            'type': 'FETCH',
            'multidraft_ids': ['invalid'],
        },
        200,
        {
            'discount_data': {
                'discounts': [],
                'hierarchy_name': 'menu_discounts',
            },
        },
        id='fetch_with_invalid_multidraft_id',
    ),
    pytest.param(
        {
            'hierarchy_name': 'menu_discounts',
            'conditions': [],
            'type': 'WEAK_MATCH',
            'draft_ids': ['grocery_draft_id_test'],
        },
        200,
        {
            'discount_data': {
                'discounts': [
                    {
                        'discount': {
                            'active_with_surge': True,
                            'description': 'Test',
                            'values_with_schedules': [
                                {
                                    'money_value': {
                                        'menu_value': {
                                            'value': '1.0',
                                            'value_type': 'absolute',
                                        },
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
                            {'condition_name': 'class', 'value': 'No class'},
                            {
                                'condition_name': 'experiment',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'tag', 'value_type': 'Other'},
                            {
                                'condition_name': 'has_yaplus',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'country', 'value': 'russia'},
                            {
                                'condition_name': 'city',
                                'exclusions': ['spb'],
                                'value_type': 'Any',
                            },
                            {'condition_name': 'depot', 'value_type': 'Other'},
                            {
                                'condition_name': 'master_group',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'group', 'value': 'food'},
                            {'condition_name': 'product', 'value_type': 'Any'},
                            {
                                'condition_name': 'orders_restriction',
                                'value_type': 'Other',
                            },
                            {
                                'condition_name': 'active_period',
                                'value': {
                                    'end': '2020-02-10T18:00:00+00:00',
                                    'is_start_utc': False,
                                    'is_end_utc': False,
                                    'start': '2020-01-01T10:00:00+00:00',
                                },
                            },
                        ],
                        'meta_info': {
                            'create_draft_id': 'grocery_draft_id_test',
                            'create_multidraft_id': 'create_multidraft_id',
                            'create_author': 'create_author',
                        },
                    },
                ],
                'hierarchy_name': 'menu_discounts',
            },
        },
        id='draft_id',
    ),
    pytest.param(
        {
            'hierarchy_name': 'menu_discounts',
            'conditions': [],
            'type': 'WEAK_MATCH',
            'multidraft_ids': ['create_multidraft_id'],
        },
        200,
        {
            'discount_data': {
                'discounts': [
                    {
                        'discount': {
                            'active_with_surge': True,
                            'description': 'Test',
                            'values_with_schedules': [
                                {
                                    'money_value': {
                                        'menu_value': {
                                            'value': '1.0',
                                            'value_type': 'absolute',
                                        },
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
                            {'condition_name': 'class', 'value': 'No class'},
                            {
                                'condition_name': 'experiment',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'tag', 'value_type': 'Other'},
                            {
                                'condition_name': 'has_yaplus',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'country', 'value': 'russia'},
                            {
                                'condition_name': 'city',
                                'exclusions': ['spb'],
                                'value_type': 'Any',
                            },
                            {'condition_name': 'depot', 'value_type': 'Other'},
                            {
                                'condition_name': 'master_group',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'group', 'value': 'food'},
                            {'condition_name': 'product', 'value_type': 'Any'},
                            {
                                'condition_name': 'orders_restriction',
                                'value_type': 'Other',
                            },
                            {
                                'condition_name': 'active_period',
                                'value': {
                                    'end': '2020-02-10T18:00:00+00:00',
                                    'is_start_utc': False,
                                    'is_end_utc': False,
                                    'start': '2020-01-01T10:00:00+00:00',
                                },
                            },
                        ],
                        'meta_info': {
                            'create_draft_id': 'grocery_draft_id_test',
                            'create_multidraft_id': 'create_multidraft_id',
                            'create_author': 'create_author',
                        },
                    },
                ],
                'hierarchy_name': 'menu_discounts',
            },
        },
        id='multidraft_id',
    ),
    pytest.param(
        {
            'hierarchy_name': 'menu_discounts',
            'conditions': [
                {'condition_name': 'group', 'values': ['food']},
                {'condition_name': 'product', 'values': 'Any'},
            ],
            'type': 'WEAK_MATCH',
        },
        200,
        {
            'discount_data': {
                'discounts': [
                    {
                        'discount': {
                            'active_with_surge': True,
                            'description': 'Test',
                            'values_with_schedules': [
                                {
                                    'money_value': {
                                        'menu_value': {
                                            'value': '1.0',
                                            'value_type': 'absolute',
                                        },
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
                            {'condition_name': 'class', 'value': 'No class'},
                            {
                                'condition_name': 'experiment',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'tag', 'value_type': 'Other'},
                            {
                                'condition_name': 'has_yaplus',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'country', 'value': 'russia'},
                            {
                                'condition_name': 'city',
                                'exclusions': ['spb'],
                                'value_type': 'Any',
                            },
                            {'condition_name': 'depot', 'value_type': 'Other'},
                            {
                                'condition_name': 'master_group',
                                'value_type': 'Other',
                            },
                            {'condition_name': 'group', 'value': 'food'},
                            {'condition_name': 'product', 'value_type': 'Any'},
                            {
                                'condition_name': 'orders_restriction',
                                'value_type': 'Other',
                            },
                            {
                                'condition_name': 'active_period',
                                'value': {
                                    'end': '2020-02-10T18:00:00+00:00',
                                    'is_start_utc': False,
                                    'is_end_utc': False,
                                    'start': '2020-01-01T10:00:00+00:00',
                                },
                            },
                        ],
                        'meta_info': {
                            'create_draft_id': 'grocery_draft_id_test',
                            'create_multidraft_id': 'create_multidraft_id',
                            'create_author': 'create_author',
                        },
                    },
                ],
                'hierarchy_name': 'menu_discounts',
            },
        },
        id='weak_match',
    ),
    pytest.param(
        {
            'hierarchy_name': 'menu_discounts',
            'conditions': [
                {'condition_name': 'class', 'values': 'Any'},
                {'condition_name': 'experiment', 'values': ['example']},
                {'condition_name': 'country', 'values': ['russia']},
                {'condition_name': 'city', 'values': ['Moscow']},
                {'condition_name': 'group', 'values': ['food']},
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
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
async def test_admin_find_rules_v3(
        taxi_grocery_discounts,
        default_headers,
        data,
        expected_status,
        expected_content,
):
    response = await taxi_grocery_discounts.post(
        '/v3/admin/match-discounts/find-rules',
        json=data,
        headers=default_headers,
    )
    content = response.json()
    if response.status_code == 200:
        for item in content['discount_data']['discounts']:
            item.pop('revision')
            item.pop('discount_id')
    assert response.status_code == expected_status, content
    assert content == expected_content


async def check_pagination(
        client,
        default_headers,
        cursor: Optional[str],
        expected_meta_info: Optional[dict],
) -> Optional[dict]:
    data = {
        'hierarchy_name': 'menu_discounts',
        'conditions': [{'condition_name': 'country', 'values': ['russia']}],
        'type': 'FETCH',
    }
    if cursor is not None:
        data['cursor'] = cursor
    response = await client.post(
        '/v3/admin/match-discounts/find-rules',
        json=data,
        headers=default_headers,
    )
    assert response.status_code == 200
    content = response.json()
    discounts = content['discount_data']['discounts']
    if expected_meta_info is not None:
        assert len(discounts) == 1
        assert discounts[0]['meta_info'] == expected_meta_info
    else:
        assert not discounts
    return content.get('cursor')


@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
@pytest.mark.config(GROCERY_DISCOUNTS_FIND_RULES_SETTINGS={'max_rules': 1})
async def test_admin_find_rules_v3_pagination(client, default_headers):
    cursor = await check_pagination(
        client,
        default_headers,
        None,
        {
            'create_draft_id': 'grocery_draft_id_test_1',
            'create_multidraft_id': 'create_multidraft_id_1',
            'create_author': 'create_author_1',
        },
    )
    assert cursor
    cursor = await check_pagination(
        client,
        default_headers,
        cursor,
        {
            'create_draft_id': 'grocery_draft_id_test_2',
            'create_multidraft_id': 'create_multidraft_id_2',
            'create_author': 'create_author_2',
        },
    )
    assert cursor
    cursor = await check_pagination(client, default_headers, cursor, None)
    assert cursor is None
