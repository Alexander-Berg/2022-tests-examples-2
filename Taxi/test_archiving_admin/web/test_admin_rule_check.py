import pytest


@pytest.mark.pgsql('archiving_admin', files=['pg_test_archiving_rules.sql'])
@pytest.mark.parametrize(
    ('request_rules_check', 'expected_status', 'expected_response'),
    [
        (
            [{'rule_name': 'test_abc', 'period': 200, 'action': 'enable'}],
            200,
            {
                'data': {
                    'rules': [
                        {
                            'rule_name': 'test_abc',
                            'period': 200,
                            'action': 'enable',
                        },
                    ],
                },
                'diff': {
                    'new': {
                        'rules': [
                            {
                                'rule_name': 'test_abc',
                                'period': 200,
                                'is_enabled': True,
                                'sleep_delay': 2,
                            },
                        ],
                    },
                    'current': {
                        'rules': [
                            {
                                'rule_name': 'test_abc',
                                'period': 300,
                                'is_enabled': False,
                                'sleep_delay': 2,
                            },
                        ],
                    },
                },
            },
        ),
        (
            [{'rule_name': 'test_abc', 'period': 200}],
            200,
            {
                'data': {'rules': [{'rule_name': 'test_abc', 'period': 200}]},
                'diff': {
                    'new': {
                        'rules': [
                            {
                                'rule_name': 'test_abc',
                                'period': 200,
                                'is_enabled': False,
                                'sleep_delay': 2,
                            },
                        ],
                    },
                    'current': {
                        'rules': [
                            {
                                'rule_name': 'test_abc',
                                'period': 300,
                                'is_enabled': False,
                                'sleep_delay': 2,
                            },
                        ],
                    },
                },
            },
        ),
        (
            [
                {'rule_name': 'test_abc', 'period': 200, 'sleep_delay': 1},
                {'rule_name': 'test_foo_1', 'period': 200, 'sleep_delay': 1},
                {'rule_name': 'test_foo_2', 'period': 22, 'sleep_delay': 22},
            ],
            200,
            {
                'data': {
                    'rules': [
                        {
                            'rule_name': 'test_abc',
                            'period': 200,
                            'sleep_delay': 1,
                        },
                        {
                            'rule_name': 'test_foo_1',
                            'period': 200,
                            'sleep_delay': 1,
                        },
                        {
                            'rule_name': 'test_foo_2',
                            'period': 22,
                            'sleep_delay': 22,
                        },
                    ],
                },
                'diff': {
                    'new': {
                        'rules': [
                            {
                                'rule_name': 'test_abc',
                                'period': 200,
                                'is_enabled': False,
                                'sleep_delay': 1,
                            },
                            {
                                'rule_name': 'test_foo_1',
                                'period': 200,
                                'is_enabled': False,
                                'sleep_delay': 1,
                            },
                            {
                                'rule_name': 'test_foo_2',
                                'period': 22,
                                'is_enabled': False,
                                'sleep_delay': 22,
                            },
                        ],
                    },
                    'current': {
                        'rules': [
                            {
                                'rule_name': 'test_abc',
                                'period': 300,
                                'is_enabled': False,
                                'sleep_delay': 2,
                            },
                            {
                                'rule_name': 'test_foo_1',
                                'period': 300,
                                'is_enabled': False,
                                'sleep_delay': 2,
                            },
                            {
                                'rule_name': 'test_foo_2',
                                'period': 300,
                                'is_enabled': False,
                                'sleep_delay': 2,
                            },
                        ],
                    },
                },
            },
        ),
        (
            [{'rule_name': 'foo_bar', 'period': 200}],
            400,
            {
                'code': 'rule-check-error',
                'message': '\'foo_bar\' is not registered',
            },
        ),
    ],
)
async def test_change(
        web_app,
        web_app_client,
        request_rules_check,
        expected_status,
        expected_response,
):
    response = await web_app_client.post(
        '/admin/v1/rules/check', json={'rules': request_rules_check},
    )
    assert response.status == expected_status, await response.text()
    content = await response.json()
    assert content == expected_response
