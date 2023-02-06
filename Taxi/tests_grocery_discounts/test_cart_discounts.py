import copy
import datetime

import pytest

from tests_grocery_discounts import common

DEFAULT_SCHEDULE = {
    'timezone': 'LOCAL',
    'intervals': [{'exclude': False, 'day': [1, 2, 3, 4, 5, 6, 7]}],
}


def _get_add_rule_body() -> dict:
    return {
        'rules': [
            {'condition_name': 'country', 'values': 'Any'},
            {'condition_name': 'city', 'values': 'Any'},
            {'condition_name': 'depot', 'values': 'Any'},
            {'condition_name': 'experiment', 'values': 'Any'},
            {
                'condition_name': 'product_set',
                'values': [
                    ['product_id_1', 'product_id_2'],
                    ['product_id_1', 'product_id_3'],
                ],
            },
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
            'hierarchy_name': 'cart_discounts',
            'discount': {
                'description': '1',
                'active_with_surge': False,
                'values_with_schedules': [
                    {
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
        },
    }


@pytest.mark.parametrize(
    'products, expected_discounts, cache_update_time',
    (
        (
            ['product_id_1', 'product_id_2', 'unknown'],
            [
                {
                    'discount': {
                        'active_with_surge': False,
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'product_set': ['product_id_1', 'product_id_2'],
                    },
                    'create_draft_id': 'draft_id_test_save_cart_discounts',
                },
            ],
            datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        ),
        (
            ['product_id_1', 'unknown'],
            [],
            datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        ),
        (
            ['product_id_1', 'product_id_2', 'product_id_3'],
            [
                {
                    'discount': {
                        'active_with_surge': False,
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'product_set': ['product_id_1', 'product_id_2'],
                    },
                    'create_draft_id': 'draft_id_test_save_cart_discounts',
                },
                {
                    'discount': {
                        'active_with_surge': False,
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'product_set': ['product_id_1', 'product_id_3'],
                    },
                    'create_draft_id': 'draft_id_test_save_cart_discounts',
                },
            ],
            datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        ),
        (
            ['product_id_1', 'product_id_2', 'product_id_3'],
            [
                {
                    'discount': {
                        'active_with_surge': False,
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'product_set': ['product_id_1', 'product_id_2'],
                    },
                    'create_draft_id': 'draft_id_test_save_cart_discounts',
                },
                {
                    'discount': {
                        'active_with_surge': False,
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'product_set': ['product_id_1', 'product_id_3'],
                    },
                    'create_draft_id': 'draft_id_test_save_cart_discounts',
                },
            ],
            datetime.datetime(2019, 12, 31, 23, tzinfo=datetime.timezone.utc),
        ),
        (
            ['product_id_1', 'product_id_2', 'product_id_3'],
            [],
            datetime.datetime(2019, 12, 31, 21, tzinfo=datetime.timezone.utc),
        ),
        (
            ['product_id_1', 'product_id_2', 'product_id_3'],
            [
                {
                    'discount': {
                        'active_with_surge': False,
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'product_set': ['product_id_1', 'product_id_2'],
                    },
                    'create_draft_id': 'draft_id_test_save_cart_discounts',
                },
                {
                    'discount': {
                        'active_with_surge': False,
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'product_set': ['product_id_1', 'product_id_3'],
                    },
                    'create_draft_id': 'draft_id_test_save_cart_discounts',
                },
            ],
            datetime.datetime(2020, 2, 11, tzinfo=datetime.timezone.utc),
        ),
        (
            ['product_id_1', 'product_id_2', 'product_id_3'],
            [],
            datetime.datetime(2020, 2, 13, tzinfo=datetime.timezone.utc),
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T10:00:00+0000')
async def test_save_cart_discounts(
        taxi_grocery_discounts,
        products,
        expected_discounts,
        mocked_time,
        cache_update_time,
):
    body = _get_add_rule_body()

    headers = copy.deepcopy(common.DEFAULT_DISCOUNTS_HEADERS)
    headers['X-YaTaxi-Draft-Id'] = 'draft_id_test_save_cart_discounts'

    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/add-rules', body, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {}
    mocked_time.set(cache_update_time)
    await taxi_grocery_discounts.invalidate_caches()

    request = {
        'show_path': False,
        'request_time': '2020-01-05T10:00:00+0000',
        'hierarchy_names': ['cart_discounts'],
        'common_conditions': [
            {'condition_name': 'country', 'values': ['russia']},
            {'condition_name': 'city', 'values': ['moscow']},
            {'condition_name': 'depot', 'values': ['mega']},
            {'condition_name': 'experiment', 'values': ['exp']},
        ],
        'subqueries': [
            {
                'subquery_id': '1',
                'conditions': [
                    {'condition_name': 'product', 'values': products},
                ],
            },
        ],
    }

    response = await taxi_grocery_discounts.post(
        'v3/match-discounts/',
        request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )

    assert response.status_code == 200
    response_json = response.json()
    common.make_match_discounts_response(response_json, False)
    assert response_json == {
        'match_results': [
            {
                'results': [
                    {
                        'discounts': expected_discounts,
                        'hierarchy_name': 'cart_discounts',
                        'status': 'ok',
                    },
                ],
                'subquery_id': '1',
            },
        ],
        'restoration_info': {
            'versions': [{'name': 'rules-match-cache', 'id': 'default'}],
        },
    }


@pytest.mark.parametrize(
    'valid_application_names', ([], ['app1'], ['app1', 'app2']),
)
@pytest.mark.parametrize(
    'application_names',
    (
        'Any',
        'Other',
        ['app3'],
        ['app1'],
        ['app2'],
        ['app2'],
        ['app1', 'app2'],
        ['app2', 'app3'],
        ['app1', 'app2', 'app3'],
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T10:00:00+0000')
async def test_cart_discounts_application_name_validation(
        taxi_grocery_discounts,
        taxi_config,
        valid_application_names,
        application_names,
):
    taxi_config.set(
        GROCERY_DISCOUNTS_APPLICATION_NAME_VALIDATION={
            'enabled': True,
            'application_names': valid_application_names,
        },
    )

    body = _get_add_rule_body()
    body['rules'].append(
        {'condition_name': 'application_name', 'values': application_names},
    )

    headers = copy.deepcopy(common.DEFAULT_DISCOUNTS_HEADERS)
    headers[
        'X-YaTaxi-Draft-Id'
    ] = 'draft_id_test_cart_discounts_application_name_validation'

    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/add-rules', body, headers=headers,
    )

    if isinstance(application_names, list):
        for application_name in application_names:
            if application_name not in valid_application_names:
                assert response.status_code == 400
                assert response.json() == {
                    'code': 'Validation error',
                    'message': (
                        'Invalid application_name: ' + application_name
                    ),
                }
                return
    assert response.status_code == 200


@pytest.mark.parametrize(
    'discount, code, expected_error',
    (
        (
            {
                'description': '1',
                'active_with_surge': True,
                'values_with_schedules': [],
            },
            400,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'discount_meta': {},
                'max_set_apply_count': 0,
                'values_with_schedules': [],
            },
            400,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'discount_meta': {},
                'max_set_apply_count': -1,
                'values_with_schedules': [],
            },
            400,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'discount_meta': {},
                'max_set_apply_count': 1,
                'values_with_schedules': [
                    {'money_value': {}, 'schedule': DEFAULT_SCHEDULE},
                ],
            },
            400,
            {
                'code': 'Validation error',
                'message': 'Cart or set discount must be specified',
            },
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'discount_meta': {},
                'max_set_apply_count': 1,
                'values_with_schedules': [
                    {
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '0.00',
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'values_with_schedules': [
                    {
                        'money_value': {
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '0',
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': False,
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '0.0',
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'values_with_schedules': [{'schedule': DEFAULT_SCHEDULE}],
            },
            400,
            {
                'code': 'Validation error',
                'message': 'All schedules are empty on discount values',
            },
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'discount_meta': {},
                'max_set_apply_count': 1,
                'values_with_schedules': [
                    {
                        'money_value': {
                            'cart_value': {
                                'value': [
                                    {
                                        'from_cost': '1',
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '1.0',
                                        },
                                    },
                                ],
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'discount_meta': {},
                'max_set_apply_count': 1,
                'values_with_schedules': [
                    {
                        'money_value': {
                            'cart_value': {
                                'value': [
                                    {
                                        'from_cost': '1',
                                        'discount': {
                                            'value_type': 'absolute',
                                            'value': '1.0',
                                        },
                                    },
                                ],
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'discount_meta': {},
                'max_set_apply_count': 1,
                'values_with_schedules': [
                    {
                        'money_value': {
                            'cart_value': {
                                'maximum_discount': '10.0',
                                'value': [
                                    {
                                        'from_cost': '1',
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '1.0',
                                        },
                                    },
                                ],
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'discount_meta': {},
                'max_set_apply_count': 1,
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'cart_value': {
                                'value': [
                                    {
                                        'from_cost': '1',
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '1.0',
                                        },
                                    },
                                ],
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'discount_meta': {},
                'max_set_apply_count': 1,
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'cart_value': {
                                'value': [
                                    {
                                        'from_cost': '1',
                                        'discount': {
                                            'value_type': 'absolute',
                                            'value': '1.0',
                                        },
                                    },
                                ],
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'discount_meta': {},
                'max_set_apply_count': 1,
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'cart_value': {
                                'maximum_discount': '10.0',
                                'value': [
                                    {
                                        'from_cost': '1',
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '1.0',
                                        },
                                    },
                                ],
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': True,
                'discount_meta': {},
                'max_set_apply_count': 1,
                'values_with_schedules': [
                    {
                        'money_value': {
                            'cart_value': {
                                'maximum_discount': '10.0',
                                'value': [
                                    {
                                        'from_cost': '1',
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '1.00',
                                        },
                                    },
                                ],
                            },
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '0.0',
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': False,
                'values_with_schedules': [
                    {
                        'product_value': {
                            'value': [
                                {
                                    'step': {
                                        'from_cost': '100500.992',
                                        'discount': '11.02',
                                    },
                                    'products': [{'id': '2'}],
                                    'bundle': 2,
                                },
                            ],
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': False,
                'values_with_schedules': [
                    {
                        'product_value': {
                            'value': [
                                {
                                    'step': {
                                        'from_cost': '0',
                                        'discount': '0',
                                    },
                                    'products': [],
                                    'bundle': 2,
                                },
                            ],
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            400,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': False,
                'values_with_schedules': [
                    {
                        'product_value': {
                            'value': [
                                {
                                    'step': {
                                        'from_cost': '0',
                                        'discount': '101',
                                    },
                                    'products': [
                                        {'id': '2'},
                                        {'id': '3'},
                                        {'id': '4'},
                                    ],
                                    'bundle': 2,
                                },
                            ],
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': False,
                'values_with_schedules': [
                    {
                        'product_value': {
                            'value': [
                                {
                                    'step': {
                                        'from_cost': '0',
                                        'discount': '201',
                                    },
                                    'products': [
                                        {'id': '2'},
                                        {'id': '3'},
                                        {'id': '4'},
                                    ],
                                    'bundle': 2,
                                },
                            ],
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Product discount (201.0) value has to be between 0'
                    ' and bundle*100 (200.0)'
                ),
            },
        ),
        (
            {
                'description': '1',
                'active_with_surge': False,
                'values_with_schedules': [
                    {
                        'product_value': {
                            'value': [
                                {
                                    'step': {
                                        'from_cost': '0',
                                        'discount': '7',
                                    },
                                    'products': [{'id': '1'}],
                                    'bundle': 0,
                                },
                            ],
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            400,
            None,
        ),
        (
            {
                'description': '1',
                'active_with_surge': False,
                'values_with_schedules': [
                    {
                        'product_value': {
                            'value': [
                                {
                                    'step': {
                                        'from_cost': '0',
                                        'discount': '8',
                                    },
                                    'products': [{'id': '1'}],
                                    'bundle': 1,
                                },
                            ],
                        },
                        'cashback_value': {
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '100.0',
                            },
                        },
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '0.0',
                            },
                            'cart_value': {
                                'maximum_discount': '10.0',
                                'value': [
                                    {
                                        'from_cost': '1',
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '1.0',
                                        },
                                    },
                                ],
                            },
                        },
                        'schedule': DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T05:00:00+0000')
async def test_validation_cart_discount(
        taxi_grocery_discounts, discount, code, expected_error,
):
    body = {
        'rules': [
            {'condition_name': 'country', 'values': 'Any'},
            {'condition_name': 'city', 'values': 'Any'},
            {'condition_name': 'depot', 'values': 'Any'},
            {
                'condition_name': 'product_set',
                'values': [
                    ['product_id_1', 'product_id_2'],
                    ['product_id_1', 'product_id_3'],
                ],
            },
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
        'revisions': [],
        'update_existing_discounts': True,
        'data': {'hierarchy_name': 'cart_discounts', 'discount': discount},
    }
    headers = copy.deepcopy(common.DEFAULT_DISCOUNTS_HEADERS)
    headers['X-YaTaxi-Draft-Id'] = 'draft_id_test_1'

    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/add-rules', body, headers=headers,
    )
    assert response.status_code == code
    if expected_error:
        assert response.json() == expected_error


@pytest.mark.servicetest
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+0000')
async def test_empty_cart_discounts(taxi_grocery_discounts, load_json):
    request = load_json('request.json')
    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    common.check_discounts(response.json(), '1', 'cart_discounts', [])

    new_discount = load_json('add_discount.json')

    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/add-rules',
        new_discount,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200

    await taxi_grocery_discounts.invalidate_caches()

    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    common.make_match_discounts_response(response_json, False)
    assert response_json == load_json('response.json')


@pytest.mark.servicetest
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+0000')
async def test_cart_discounts_with_exclusions(
        taxi_grocery_discounts, load_json,
):
    request = load_json('request.json')
    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    common.check_discounts(response.json(), '1', 'cart_discounts', [])

    new_discount = load_json('add_rules_request.json')

    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/add-rules',
        new_discount,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200

    await taxi_grocery_discounts.invalidate_caches()

    response = await taxi_grocery_discounts.post(
        'v3/match-discounts',
        request,
        headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    common.make_match_discounts_response(response_json, False)
    assert response_json == load_json('response.json')
