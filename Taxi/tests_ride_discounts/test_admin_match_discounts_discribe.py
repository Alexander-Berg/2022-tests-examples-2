import uuid

import pytest

from tests_ride_discounts import common


@pytest.mark.parametrize(
    'hierarchies_version, existing_discounts_rules, common_conditions, '
    'select_params, expected_status, expected_data',
    (
        pytest.param(
            1,
            [
                [
                    {'condition_name': 'tariff', 'values': ['econom']},
                    {'condition_name': 'payment_method', 'values': ['card']},
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'is_prioritized': False,
                                'name': 'moscow',
                                'type': 'tariff_zone',
                            },
                        ],
                    },
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'end': '2021-07-08T15:00:00+00:00',
                                'is_end_utc': True,
                                'is_start_utc': True,
                                'start': '2021-06-25T18:00:00+00:00',
                            },
                        ],
                    },
                ],
                [
                    {'condition_name': 'tariff', 'values': ['econom']},
                    {'condition_name': 'tag', 'values': ['user_tag']},
                    {
                        'condition_name': 'surge_range',
                        'values': [{'start': '0.0', 'end': '1.2'}],
                    },
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'is_prioritized': False,
                                'name': 'moscow',
                                'type': 'tariff_zone',
                            },
                        ],
                    },
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'end': '2021-07-08T15:00:00+00:00',
                                'is_end_utc': True,
                                'is_start_utc': True,
                                'start': '2021-06-25T18:00:00+00:00',
                            },
                        ],
                    },
                ],
                [
                    {'condition_name': 'tariff', 'values': ['econom']},
                    {
                        'condition_name': 'application_brand',
                        'values': ['yataxi'],
                    },
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'is_prioritized': False,
                                'name': 'moscow',
                                'type': 'tariff_zone',
                            },
                        ],
                    },
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'end': '2021-07-08T15:00:00+00:00',
                                'is_end_utc': True,
                                'is_start_utc': True,
                                'start': '2021-06-25T18:00:00+00:00',
                            },
                        ],
                    },
                ],
                [
                    {'condition_name': 'tariff', 'values': ['econom']},
                    {
                        'condition_name': 'application_brand',
                        'values': ['yataxi'],
                    },
                    {
                        'condition_name': 'surge_range',
                        'values': [{'start': '1.5', 'end': '1.8'}],
                    },
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'is_prioritized': False,
                                'name': 'moscow',
                                'type': 'tariff_zone',
                            },
                        ],
                    },
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'end': '2021-07-08T15:00:00+00:00',
                                'is_end_utc': True,
                                'is_start_utc': True,
                                'start': '2021-06-25T18:00:00+00:00',
                            },
                        ],
                    },
                ],
            ],
            [
                {'condition_name': 'application_brand', 'values': ['yataxi']},
                {
                    'condition_name': 'zone',
                    'values': [
                        {
                            'is_prioritized': False,
                            'name': 'moscow',
                            'type': 'tariff_zone',
                        },
                    ],
                },
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'end': '2021-07-01T19:00:00+00:00',
                            'is_end_utc': True,
                            'is_start_utc': True,
                            'start': '2021-07-01T18:00:00+00:00',
                        },
                    ],
                },
            ],
            {
                'request_time': '2021-07-01T18:01:00+00:00',
                'timezone': 'Europe/Moscow',
                'client_supports_cashback': True,
            },
            200,
            {
                'items': [
                    {
                        'discount_id': '123',
                        'discount_name': '1',
                        'is_given': False,
                        'message': 'Condition payment_method does not match',
                    },
                    {
                        'discount_id': '124',
                        'discount_name': '1',
                        'is_given': False,
                        'message': 'Condition tag does not match',
                    },
                    {
                        'discount_id': '125',
                        'discount_name': '1',
                        'is_given': True,
                    },
                    {
                        'discount_id': '126',
                        'discount_name': '1',
                        'is_given': False,
                        'message': 'Condition surge_range does not match',
                    },
                ],
            },
            id='ok',
        ),
        pytest.param(
            1,
            [
                [
                    {'condition_name': 'tariff', 'values': 'Any'},
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'is_prioritized': False,
                                'name': 'moscow',
                                'type': 'tariff_zone',
                            },
                        ],
                    },
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'end': '2021-07-08T15:00:00+00:00',
                                'is_end_utc': True,
                                'is_start_utc': True,
                                'start': '2021-06-25T18:00:00+00:00',
                            },
                        ],
                    },
                ],
            ],
            [
                {
                    'condition_name': 'zone',
                    'values': [
                        {
                            'is_prioritized': False,
                            'name': 'moscow',
                            'type': 'tariff_zone',
                        },
                    ],
                },
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'end': '2021-07-01T19:00:00+00:00',
                            'is_end_utc': True,
                            'is_start_utc': True,
                            'start': '2021-07-01T18:00:00+00:00',
                        },
                    ],
                },
            ],
            {
                'request_time': '2021-07-01T18:01:00+00:00',
                'timezone': 'Europe/Moscow',
                'client_supports_cashback': True,
            },
            200,
            {
                'items': [
                    {
                        'discount_id': '123',
                        'discount_name': '1',
                        'is_given': True,
                    },
                ],
            },
            id='tariff_equal_any',
        ),
        pytest.param(
            1,
            [
                [
                    {'condition_name': 'tariff', 'values': 'Any'},
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'is_prioritized': False,
                                'name': 'moscow',
                                'type': 'tariff_zone',
                            },
                        ],
                    },
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'end': '2021-07-08T15:00:00+00:00',
                                'is_end_utc': True,
                                'is_start_utc': True,
                                'start': '2021-06-25T18:00:00+00:00',
                            },
                        ],
                    },
                ],
            ],
            [
                {
                    'condition_name': 'zone',
                    'values': [
                        {
                            'is_prioritized': False,
                            'name': 'moscow',
                            'type': 'tariff_zone',
                        },
                    ],
                },
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'end': '2021-07-01T19:00:00+00:00',
                            'is_end_utc': True,
                            'is_start_utc': True,
                            'start': '2021-07-01T18:00:00+00:00',
                        },
                    ],
                },
            ],
            {
                'request_time': '2021-07-01T18:01:00+00:00',
                'timezone': 'Europe/Moscow',
                'client_supports_cashback': True,
            },
            200,
            {
                'items': [
                    {
                        'discount_id': '123',
                        'discount_name': '1',
                        'is_given': True,
                    },
                ],
            },
            id='tariff_equal_any',
        ),
        pytest.param(
            1,
            [
                [
                    {'condition_name': 'tariff', 'values': 'Any'},
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'is_prioritized': False,
                                'name': 'moscow',
                                'type': 'tariff_zone',
                            },
                        ],
                    },
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'end': '2021-07-08T15:00:00+00:00',
                                'is_end_utc': True,
                                'is_start_utc': True,
                                'start': '2021-06-25T18:00:00+00:00',
                            },
                        ],
                    },
                ],
            ],
            [
                {
                    'condition_name': 'zone',
                    'values': [
                        {
                            'is_prioritized': False,
                            'name': 'moscow',
                            'type': 'tariff_zone',
                        },
                    ],
                },
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'end': '2021-07-01T19:00:00+00:00',
                            'is_end_utc': True,
                            'is_start_utc': True,
                            'start': '2021-07-01T18:00:00+00:00',
                        },
                    ],
                },
            ],
            {
                'request_time': '2021-07-01T18:01:00+00:00',
                'timezone': 'Europe/Moscow',
                'client_supports_cashback': True,
                'need_return_discounts': False,
            },
            200,
            {
                'items': [
                    {
                        'discount_id': '123',
                        'discount_name': '1',
                        'is_given': False,
                        'message': 'Returning discounts disabled by config',
                    },
                ],
            },
            id='not_need_return_discounts',
        ),
        pytest.param(
            1,
            [
                [
                    {
                        'condition_name': 'tariff',
                        'values': 'Other',
                        'exclusions': ['econom'],
                    },
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'is_prioritized': False,
                                'name': 'moscow',
                                'type': 'tariff_zone',
                            },
                        ],
                    },
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'end': '2021-07-08T15:00:00+00:00',
                                'is_end_utc': True,
                                'is_start_utc': True,
                                'start': '2021-06-25T18:00:00+00:00',
                            },
                        ],
                    },
                ],
            ],
            [
                {
                    'condition_name': 'zone',
                    'values': [
                        {
                            'is_prioritized': False,
                            'name': 'moscow',
                            'type': 'tariff_zone',
                        },
                    ],
                },
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'end': '2021-07-01T19:00:00+00:00',
                            'is_end_utc': True,
                            'is_start_utc': True,
                            'start': '2021-07-01T18:00:00+00:00',
                        },
                    ],
                },
            ],
            {
                'request_time': '2021-07-01T18:01:00+00:00',
                'timezone': 'Europe/Moscow',
                'client_supports_cashback': True,
            },
            200,
            {
                'items': [
                    {
                        'discount_id': '123',
                        'discount_name': '1',
                        'is_given': False,
                        'message': 'Condition tariff does not match',
                    },
                ],
            },
            id='tariff_equal_other_and_has_exclusions',
        ),
        pytest.param(
            1,
            [
                [
                    {'condition_name': 'tariff', 'values': ['econom']},
                    {
                        'condition_name': 'application_brand',
                        'values': ['yataxi'],
                    },
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'is_prioritized': False,
                                'name': 'moscow',
                                'type': 'tariff_zone',
                            },
                        ],
                    },
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'end': '2021-07-08T15:00:00+00:00',
                                'is_end_utc': True,
                                'is_start_utc': True,
                                'start': '2021-06-25T18:00:00+00:00',
                            },
                        ],
                    },
                ],
            ],
            [
                {'condition_name': 'application_brand', 'values': ['yataxi']},
                {
                    'condition_name': 'zone',
                    'values': [
                        {
                            'is_prioritized': False,
                            'name': 'moscow',
                            'type': 'tariff_zone',
                        },
                    ],
                },
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'end': '2021-07-01T19:00:00+00:00',
                            'is_end_utc': True,
                            'is_start_utc': True,
                            'start': '2021-07-01T18:00:00+00:00',
                        },
                    ],
                },
            ],
            {
                'request_time': '2021-07-01T18:01:00+00:00',
                'timezone': 'Europe/Moscow',
                'client_supports_cashback': False,
            },
            200,
            {
                'items': [
                    {
                        'discount_id': '123',
                        'discount_name': '1',
                        'is_given': False,
                        'message': 'Client does not support cashback',
                    },
                ],
            },
            id='does_not_support_cashback',
        ),
        pytest.param(
            2,
            [],
            [],
            None,
            400,
            {
                'code': 'Validation error',
                'message': 'Hierarchies with version=2 does not found',
            },
            id='hierarchies_version_not_found',
        ),
        pytest.param(
            1,
            [],
            [
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'end': '2021-07-08T15:00:00+00:00',
                            'is_end_utc': True,
                            'is_start_utc': True,
                            'start': '2021-06-25T18:00:00+00:00',
                        },
                    ],
                },
                {
                    'condition_name': 'zone',
                    'values': [
                        {
                            'is_prioritized': False,
                            'name': 'moscow',
                            'type': 'tariff_zone',
                        },
                    ],
                },
            ],
            {},
            400,
            {
                'code': 'Validation error',
                'message': (common.StartsWith('Invalid select_params={}.')),
            },
            id='invalid_select_params',
        ),
        pytest.param(
            1,
            [],
            [],
            None,
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Conditions does not have '
                    'condition with name=active_period'
                ),
            },
            id='invalid_conditions',
        ),
    ),
)
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.usefixtures('reset_data_id')
async def test_admin_match_discounts_describe(
        client,
        add_discount,
        hierarchies_version,
        existing_discounts_rules,
        common_conditions,
        select_params,
        expected_status: int,
        expected_data: dict,
):
    for existing_discounts_rule in existing_discounts_rules:
        await add_discount(
            'full_cashback_discounts', existing_discounts_rule, uuid.uuid4(),
        )

    request = {
        'tariff': 'econom',
        'hierarchies_version': hierarchies_version,
        'common_conditions': common_conditions,
        'subqueries': [
            [
                {'condition_name': 'tariff', 'values': ['econom']},
                {
                    'condition_name': 'surge_range',
                    'values': [{'end': '1.110000', 'start': '1.100000'}],
                },
            ],
        ],
        'select_params': select_params,
    }
    response = await client.post(
        'v1/admin/match-discounts/describe',
        headers=common.get_headers(),
        json=request,
    )
    assert response.status == expected_status
    data = response.json()
    data.get('items', []).sort(key=lambda x: x['discount_id'])
    assert data == expected_data
