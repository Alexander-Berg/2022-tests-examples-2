import copy

import pytest

from tests_grocery_discounts import common


def _get_add_rule_body():
    return {
        'rules': [
            {'condition_name': 'country', 'values': 'Any'},
            {'condition_name': 'city', 'values': 'Any'},
            {'condition_name': 'depot', 'values': 'Any'},
            {'condition_name': 'experiment', 'values': 'Any'},
            {
                'condition_name': 'product_set',
                'values': [['product_id_1', 'product_id_3']],
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
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
        },
    }


@pytest.mark.parametrize(
    'products, show_path, expected_suggestions',
    (
        pytest.param(
            ['product_id_1', 'unknown'],
            False,
            {
                'result': {
                    'hierarchy_name': 'cart_discounts',
                    'suggestions': [
                        {
                            'discount': {
                                'discount': {
                                    'active_with_surge': False,
                                    'money_value': {
                                        'set_value': {
                                            'value': '10.0',
                                            'value_type': 'fraction',
                                        },
                                    },
                                    'product_set': [
                                        'product_id_1',
                                        'product_id_3',
                                    ],
                                },
                            },
                            'missing_products': [{'name': 'product_id_3'}],
                        },
                    ],
                },
            },
            id='without_show_path',
        ),
        pytest.param(
            ['product_id_1', 'unknown'],
            True,
            {
                'result': {
                    'hierarchy_name': 'cart_discounts',
                    'suggestions': [
                        {
                            'discount': {
                                'discount': {
                                    'active_with_surge': False,
                                    'money_value': {
                                        'set_value': {
                                            'value': '10.0',
                                            'value_type': 'fraction',
                                        },
                                    },
                                    'product_set': [
                                        'product_id_1',
                                        'product_id_3',
                                    ],
                                },
                                'match_path': [
                                    {
                                        'condition_name': 'class',
                                        'value': 'No class',
                                    },
                                    {
                                        'condition_name': 'experiment',
                                        'value_type': 'Any',
                                    },
                                    {
                                        'condition_name': 'tag',
                                        'value_type': 'Other',
                                    },
                                    {
                                        'condition_name': 'has_yaplus',
                                        'value_type': 'Other',
                                    },
                                    {
                                        'condition_name': 'active_with_surge',
                                        'value_type': 'Other',
                                    },
                                    {
                                        'condition_name': 'application_name',
                                        'value_type': 'Other',
                                    },
                                    {
                                        'condition_name': 'country',
                                        'value_type': 'Any',
                                    },
                                    {
                                        'condition_name': 'city',
                                        'value_type': 'Any',
                                    },
                                    {
                                        'condition_name': 'depot',
                                        'value_type': 'Any',
                                    },
                                    {
                                        'condition_name': 'product_set',
                                        'value': [
                                            'product_id_1',
                                            'product_id_3',
                                        ],
                                    },
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
                                            'start': (
                                                '2020-01-01T10:00:00+00:00'
                                            ),
                                        },
                                    },
                                ],
                            },
                            'missing_products': [{'name': 'product_id_3'}],
                        },
                    ],
                },
            },
            id='with_show_path',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T10:00:00+0000')
async def test_suggest_cart_discounts(
        taxi_grocery_discounts, products, show_path, expected_suggestions,
):
    body = _get_add_rule_body()

    headers = copy.deepcopy(common.DEFAULT_DISCOUNTS_HEADERS)
    headers['X-YaTaxi-Draft-Id'] = 'draft_id_test_save_cart_discounts'

    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/add-rules', body, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {}
    await taxi_grocery_discounts.invalidate_caches()

    request = {
        'show_path': show_path,
        'hierarchy_name': 'cart_discounts',
        'request_time': '2020-01-05T10:00:00+0000',
        'request_timezone': 'UTC',
        'conditions': [
            {'condition_name': 'country', 'values': ['russia']},
            {'condition_name': 'city', 'values': ['moscow']},
            {'condition_name': 'depot', 'values': ['mega']},
            {'condition_name': 'experiment', 'values': ['exp']},
            {'condition_name': 'product', 'values': products},
        ],
    }

    response = await taxi_grocery_discounts.post(
        'v3/suggest/', request, headers=common.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    content = response.json()
    for suggestion in content['result']['suggestions']:
        suggestion['discount'].pop('revision')
        suggestion['discount']['discount'].pop('discount_id')
    assert content == expected_suggestions
