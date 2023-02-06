import pytest

_RULE_INFO_ABC = {
    'rule_name': 'test_abc',
    'group_name': 'abc',
    'source_type': 'bar',
}
_TEST_RULE_DEFAULTS = {
    'period': 300,
    'sleep_delay': 2,
    'ttl_duration': None,
    'enabled': False,
}


def _get_rule_db_state(**kwargs):
    return {**_TEST_RULE_DEFAULTS, **kwargs}


@pytest.mark.pgsql('archiving_admin', files=['pg_test_archiving_rules.sql'])
@pytest.mark.parametrize(
    'request_rules_change,expected_status,expected_response,expected_db',
    [
        (
            [{'rule_name': 'test_abc', 'period': 200}],
            200,
            {'rules': [_RULE_INFO_ABC]},
            {'test_abc': _get_rule_db_state(period=200)},
        ),
        (
            [{'rule_name': 'test_abc', 'period': 200, 'ttl_duration': 10}],
            200,
            {'rules': [_RULE_INFO_ABC]},
            {'test_abc': _get_rule_db_state(period=200, ttl_duration=10)},
        ),
        (
            [{'rule_name': 'test_abc', 'period': 200, 'sleep_delay': 1}],
            200,
            {'rules': [_RULE_INFO_ABC]},
            {'test_abc': _get_rule_db_state(period=200, sleep_delay=1)},
        ),
        (
            [{'rule_name': 'test_abc', 'period': 300, 'sleep_delay': 2}],
            400,
            {
                'code': 'rule-change-error',
                'message': '\'test_abc\': has no actions to change',
            },
            {'test_abc': _get_rule_db_state()},
        ),
        (
            [
                {'rule_name': 'test_abc', 'period': 200, 'sleep_delay': 1},
                {'rule_name': 'test_foo_1', 'period': 200, 'sleep_delay': 1},
                {'rule_name': 'test_foo_2', 'period': 22, 'sleep_delay': 22},
            ],
            200,
            {
                'rules': [
                    _RULE_INFO_ABC,
                    {
                        'rule_name': 'test_foo_1',
                        'group_name': 'foo',
                        'source_type': 'bar',
                    },
                    {
                        'rule_name': 'test_foo_2',
                        'group_name': 'foo',
                        'source_type': 'bar',
                    },
                ],
            },
            {
                'test_abc': _get_rule_db_state(period=200, sleep_delay=1),
                'test_foo_1': _get_rule_db_state(period=200, sleep_delay=1),
                'test_foo_2': _get_rule_db_state(period=22, sleep_delay=22),
            },
        ),
        (
            [{'rule_name': 'test_abc', 'action': 'enable'}],
            200,
            {'rules': [_RULE_INFO_ABC]},
            {
                'test_abc': _get_rule_db_state(enabled=True),
                'test_foo_1': _get_rule_db_state(),
                'test_foo_2': _get_rule_db_state(),
            },
        ),
        (
            [{'rule_name': 'test_abc', 'action': 'disable'}],
            409,
            {
                'code': 'rule-change-error',
                'message': (
                    '\'test_abc\': '
                    'invalid action \'disable\' for rule in state disabled'
                ),
            },
            {'test_abc': _get_rule_db_state()},
        ),
    ],
)
async def test_change(
        web_app,
        web_app_client,
        request_rules_change,
        expected_status,
        expected_response,
        expected_db,
):
    response = await web_app_client.post(
        '/admin/v1/rules/change', json={'rules': request_rules_change},
    )
    assert response.status == expected_status, await response.text()
    content = await response.json()
    assert content == expected_response

    if expected_db is not None:
        actual_db = await web_app['context'].pg.archiving_rules.fetch(
            'SELECT * FROM archiving.rules',
        )
        actual_db = {state['rule_name']: state for state in actual_db}
        for rule_name, expected_state in expected_db.items():
            for key, expected_value in expected_state.items():
                assert (
                    actual_db[rule_name][key] == expected_value
                ), f'{rule_name}.{key}'
