import pytest

from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils


ENDPOINT = 'fleet/driver-work-rules/v1/work-rules'


@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.parametrize(
    ('park_id', 'params', 'expected_response', 'parks_service'),
    [
        (
            'extra_super_park_id',
            {'is_archived': True},
            'all_archived_work_rules.json',
            {
                'request': {
                    'ids': [
                        'work_rule_4_archived',
                        'work_rule_1_archived',
                        'work_rule_6_archived',
                    ],
                },
                'response': {
                    'work_rules': [
                        {'usage': 7, 'id': 'work_rule_4_archived'},
                        {'usage': 4, 'id': 'work_rule_1_archived'},
                        {'usage': 999, 'id': 'work_rule_6_archived'},
                    ],
                },
            },
        ),
        (
            'extra_super_park_id',
            {'is_archived': True, 'limit': 2},
            'first_2_archived_work_rules.json',
            {
                'request': {
                    'ids': ['work_rule_4_archived', 'work_rule_1_archived'],
                },
                'response': {
                    'work_rules': [{'usage': 7, 'id': 'work_rule_4_archived'}],
                },
            },
        ),
        (
            'extra_super_park_id',
            {
                'is_archived': True,
                'limit': 3,
                'cursor': (
                    'eyJsYXN0X3J1bGVfaWQiOiJ3b3JrX3J1bGVfMV9hcmNoaXZlZCJ9'
                ),
            },
            'paginated_archived_work_rules.json',
            {
                'request': {
                    'ids': ['work_rule_1_archived', 'work_rule_6_archived'],
                },
                'response': {
                    'work_rules': [
                        {'usage': 4, 'id': 'work_rule_1_archived'},
                        {'usage': 999, 'id': 'work_rule_6_archived'},
                    ],
                },
            },
        ),
        (
            'extra_super_park_id',
            {'is_archived': False},
            'all_active_work_rules.json',
            {
                'request': {
                    'ids': [
                        'work_rule_5',
                        'work_rule_2',
                        'work_rule_3_default',
                    ],
                },
                'response': {
                    'work_rules': [
                        {'usage': 2, 'id': 'work_rule_5'},
                        {'usage': 8, 'id': 'work_rule_2'},
                        {'usage': 1, 'id': 'work_rule_3_default'},
                    ],
                },
            },
        ),
        (
            'extra_super_park_id',
            {'is_archived': False, 'limit': 2},
            'first_2_active_work_rules.json',
            {
                'request': {'ids': ['work_rule_5', 'work_rule_2']},
                'response': {
                    'work_rules': [
                        {'usage': 2, 'id': 'work_rule_5'},
                        {'usage': 8, 'id': 'work_rule_2'},
                    ],
                },
            },
        ),
        (
            'extra_super_park_id',
            {
                'is_archived': False,
                'limit': 3,
                'cursor': 'eyJsYXN0X3J1bGVfaWQiOiJ3b3JrX3J1bGVfMiJ9=',
            },
            'paginated_active_work_rules.json',
            {
                'request': {'ids': ['work_rule_2', 'work_rule_3_default']},
                'response': {
                    'work_rules': [
                        {'usage': 8, 'id': 'work_rule_2'},
                        {'usage': 1, 'id': 'work_rule_3_default'},
                    ],
                },
            },
        ),
        (
            'extra_super_park_id',
            {},
            'all_work_rules.json',
            {
                'request': {
                    'ids': [
                        'work_rule_4_archived',
                        'work_rule_5',
                        'work_rule_1_archived',
                        'work_rule_2',
                        'work_rule_3_default',
                        'work_rule_6_archived',
                    ],
                },
                'response': {
                    'work_rules': [
                        {'usage': 7, 'id': 'work_rule_4_archived'},
                        {'usage': 2, 'id': 'work_rule_5'},
                        {'usage': 4, 'id': 'work_rule_1_archived'},
                        {'usage': 8, 'id': 'work_rule_2'},
                        {'usage': 1, 'id': 'work_rule_3_default'},
                        {'usage': 999, 'id': 'work_rule_6_archived'},
                    ],
                },
            },
        ),
        ('park_without_work_rules', {}, 'empty_work_rules.json', {}),
        (
            'park_without_active_work_rules',
            {'is_archived': False},
            'empty_work_rules.json',
            {},
        ),
        (
            'park_without_archived_work_rules',
            {'is_archived': True},
            'empty_work_rules.json',
            {},
        ),
        (
            'extra_super_park_id',
            {},
            'without_countractors_count.json',
            {
                'request': {
                    'ids': [
                        'work_rule_4_archived',
                        'work_rule_5',
                        'work_rule_1_archived',
                        'work_rule_2',
                        'work_rule_3_default',
                        'work_rule_6_archived',
                    ],
                },
                'response': {'work_rules': []},
            },
        ),
    ],
)
async def test_ok(
        taxi_driver_work_rules,
        mockserver,
        load_json,
        park_id,
        params,
        expected_response,
        parks_service,
):
    @mockserver.json_handler('/parks/v1/work-rules/usage')
    def _v1_work_rules_usage(request):
        assert request.query == {'park_id': park_id}
        assert request.json == parks_service['request']
        return parks_service['response']

    response = await taxi_driver_work_rules.get(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS, {'X-Park-Id': park_id},
        ),
        params=params,
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json(expected_response)


@pytest.mark.parametrize(
    ('params', 'expected_response'),
    [
        (
            {'cursor': ''},
            {
                'code': 'invalid_cursor',
                'message': 'Invalid cursor JSON string',
            },
        ),
    ],
)
async def test_invalid_cursor(
        taxi_driver_work_rules, params, expected_response,
):
    response = await taxi_driver_work_rules.get(
        ENDPOINT, headers=defaults.HEADERS, params=params,
    )

    assert response.status_code == 400, response.text
    assert response.json() == expected_response
