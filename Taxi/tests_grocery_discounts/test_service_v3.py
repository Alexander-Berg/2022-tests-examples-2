# pylint: disable=too-many-lines
import copy

import pytest

from tests_grocery_discounts import common

ADD_RULES_QUERY = {
    'rules': [
        {'condition_name': 'experiment', 'values': ['testExp1']},
        {'condition_name': 'city', 'values': 'Any', 'exclusions': ['spb']},
        {'condition_name': 'country', 'values': ['russia']},
        {'condition_name': 'depot', 'values': 'Other'},
        {'condition_name': 'group', 'values': ['food']},
        {'condition_name': 'product', 'values': 'Any'},
        {
            'condition_name': 'active_period',
            'values': [
                {
                    'start': '2020-01-01T10:00:00+0000',
                    'end': '2020-02-10T18:00:00+0000',
                },
            ],
        },
    ],
    'update_existing_discounts': True,
    'revisions': [],
    'data': {
        'hierarchy_name': 'menu_discounts',
        'discount': {
            'active_with_surge': True,
            'description': 'Test',
            'values_with_schedules': [
                {
                    'money_value': {
                        'menu_value': {
                            'value_type': 'absolute',
                            'value': '1.0',
                        },
                    },
                    'schedule': {
                        'timezone': 'LOCAL',
                        'intervals': [
                            {'exclude': False, 'day': [1, 2, 3, 4, 5, 6, 7]},
                        ],
                    },
                },
            ],
        },
    },
}


@pytest.mark.servicetest
@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
@pytest.mark.now('2019-01-01T10:00:00+0000')
async def test_save_update_draft_info(taxi_grocery_discounts):
    headers = copy.deepcopy(common.DEFAULT_DISCOUNTS_HEADERS)
    headers['X-YaTaxi-Draft-Id'] = 'draft_id_test_1'

    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/add-rules', ADD_RULES_QUERY, headers=headers,
    )
    assert response.status_code == 200

    request = {
        'hierarchy_name': 'menu_discounts',
        'conditions': [
            {'condition_name': 'country', 'values': ['russia']},
            {'condition_name': 'city', 'values': []},
            {'condition_name': 'depot', 'values': []},
            {'condition_name': 'group', 'values': ['food']},
            {'condition_name': 'product', 'values': []},
        ],
    }

    response = await taxi_grocery_discounts.post(
        '/v3/admin/match-discounts/search-rules',
        request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    rules = response_json['discount_data']
    item = rules['discounts'][0]
    assert item['meta_info'] == {
        'create_draft_id': 'draft_id_test_1',
        'create_author': 'user',
    }

    update_time_request = {
        'hierarchy_name': 'menu_discounts',
        'conditions': [
            {'condition_name': 'experiment', 'values': ['testExp1']},
            {'condition_name': 'city', 'values': 'Any', 'exclusions': ['spb']},
            {'condition_name': 'country', 'values': ['russia']},
            {'condition_name': 'depot', 'values': 'Other'},
            {'condition_name': 'group', 'values': ['food']},
            {'condition_name': 'product', 'values': 'Any'},
            {
                'condition_name': 'active_period',
                'values': [
                    {
                        'start': '2020-01-01T10:00:00+0000',
                        'end': '2020-02-10T18:00:00+0000',
                    },
                ],
            },
        ],
        'new_end_time': '2020-01-01T18:00:00',
    }
    headers['X-YaTaxi-Draft-Id'] = 'draft_id_test_2'
    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/change-end-rules-time/check',
        update_time_request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    update_time_request['revisions'] = response.json()['data']['revisions']
    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/change-end-rules-time',
        update_time_request,
        headers=headers,
    )
    assert response.status_code == 200

    response = await taxi_grocery_discounts.post(
        '/v3/admin/match-discounts/search-rules',
        request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    rules = response_json['discount_data']
    item = rules['discounts'][0]
    assert item['meta_info'] == {
        'create_draft_id': 'draft_id_test_1',
        'create_author': 'user',
        'end_time_draft_id': 'draft_id_test_2',
    }


@pytest.mark.parametrize(
    'rules, hierarchy_name, expected_error',
    (
        (
            [
                {'condition_name': 'country', 'values': [1]},
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-02-01T10:00:00+0000',
                            'end': '2020-01-10T18:00:00+0000',
                        },
                    ],
                },
            ],
            'cart_discounts',
            {
                'code': 'Validation error',
                'message': (
                    'Exception in AnyOtherConditionsVectorFromGenerated '
                    'for \'country\' : '
                    'Wrong type!'
                ),
            },
        ),
        (
            [
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-02-01T10:00:00+0000',
                            'end': '2020-01-10T18:00:00+0000',
                        },
                    ],
                },
            ],
            'cart_discounts',
            {
                'code': 'Validation error',
                'message': (
                    'Exception in AnyOtherConditionsVectorFromGenerated for '
                    '\'active_period\' : begin more than end in TimeRange'
                ),
            },
        ),
        (
            [
                {'condition_name': 'city', 'values': ['213']},
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-01T02:00:00+0000',
                            'end': '2020-01-10T18:00:00+0000',
                        },
                    ],
                },
            ],
            'cart_discounts',
            {
                'code': 'Validation error',
                'message': (
                    common.TIME_IN_THE_PAST_ERROR.format(
                        '213',
                        300,
                        '2020-01-01T08:05:00+0000',
                        '2020-01-01T02:00:00+0000',
                    )
                ),
            },
        ),
        (
            [
                {'condition_name': 'city', 'values': 'Any'},
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-01T08:00:00+0000',
                            'end': '2020-01-10T18:00:00+0000',
                        },
                    ],
                },
            ],
            'cart_discounts',
            {
                'code': 'Validation error',
                'message': (
                    common.TIME_IN_THE_PAST_ERROR.format(
                        'Any/Other',
                        43200,
                        '2020-01-01T17:00:00+0000',
                        '2020-01-01T08:00:00+0000',
                    )
                ),
            },
        ),
        (
            [
                {'condition_name': 'city', 'values': ['2', '47']},
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-01T02:00:00+0000',
                            'end': '2020-01-10T18:00:00+0000',
                        },
                    ],
                },
            ],
            'cart_discounts',
            {
                'code': 'Validation error',
                'message': (
                    common.TIME_IN_THE_PAST_ERROR.format(
                        '2',
                        300,
                        '2020-01-01T08:05:00+0000',
                        '2020-01-01T02:00:00+0000',
                    )
                ),
            },
        ),
        (
            [
                {
                    'condition_name': 'product_set',
                    'values': [['duplicated'], ['duplicated']],
                },
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-02T10:00:00+0000',
                            'end': '2020-02-10T18:00:00+0000',
                        },
                    ],
                },
            ],
            'cart_discounts',
            {
                'code': 'Validation error',
                'message': 'Some conditions are duplicated in product_set',
            },
        ),
        (
            [
                {
                    'condition_name': 'city',
                    'values': 'Any',
                    'exclusions': ['moscow', 'moscow'],
                },
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-02T10:00:00+0000',
                            'end': '2020-02-10T18:00:00+0000',
                        },
                    ],
                },
            ],
            'cart_discounts',
            {
                'code': 'Validation error',
                'message': 'Some exclusions are duplicated in city',
            },
        ),
    ),
)
@pytest.mark.now('2020-01-01T05:00:00+0000')
@pytest.mark.config(GROCERY_DISCOUNTS_MINIMUM_TIME_TO_VALIDATE=43200)
@pytest.mark.parametrize(
    'url',
    [
        'v3/admin/match-discounts/add-rules',
        'v3/admin/match-discounts/add-rules/check',
    ],
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
async def test_validation_rules_in_save_update(
        taxi_grocery_discounts, rules, expected_error, url, hierarchy_name,
):
    if hierarchy_name == 'cart_discounts':
        value_name = 'set_value'
    else:
        value_name = 'menu_value'

    body = {
        'rules': rules,
        'update_existing_discounts': True,
        'revisions': [],
        'data': {
            'hierarchy_name': hierarchy_name,
            'discount': {
                'description': '1',
                'active_with_surge': False,
                'values_with_schedules': [
                    {
                        'money_value': {
                            value_name: {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'schedule': {
                            'timezone': 'LOCAL',
                            'intervals': [
                                {
                                    'exclude': False,
                                    'day': [1, 2, 3, 4, 5, 6, 7],
                                },
                            ],
                        },
                    },
                ],
            },
        },
    }
    headers = copy.deepcopy(common.DEFAULT_DISCOUNTS_HEADERS)
    headers['X-YaTaxi-Draft-Id'] = 'draft_id_test_1'

    response = await taxi_grocery_discounts.post(url, body, headers=headers)

    assert response.status_code == 400
    assert response.json() == expected_error
