# pylint: disable=too-many-lines
import copy
import typing as tp

import pytest

from tests_grocery_discounts import common

# ATTENTION payment_method_discounts doesn't have depot condition
# it wont hurt if you provide it, but still
CHECK_LIST: tp.Tuple = (
    # find one rule
    (
        {
            'request_time': '2020-01-01T18:00:00+0000',
            'hierarchy_names': ['payment_method_discounts'],
            'common_conditions': [
                {'condition_name': 'experiment', 'values': ['testExp1']},
                {'condition_name': 'application_name', 'values': ['android']},
                {'condition_name': 'country', 'values': ['russia']},
                {'condition_name': 'city', 'values': ['moscow']},
                {'condition_name': 'payment_method', 'values': ['GPay']},
                {'condition_name': 'card_bin', 'values': ['405060']},
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
                            'value_type': 'absolute',
                            'value': '1.0',
                        },
                        'cart_value': {
                            'discount_values': {
                                'value_type': 'table',
                                'value': [
                                    {
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '10.0',
                                        },
                                        'from_cost': '120.0',
                                    },
                                ],
                            },
                            'maximum_discount': '10000.0',
                        },
                    },
                },
                'create_draft_id': 'unknown',
            },
        ],
    ),
    # find nothing, wrong application_name
    (
        {
            'request_time': '2020-01-01T18:00:00+0000',
            'hierarchy_names': ['payment_method_discounts'],
            'common_conditions': [
                {'condition_name': 'experiment', 'values': ['testExp1']},
                {'condition_name': 'application_name', 'values': ['iphone']},
                {'condition_name': 'country', 'values': ['russia']},
                {'condition_name': 'city', 'values': ['moscow']},
                {'condition_name': 'payment_method', 'values': ['GPay']},
                {'condition_name': 'card_bin', 'values': ['405060']},
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
    ),
    # find nothing, wrong bin
    (
        {
            'request_time': '2020-01-01T18:00:00+0000',
            'hierarchy_names': ['payment_method_discounts'],
            'common_conditions': [
                {'condition_name': 'experiment', 'values': ['testExp1']},
                {'condition_name': 'application_name', 'values': ['android']},
                {'condition_name': 'country', 'values': ['russia']},
                {'condition_name': 'city', 'values': ['moscow']},
                {'condition_name': 'payment_method', 'values': ['GPay']},
                {'condition_name': 'card_bin', 'values': ['444444']},
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
    ),
    # find nothing, excluded payment_method
    (
        {
            'request_time': '2020-01-01T18:00:00+0000',
            'hierarchy_names': ['payment_method_discounts'],
            'common_conditions': [
                {'condition_name': 'experiment', 'values': ['testExp1']},
                {'condition_name': 'application_name', 'values': ['android']},
                {'condition_name': 'country', 'values': ['russia']},
                {'condition_name': 'city', 'values': ['moscow']},
                {'condition_name': 'payment_method', 'values': ['card']},
                {'condition_name': 'card_bin', 'values': ['405060']},
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
    ),
)


@pytest.mark.servicetest
@pytest.mark.now('2020-01-01T18:00:00')
@pytest.mark.pgsql(
    'grocery_discounts',
    files=['init.sql', 'fill_payment_method_discounts.sql'],
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
        response.json(), '1234', 'payment_method_discounts', expected_response,
    )


FETCH_CHECK_LIST: tp.Tuple = (
    (
        {
            'show_path': True,
            'request_time': '2020-01-01T17:00:00+0000',
            'hierarchy_names': ['payment_method_discounts'],
            'depot': 'mega',
            'country': 'russia',
            'city': 'moscow',
        },
        'check_response.json',
    ),
    (
        {
            'show_path': True,
            'request_time': '2020-02-11T16:00:00+0000',
            'hierarchy_names': ['payment_method_discounts'],
            'depot': 'mega',
            'country': 'russia',
            'city': 'moscow',
        },
        'check_empty_response.json',
    ),
)


@pytest.mark.servicetest
@pytest.mark.pgsql(
    'grocery_discounts',
    files=['init.sql', 'fill_payment_method_discounts.sql'],
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
    'grocery_discounts',
    files=['init.sql', 'fill_payment_method_discounts.sql'],
)
@pytest.mark.parametrize('request_body,expected_response', CHECK_LIST)
@pytest.mark.now('2020-01-01T09:00:00+0000')
@pytest.mark.config(
    GROCERY_DISCOUNTS_MINIMUM_TIME_TO_VALIDATE=3600,
    GROCERY_DISCOUNTS_APPLICATION_NAME_VALIDATION={
        'enabled': True,
        'application_names': ['android', 'iphone'],
    },
)
async def test_match_discounts_with_add_rules(
        taxi_grocery_discounts, request_body, expected_response, load_json,
):
    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request_body,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    common.check_discounts(
        response.json(), '1234', 'payment_method_discounts', [],
    )

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
        response.json(), '1234', 'payment_method_discounts', expected_response,
    )


@pytest.mark.servicetest
@pytest.mark.pgsql(
    'grocery_discounts',
    files=['init.sql', 'fill_payment_method_discounts.sql'],
)
@pytest.mark.now('2020-01-01T10:00:00+0000')
@pytest.mark.parametrize(
    'request_body,expected_response',
    (
        # find one rule
        (
            {
                'request_time': '2020-01-01T18:00:00+0000',
                'hierarchy_names': ['payment_method_discounts'],
                'common_conditions': [
                    {'condition_name': 'experiment', 'values': ['testExp1']},
                    {'condition_name': 'country', 'values': ['russia']},
                    {'condition_name': 'city', 'values': ['moscow']},
                    {'condition_name': 'payment_method', 'values': ['GPay']},
                    {'condition_name': 'card_bin', 'values': ['405060']},
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
                                'value_type': 'absolute',
                                'value': '1.0',
                            },
                            'cart_value': {
                                'discount_values': {
                                    'value_type': 'table',
                                    'value': [
                                        {
                                            'discount': {
                                                'value_type': 'fraction',
                                                'value': '10.0',
                                            },
                                            'from_cost': '120.0',
                                        },
                                    ],
                                },
                                'maximum_discount': '10000.0',
                            },
                        },
                    },
                    'create_draft_id': 'unknown',
                },
            ],
        ),
    ),
)
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
        response.json(), '1234', 'payment_method_discounts', expected_response,
    )

    update_time_request = {
        'hierarchy_name': 'payment_method_discounts',
        'conditions': [
            {'condition_name': 'city', 'values': 'Any'},
            {'condition_name': 'country', 'values': ['russia']},
            {
                'condition_name': 'depot',
                'values': 'Any',
            },  # just for front. Will be removed
            {'condition_name': 'payment_method', 'values': 'Other'},
            {'condition_name': 'bins', 'values': ['SuperGroup']},
            {'condition_name': 'group', 'values': ['food']},
            {'condition_name': 'product', 'values': 'Any'},
            {'condition_name': 'experiment', 'values': 'Other'},
            {
                'condition_name': 'active_period',
                'values': [
                    {
                        'start': '2020-01-01T10:00:00+0000',
                        'end': '2020-02-18T00:00:00+0000',
                    },
                ],
            },
        ],
        'new_end_time': '2020-01-01T13:00:00',
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
    common.check_discounts(
        response.json(), '1234', 'payment_method_discounts', [],
    )


@pytest.mark.servicetest
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'discount_data, expected_error',
    (
        (
            {
                'hierarchy_name': 'payment_method_discounts',
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
                'hierarchy_name': 'payment_method_discounts',
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
                'hierarchy_name': 'payment_method_discounts',
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
