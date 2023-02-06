# pylint: disable=too-many-lines
import copy
import typing as tp

import pytest

from tests_grocery_discounts import common


CHECK_LIST: tp.Tuple = (
    pytest.param(
        {
            'request_time': '2020-01-01T18:00:00+0000',
            'hierarchy_names': ['menu_discounts'],
            'common_conditions': [
                {'condition_name': 'experiment', 'values': ['testExp1']},
                {'condition_name': 'country', 'values': ['russia']},
                {'condition_name': 'city', 'values': ['moscow']},
                {'condition_name': 'depot', 'values': ['mega']},
            ],
            'subqueries': [
                {
                    'subquery_id': '1234',
                    'conditions': [
                        {'condition_name': 'group', 'values': ['food']},
                        {'condition_name': 'product', 'values': ['milk']},
                    ],
                },
            ],
        },
        [
            {
                'discount': {
                    'active_with_surge': True,
                    'money_value': {
                        'menu_value': {
                            'value': '1.0',
                            'value_type': 'absolute',
                        },
                    },
                },
                'create_draft_id': 'unknown',
            },
        ],
        id='find_one_rule',
    ),
    pytest.param(
        {
            'request_time': '2020-01-01T18:00:00+0000',
            'hierarchy_names': ['menu_discounts'],
            'common_conditions': [
                {'condition_name': 'experiment', 'values': ['testExp1']},
                {'condition_name': 'country', 'values': ['russia']},
                {'condition_name': 'city', 'values': ['spb']},
                {'condition_name': 'depot', 'values': ['mega']},
            ],
            'subqueries': [
                {
                    'subquery_id': '1234',
                    'conditions': [
                        {'condition_name': 'group', 'values': ['food']},
                        {'condition_name': 'product', 'values': ['milk']},
                    ],
                },
            ],
        },
        [],
        id='find nothing, excluded spb',
    ),
    pytest.param(
        {
            'request_time': '2020-01-01T10:00:00+0000',
            'hierarchy_names': ['menu_discounts'],
            'common_conditions': [
                {'condition_name': 'experiment', 'values': ['testExp1']},
                {'condition_name': 'country', 'values': ['russia']},
                {'condition_name': 'city', 'values': ['spb']},
                {'condition_name': 'depot', 'values': ['mega']},
            ],
            'subqueries': [
                {
                    'subquery_id': '1234',
                    'conditions': [
                        {'condition_name': 'group', 'values': ['food']},
                        {'condition_name': 'product', 'values': ['milk']},
                    ],
                },
            ],
        },
        [],
        id='find nothing, `request_time` out of bounds',
    ),
)


@pytest.mark.servicetest
@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
@pytest.mark.parametrize('request_body,expected_response', CHECK_LIST)
async def test_match_discounts(
        taxi_grocery_discounts, request_body, expected_response,
):
    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request_body,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    common.check_discounts(
        response.json(), '1234', 'menu_discounts', expected_response,
    )


FETCH_CHECK_LIST: tp.Tuple = (
    (
        {
            'show_path': True,
            'request_time': '2020-02-13T14:00:00+0300',
            'request_timezone': 'Europe/Moscow',
            'hierarchy_names': ['menu_discounts'],
            'depot': 'mega',
            'city': '213',
            'country': 'RUS',
            'experiments': ['testExp1'],
        },
        'check_response_for_absolute_time.json',
    ),
    (
        {
            'show_path': True,
            'request_time': '2020-02-13T14:00:00+0300',
            'request_timezone': 'Europe/Moscow',
            'hierarchy_names': ['menu_discounts'],
            'depot': 'mega',
            'city': '213',
            'country': 'RUS',
        },
        'check_empty_response.json',
    ),
    (
        {
            'show_path': True,
            'request_time': '2020-01-01T17:00:00+0000',
            'hierarchy_names': ['menu_discounts'],
            'depot': 'mega',
            'city': '213',
            'country': 'RUS',
            'experiments': ['testExp1'],
        },
        'check_response.json',
    ),
    (
        {
            'show_path': True,
            'request_time': '2020-01-01T17:00:00+0000',
            'hierarchy_names': ['menu_discounts'],
            'depot': 'not_mega',
            'city': '213',
            'country': 'RUS',
            'experiments': ['testExp1'],
        },
        'check_only_any_other_response.json',
    ),
    (
        {
            'show_path': True,
            'request_time': '2020-02-11T16:00:00+0000',
            'hierarchy_names': ['menu_discounts'],
            'depot': 'mega',
            'city': '213',
            'country': 'RUS',
            'experiments': ['testExp1'],
        },
        'check_empty_response.json',
    ),
    (
        {
            'show_path': True,
            'request_time': '2020-02-11T16:00:00+0000',
            'hierarchy_names': ['menu_discounts'],
            'depot': 'mega',
            'city': 'voronezh',
            'country': 'usa',
            'experiments': ['testExp1'],
        },
        'check_empty_response.json',
    ),
)


@pytest.mark.servicetest
@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
@pytest.mark.parametrize('request_body,expected_response', FETCH_CHECK_LIST)
async def test_fetch_discounts(
        taxi_grocery_discounts, request_body, expected_response, load_json,
):
    response = await taxi_grocery_discounts.post(
        'v3/fetch-discounts',
        request_body,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )

    assert response.status_code == 200
    expected_response = load_json(expected_response)
    assert common.remove_discount_id(
        common.remove_revision(response.json()),
    ) == common.remove_revision(expected_response)


@pytest.mark.servicetest
@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
@pytest.mark.parametrize('request_body,expected_response', CHECK_LIST)
@pytest.mark.now('2020-01-01T09:00:00+0000')
@pytest.mark.config(GROCERY_DISCOUNTS_MINIMUM_TIME_TO_VALIDATE=3600)
async def test_match_discounts_with_add_rules(
        taxi_grocery_discounts, request_body, expected_response, load_json,
):
    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request_body,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    common.check_discounts(response.json(), '1234', 'menu_discounts', [])

    new_discounts = load_json('add_discounts.json')
    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/add-rules',
        new_discounts[0],
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200

    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/add-rules',
        new_discounts[1],
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200

    await taxi_grocery_discounts.invalidate_caches()

    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request_body,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    common.check_discounts(
        response.json(), '1234', 'menu_discounts', expected_response,
    )


@pytest.mark.servicetest
@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
@pytest.mark.parametrize(
    'request_body,expected_response',
    (
        # find one rule
        (
            {
                'request_time': '2020-01-01T18:00:00+0000',
                'hierarchy_names': ['menu_discounts'],
                'common_conditions': [
                    {'condition_name': 'country', 'values': ['russia']},
                    {'condition_name': 'city', 'values': ['moscow']},
                    {'condition_name': 'depot', 'values': ['mega']},
                ],
                'subqueries': [
                    {
                        'subquery_id': '1234',
                        'conditions': [
                            {'condition_name': 'group', 'values': ['food']},
                            {'condition_name': 'product', 'values': ['milk']},
                        ],
                    },
                ],
            },
            [
                {
                    'discount': {
                        'active_with_surge': True,
                        'money_value': {
                            'menu_value': {
                                'value': '1.0',
                                'value_type': 'absolute',
                            },
                        },
                    },
                    'create_draft_id': 'unknown',
                },
            ],
        ),
    ),
)
@pytest.mark.now('2020-01-01T09:00:00+0000')
async def test_change_end_rules_time(
        taxi_grocery_discounts, request_body, expected_response,
):
    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request_body,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    common.check_discounts(
        response.json(), '1234', 'menu_discounts', expected_response,
    )

    update_time_request = {
        'hierarchy_name': 'menu_discounts',
        'conditions': [
            {'condition_name': 'city', 'values': 'Any'},
            {'condition_name': 'country', 'values': ['russia']},
            {'condition_name': 'depot', 'values': 'Other'},
            {'condition_name': 'group', 'values': ['food']},
            {'condition_name': 'product', 'values': 'Any'},
            {
                'condition_name': 'active_period',
                'values': [
                    {
                        'start': '2020-01-01T00:00:00+0000',
                        'end': '2020-12-10T00:00:00+0000',
                    },
                ],
            },
            {'condition_name': 'experiment', 'values': 'Other'},
        ],
        'new_end_time': '2020-01-01T18:00:00',
    }
    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/change-end-rules-time/check',
        update_time_request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    update_time_request['revisions'] = response.json()['data']['revisions']
    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/change-end-rules-time',
        update_time_request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200

    await taxi_grocery_discounts.invalidate_caches()

    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request_body,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    common.check_discounts(response.json(), '1234', 'menu_discounts', [])


@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
async def test_discount_classes(taxi_grocery_discounts):
    request = {
        'request_time': '2020-01-01T18:00:00+0000',
        'hierarchy_names': ['menu_discounts'],
        'common_conditions': [
            {'condition_name': 'experiment', 'values': ['testExp1']},
            {'condition_name': 'country', 'values': ['russia']},
            {'condition_name': 'city', 'values': ['moscow']},
            {'condition_name': 'depot', 'values': ['mega']},
        ],
        'subqueries': [
            {
                'subquery_id': '1234',
                'conditions': [
                    {
                        'condition_name': 'group',
                        'values': ['food', 'zzz', 'xxx'],
                    },
                    {'condition_name': 'product', 'values': ['milk']},
                ],
            },
        ],
    }
    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    rules = response_json['match_results'][0]
    assert (
        rules['results'][0]['discounts'][0]['discount']['money_value'][
            'menu_value'
        ]['value']
        == '1.0'
    )


@pytest.mark.parametrize(
    'request_experiments, experiments_orders, '
    'expected_status, expected_discount',
    (
        pytest.param(['first', 'second'], ['first', 'second'], 200, '1.0'),
        pytest.param(['first', 'second'], ['second', 'first'], 200, '2.0'),
        pytest.param(['first'], ['first', 'second'], 200, '1.0'),
        pytest.param(['first'], ['second', 'first'], 200, '1.0'),
        pytest.param([1], ['second', 'first'], 400, None),
    ),
)
@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
async def test_discount_experiments(
        request_experiments,
        experiments_orders,
        taxi_grocery_discounts,
        expected_status,
        expected_discount,
        pgsql,
):
    cursor = pgsql['grocery_discounts'].cursor()
    cursor.execute(
        """
        INSERT INTO grocery_discounts.experiments_orders
        (experiments, updated_at)
        VALUES(ARRAY[{}]::text[], '2020-01-01T18:00:00+0000');
        """.format(
            ', '.join(repr(e) for e in experiments_orders),
        ),
    )

    request = {
        'request_time': '2020-01-01T18:00:00+0000',
        'hierarchy_names': ['menu_discounts'],
        'common_conditions': [
            {'condition_name': 'experiment', 'values': request_experiments},
            {'condition_name': 'country', 'values': ['russia']},
            {'condition_name': 'city', 'values': ['moscow']},
            {'condition_name': 'depot', 'values': ['mega']},
        ],
        'subqueries': [
            {
                'subquery_id': '1234',
                'conditions': [
                    {
                        'condition_name': 'group',
                        'values': ['food', 'zzz', 'xxx'],
                    },
                    {'condition_name': 'product', 'values': ['milk']},
                ],
            },
        ],
    }
    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == expected_status
    if expected_status != 200:
        return
    response_json = response.json()
    rules = response_json['match_results'][0]
    assert (
        rules['results'][0]['discounts'][0]['discount']['money_value'][
            'menu_value'
        ]['value']
        == expected_discount
    )


@pytest.mark.config(GROCERY_DISCOUNTS_USE_NAMED_GROUPS=True)
@pytest.mark.parametrize(
    'depot, groups, expected_discount',
    [
        ('depot1', ['group3', 'group1', 'group2'], '2.0'),
        ('depot2', ['group3', 'group1', 'group2'], '3.0'),
        ('depot1', ['group1'], '1.0'),
        ('depot5', ['group1'], 'No discount'),
        ('depot100', ['group1'], 'No discount'),
        ('depot1', [], 'No discount'),
    ],
)
@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
async def test_discount_groups(
        taxi_grocery_discounts, depot, expected_discount, groups,
):
    request = {
        'request_time': '2020-01-01T18:00:00+0000',
        'hierarchy_names': ['menu_discounts'],
        'common_conditions': [
            {'condition_name': 'experiment', 'values': ['testExp1']},
            {'condition_name': 'country', 'values': ['russia']},
            {'condition_name': 'city', 'values': ['moscow']},
            {'condition_name': 'depot', 'values': [depot]},
        ],
        'subqueries': [
            {
                'subquery_id': '1234',
                'conditions': [
                    {'condition_name': 'group', 'values': groups},
                    {'condition_name': 'product', 'values': ['milk']},
                ],
            },
        ],
    }
    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    rules = response_json['match_results'][0]
    if expected_discount == 'No discount':
        assert not rules['results'][0]['discounts']
    else:
        assert (
            rules['results'][0]['discounts'][0]['discount']['money_value'][
                'menu_value'
            ]['value']
            == expected_discount
        )


@pytest.mark.servicetest
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'discount_data, expected_error',
    (
        (
            {
                'hierarchy_name': 'menu_discounts',
                'discount': {
                    'active_with_surge': True,
                    'description': 'Test',
                    'values_with_schedules': [
                        {
                            'money_value': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '-5.0',
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
            None,
        ),
        (
            {
                'hierarchy_name': 'menu_discounts',
                'discount': {
                    'active_with_surge': True,
                    'description': 'Test',
                    'values_with_schedules': [
                        {
                            'money_value': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '122.0',
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
            None,
        ),
        (
            {
                'hierarchy_name': 'menu_discounts',
                'discount': {
                    'description': '1',
                    'active_with_surge': False,
                    'values_with_schedules': [
                        {
                            'money_value': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '10.0',
                                },
                            },
                            'schedule': {
                                'timezone': 'LOCAL',
                                'intervals': [
                                    {'exclude': False, 'day': [5, 6, 7]},
                                ],
                            },
                        },
                        {
                            'money_value': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '15.0',
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
            {
                'code': 'Validation error',
                'message': 'Validating overlapping schedules failed',
            },
        ),
    ),
)
@pytest.mark.now('2020-01-01T05:00:00+0000')
async def test_validation_discount_in_save_update_draft_info(
        taxi_grocery_discounts, discount_data, expected_error,
):
    body = {
        'rules': [
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
        'data': discount_data,
        'revisions': [],
    }
    headers = copy.deepcopy(common.DEFAULT_DISCOUNTS_HEADERS)
    headers['X-YaTaxi-Draft-Id'] = 'draft_id_test_1'

    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/add-rules', body, headers=headers,
    )
    assert response.status_code == 400
    if expected_error:
        assert response.json() == expected_error
