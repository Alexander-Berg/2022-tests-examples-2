import typing

import pytest

from generated.models import archiving_admin

from archiving.generated.cron import run_monrun


class _MockRule(typing.NamedTuple):
    name: str
    period: int


_MOCK_RULES = [
    _MockRule(name='critical_collection_from_config', period=3600),
    _MockRule(name='critical_collection_fails_old_sync', period=3600),
    _MockRule(name='critical_collection', period=3600),
    _MockRule(name='critical_collection_few_removed', period=3600),
    _MockRule(name='warning_collection_in_progress', period=3600),
    _MockRule(name='warn_collection_no_fails', period=3600),
    _MockRule(name='ok_collection', period=24 * 3600),
    _MockRule(name='ok_no_last_runs', period=3600),
    _MockRule(name='ok_collection_with_fails', period=3600),
]


@pytest.fixture
async def _retrieve_rules_mock(
        cron_context,
        mockserver,
        mock_archiving_admin,
        load_py_json,
        patch_test_env,
):
    @mock_archiving_admin('/admin/v1/rules/retrieve')
    async def rules_retrieve(request):  # pylint: disable=unused-variable
        response = {'rules': []}
        last_runs_by_rules = load_py_json('last_runs_by_rules.json')
        for mock_rule in _MOCK_RULES:
            rule_last_runs = []
            last_runs_raw = last_runs_by_rules[mock_rule.name]
            for last_run_raw in last_runs_raw:
                rule_last_runs.append(
                    archiving_admin.AdminRunInfoItem(link='', **last_run_raw),
                )
            response['rules'].append(
                archiving_admin.RulesRetrieveResponse.RulesItem(
                    group_name=mock_rule.name,
                    rule_name=mock_rule.name,
                    source_type='mongo',
                    period=mock_rule.period,
                    sleep_delay=5,
                    enabled=True,
                    last_run=rule_last_runs,
                    ttl_duration=3600,
                ).serialize(),
            )
        return response


@pytest.mark.now('2018-05-21T08:00:00.0')
@pytest.mark.config(
    ARCHIVING_SERVICE_DELAYS_THRESHOLDS={
        'critical_collection_from_config': {
            'archiving_delay': {'warning': 30 * 60, 'critical': 60 * 60},
        },
    },
)
async def test_archivation(_retrieve_rules_mock):
    msg = await run_monrun.run(['archiving.monrun_checks.delays'])
    assert msg == (
        '2; CRIT (6 problems): critical_collection: archiving_delay = 241 min,'
        ' critical_collection_fails_old_sync: archiving_delay = 241 min,'
        ' previous_runs_failed = 2, critical_collection_few_removed:'
        ' archiving_delay = 190 min, previous_runs_failed = 2,'
        ' critical_collection_from_config: archiving_delay = 61 min,'
        ' WARN (2 problems): warn_collection_no_fails: archiving_delay'
        ' = 131 min, warning_collection_in_progress: previous_runs_failed = 1'
    )
