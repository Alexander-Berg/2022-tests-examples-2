# encoding=utf-8
import json

import pytest


@pytest.mark.parametrize(
    'request_json,expected_response',
    [
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {'id': ['driver1']},
                    },
                },
                'limit': 1,
                'fields': {
                    'driver_profile': [
                        'id',
                        'is_removed_by_request',
                        'is_readonly',
                        'last_name',
                    ],
                    'park': ['id'],
                    'account': ['balance'],
                    'current_status': ['status'],
                    'aggregate': {
                        'account': [
                            'positive_balance_sum',
                            'negative_balance_sum',
                            'balance_limit_sum',
                        ],
                    },
                },
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [
                    {
                        'driver_profile': {
                            'id': 'driver1',
                            'is_removed_by_request': True,
                            'is_readonly': True,
                        },
                        'accounts': [],
                        'current_status': {},
                    },
                ],
                'parks': [{'id': 'park1'}],
                'aggregate': {
                    'account': {
                        'positive_balance_sum': '0.0000',
                        'negative_balance_sum': '0.0000',
                        'balance_limit_sum': '0.0000',
                    },
                },
                'limit': 1,
                'offset': 0,
                'total': 1,
            },
            id='hide fields',
        ),
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {'id': ['driver1']},
                    },
                },
                'limit': 1,
                'fields': {
                    'driver_profile': [
                        'id',
                        'is_removed_by_request',
                        'is_readonly',
                        'last_name',
                    ],
                    'park': ['id'],
                    'account': ['balance'],
                    'current_status': ['status'],
                },
            },
            {
                'driver_profiles': [
                    {
                        'driver_profile': {
                            'id': 'driver1',
                            'is_removed_by_request': True,
                            'last_name': 'Petrov',
                        },
                        'accounts': [{'balance': '99.0000', 'id': 'driver1'}],
                        'current_status': {'status': 'busy'},
                    },
                ],
                'parks': [{'id': 'park1'}],
                'limit': 1,
                'offset': 0,
                'total': 1,
            },
            id='dont hide fields by default',
        ),
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {'id': ['driver2']},
                        'account': {
                            'last_transaction_date': {
                                'from': '2000-01-01T10:00:00.00000Z',
                            },
                        },
                    },
                },
                'limit': 1,
                'fields': {'driver_profile': ['id']},
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [{'driver_profile': {'id': 'driver2'}}],
                'parks': [{'id': 'park1'}],
                'limit': 1,
                'offset': 0,
                'total': 1,
            },
            id='check for normal driver - remove driver from search if '
            'last_transaction_date filter used',
        ),
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {'id': ['driver1']},
                        'account': {
                            'last_transaction_date': {
                                'from': '2000-01-01T10:00:00.00000Z',
                            },
                        },
                    },
                },
                'limit': 1,
                'fields': {'driver_profile': ['id']},
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [],
                'parks': [{'id': 'park1'}],
                'limit': 1,
                'offset': 0,
                'total': 0,
            },
            id='remove driver from search if '
            'last_transaction_date filter used',
        ),
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {'id': ['driver2']},
                        'current_status': {'status': ['busy']},
                    },
                },
                'limit': 1,
                'fields': {'driver_profile': ['id']},
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [{'driver_profile': {'id': 'driver2'}}],
                'parks': [{'id': 'park1'}],
                'limit': 1,
                'offset': 0,
                'total': 1,
            },
            id='check for normal driver - remove driver from '
            'search if current_status filter used',
        ),
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {'id': ['driver1']},
                        'current_status': {'status': ['busy']},
                    },
                },
                'limit': 1,
                'fields': {'driver_profile': ['id']},
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [],
                'parks': [{'id': 'park1'}],
                'limit': 1,
                'offset': 0,
                'total': 0,
            },
            id='remove driver from search if current_status filter used',
        ),
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {'id': ['driver2']},
                    },
                    'text': 'Petrov',
                },
                'limit': 1,
                'fields': {'driver_profile': ['id']},
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [{'driver_profile': {'id': 'driver2'}}],
                'parks': [{'id': 'park1'}],
                'limit': 1,
                'offset': 0,
                'total': 1,
            },
            id='check for normal driver - remove driver from '
            'search if text filter used',
        ),
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {'id': ['driver1']},
                    },
                    'text': 'Petrov',
                },
                'limit': 1,
                'fields': {'driver_profile': ['id']},
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [],
                'parks': [{'id': 'park1'}],
                'limit': 1,
                'offset': 0,
                'total': 0,
            },
            id='remove driver from search if text filter used',
        ),
        pytest.param(
            {
                'query': {'park': {'id': 'park1'}},
                'limit': 2,
                'fields': {'driver_profile': ['id']},
                'sort_order': [
                    {'direction': 'asc', 'field': 'account.current.balance'},
                ],
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [
                    {'driver_profile': {'id': 'driver2'}},
                    {'driver_profile': {'id': 'driver1'}},
                ],
                'parks': [{'id': 'park1'}],
                'limit': 2,
                'offset': 0,
                'total': 2,
            },
            id='sort_order deleted go at the end',
        ),
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {
                            'id': ['driver2'],
                            'work_status': ['fired'],
                        },
                    },
                },
                'limit': 1,
                'fields': {'driver_profile': ['id']},
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [{'driver_profile': {'id': 'driver2'}}],
                'parks': [{'id': 'park1'}],
                'limit': 1,
                'offset': 0,
                'total': 1,
            },
            id='check for normal driver - remove driver from '
            'search if work_status filter used',
        ),
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {
                            'id': ['driver1'],
                            'work_status': ['fired'],
                        },
                    },
                },
                'limit': 1,
                'fields': {'driver_profile': ['id']},
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [],
                'parks': [{'id': 'park1'}],
                'limit': 1,
                'offset': 0,
                'total': 0,
            },
            id='remove driver from search if work_status filter used',
        ),
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {
                            'id': ['driver2'],
                            'work_rule_id': ['rule_one'],
                        },
                    },
                },
                'limit': 1,
                'fields': {'driver_profile': ['id']},
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [{'driver_profile': {'id': 'driver2'}}],
                'parks': [{'id': 'park1'}],
                'limit': 1,
                'offset': 0,
                'total': 1,
            },
            id='check for normal driver - remove driver from search '
            'if work_rule_id filter used',
        ),
        pytest.param(
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {
                            'id': ['driver1'],
                            'work_rule_id': ['rule_one'],
                        },
                    },
                },
                'limit': 1,
                'fields': {'driver_profile': ['id']},
                'removed_drivers_mode': 'hide_all_fields',
            },
            {
                'driver_profiles': [],
                'parks': [{'id': 'park1'}],
                'limit': 1,
                'offset': 0,
                'total': 0,
            },
            id='remove driver from search if work_rule_id filter used',
        ),
    ],
)
@pytest.mark.redis_store(
    ['hset', 'park1:STATUS_DRIVERS', 'driver1', 1],
    ['hset', 'park1:STATUS_DRIVERS', 'driver2', 1],
)
@pytest.mark.parametrize('use_personal_caches', [True, False])
def test_ok(
        taxi_parks,
        mockserver,
        request_json,
        expected_response,
        use_personal_caches,
        config,
):
    config.set_values(dict(PARKS_USE_PERSONAL_CACHES=use_personal_caches))

    @mockserver.json_handler('/personal_caches/v1/parks/drivers-lookup')
    def mock_personal_caches(request):
        input_json = json.loads(request.get_data())
        if input_json['park_id'] == 'park1' and input_json['text'] == 'Petrov':
            return {
                'driver_profile_items': [
                    {'driver_id': 'driver1', 'rank': 7},
                    {'driver_id': 'driver2', 'rank': 7},
                ],
                'filter_status': 'filled',
            }

        assert False  # should implement custom mock

    response = taxi_parks.post(
        '/driver-profiles/list', data=json.dumps(request_json),
    )

    assert response.status_code == 200
    assert response.json() == expected_response
