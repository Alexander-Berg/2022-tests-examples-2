import datetime

import pytest

from piecework_calculation import agent
from piecework_calculation import calculation_rules

NOW = datetime.datetime(2020, 1, 10, 10, 0)

RESPONSE_OK = {
    'items': [
        {'login': 'ivanov', 'team': 'general', 'country': 'ru'},
        {'login': 'petrov', 'team': 'general', 'country': 'ru'},
        {'login': 'smirnoff', 'team': 'general', 'country': 'ru'},
    ],
}

PG_RESULT = [
    {
        'start_date': datetime.date(2020, 1, 1),
        'stop_date': datetime.date(2020, 1, 16),
        'login': 'ivanov',
        'country': 'ru',
        'branch': 'general',
    },
    {
        'start_date': datetime.date(2020, 1, 1),
        'stop_date': datetime.date(2020, 1, 16),
        'login': 'petrov',
        'country': 'ru',
        'branch': 'general',
    },
    {
        'start_date': datetime.date(2020, 1, 1),
        'stop_date': datetime.date(2020, 1, 16),
        'login': 'smirnoff',
        'country': 'ru',
        'branch': 'general',
    },
]


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'calculation_rule_id, expected_project, expected_pg_result, '
    'expected_extra_projects',
    [
        ('unified_rule_id', 'calltaxi', PG_RESULT, None),
        ('cargo_rule_id', 'calldelivery', PG_RESULT, None),
        (
            'logins_rule_id',
            'taxisupport',
            PG_RESULT
            + [
                {
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'wopov',
                    'country': 'ru',
                    'branch': 'second',
                },
            ],
            ['marketsupport'],
        ),
    ],
)
async def test_fetch_ok(
        cron_context,
        mock_agent_employees,
        calculation_rule_id,
        expected_project,
        expected_pg_result,
        expected_extra_projects,
):
    mocked_agent_employees = mock_agent_employees(RESPONSE_OK)

    async with cron_context.pg.slave_pool.acquire() as conn:
        rule = await calculation_rules.find_by_id(
            cron_context, calculation_rule_id, conn,
        )
    employees = await agent.fetch_employees(cron_context, rule)
    assert employees == {
        'ivanov': {
            'login': 'ivanov',
            'branch': 'general',
            'country': 'ru',
            'rating_factor': 1.0,
        },
        'petrov': {
            'login': 'petrov',
            'branch': 'general',
            'country': 'ru',
            'rating_factor': 1.0,
        },
        'smirnoff': {
            'login': 'smirnoff',
            'branch': 'general',
            'country': 'ru',
            'rating_factor': 1.0,
        },
    }
    employees_call = mocked_agent_employees.next_call()
    assert employees_call['request'].json == {
        'project': expected_project,
        'start_date': '2020-01-01',
        'stop_date': '2020-01-16',
    }
    if expected_extra_projects is None:
        assert not mocked_agent_employees.has_calls
        return
    for project in expected_extra_projects:
        employees_call = mocked_agent_employees.next_call()
        assert employees_call['request'].json == {
            'project': project,
            'start_date': '2020-01-01',
            'stop_date': '2020-01-16',
        }
    assert not mocked_agent_employees.has_calls
