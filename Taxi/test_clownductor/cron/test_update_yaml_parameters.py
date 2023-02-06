import operator
from typing import Dict
from typing import List

import pytest

from client_github import components as github
from testsuite.utils import matching

from clownductor.generated.cron import run_cron
from clownductor.internal import service_issues
from clownductor.internal.utils import postgres


PARAMS_QUERY = """
select
    id,
    service_id,
    branch_id,
    subsystem_name
from
    clownductor.parameters
;
"""


EXPECTED_PARAMS: List[Dict] = [
    {'id': 1, 'service_id': 5, 'branch_id': None, 'subsystem_name': 'abc'},
    {
        'id': 2,
        'service_id': 5,
        'branch_id': None,
        'subsystem_name': 'service_info',
    },
    {'branch_id': 1, 'id': 3, 'service_id': 1, 'subsystem_name': 'abc'},
    {'branch_id': None, 'id': 4, 'service_id': 1, 'subsystem_name': 'nanny'},
    {'branch_id': 1, 'id': 5, 'service_id': 1, 'subsystem_name': 'nanny'},
    {'branch_id': 2, 'id': 6, 'service_id': 1, 'subsystem_name': 'nanny'},
    {
        'branch_id': None,
        'id': 7,
        'service_id': 1,
        'subsystem_name': 'service_info',
    },
    {
        'id': 8,
        'service_id': 1,
        'branch_id': 1,
        'subsystem_name': 'service_info',
    },
    {'branch_id': 3, 'id': 9, 'service_id': 2, 'subsystem_name': 'abc'},
    {'branch_id': None, 'id': 10, 'service_id': 2, 'subsystem_name': 'nanny'},
    {
        'branch_id': None,
        'id': 11,
        'service_id': 2,
        'subsystem_name': 'service_info',
    },
    {
        'branch_id': 3,
        'id': 12,
        'service_id': 2,
        'subsystem_name': 'service_info',
    },
    {'branch_id': None, 'id': 13, 'service_id': 3, 'subsystem_name': 'abc'},
    {'branch_id': 5, 'id': 14, 'service_id': 3, 'subsystem_name': 'abc'},
    {
        'branch_id': None,
        'id': 15,
        'service_id': 3,
        'subsystem_name': 'service_info',
    },
    {
        'branch_id': 5,
        'id': 16,
        'service_id': 3,
        'subsystem_name': 'service_info',
    },
]
EXPECTED_IDS = {x['id'] for x in EXPECTED_PARAMS}
assert len(EXPECTED_IDS) == len(EXPECTED_PARAMS)
MEANINGFUL_FIELDS = ['service_id', 'branch_id', 'subsystem_name']
ITEMGETTER = operator.itemgetter(*MEANINGFUL_FIELDS)


EXPECTED_ISSUES: List[Dict] = []


def _sorter(params):
    return sorted(params, key=(lambda x: tuple(y or 0 for y in ITEMGETTER(x))))


def _no_ids(params):
    return [dict(zip(ITEMGETTER(x), MEANINGFUL_FIELDS)) for x in params]


@pytest.mark.config(
    CLOWNDUCTOR_SYNC_YAML_PARAMETERS={
        'enabled': True,
        'dry_run': False,
        'tasks_at_time': 5,
    },
    CLOWNDUCTOR_FEATURES_PER_SERVICE={
        '__default__': {'check_service_yaml_service_issues_cron': True},
    },
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_sync_yaml_parameters(cron_context, web_context, patch, load):
    @patch('client_github.components.GithubClient.get_single_file')
    async def _get_file(**kwargs):
        path = kwargs['path']
        if path == 'service-1/service.yaml':
            filename = 'service_1.yaml'
        elif path == 'service-2/service.yaml':
            filename = 'service_2.yaml'
        elif path == 'service-3/service.yaml':
            filename = 'service_3.yaml'
        elif path == 'service-4/service.yaml':
            filename = 'service_4.yaml'
        elif path == 'service-5/service.yaml':
            filename = 'service_5.yaml'
        else:
            raise github.NotFoundError(content='', status_code=404)

        data = load(filename)
        return data.encode()

    await run_cron.main(
        ['clownductor.crontasks.update_yaml_parameters', '-t', '0'],
    )
    assert len(_get_file.calls) == 6

    params = await _get_params(cron_context)
    assert _no_ids(params) == _no_ids(_sorter(EXPECTED_PARAMS))

    db_ids = {x['id'] for x in params}
    assert db_ids == EXPECTED_IDS

    issues = await web_context.service_manager.service_issues.get_all_issues()
    issues.sort(key=lambda x: x.service_id)
    assert issues == [
        service_issues.ServiceIssue(
            id=matching.positive_integer,
            service_id=4,
            issue_key='service_yaml_missed',
            issue_parameters={},
        ),
        service_issues.ServiceIssue(
            id=matching.positive_integer,
            service_id=6,
            issue_key='service_yaml_is_broken',
            issue_parameters={},
        ),
        service_issues.ServiceIssue(
            id=matching.positive_integer,
            service_id=7,
            issue_key='service_yaml_missed',
            issue_parameters={},
        ),
    ]


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.features_on('check_service_yaml_service_issues_cron')
async def test_sync_yaml_parameters_with_errors(
        cron_context, web_context, patch, load,
):
    @patch('client_github.components.GithubClient.get_single_file')
    async def _get_file(**kwargs):
        path = kwargs['path']
        if path == 'service-1/service.yaml':
            filename = 'service_1.yaml'
        else:
            raise Exception()
        data = load(filename)
        return data.encode()

    coro = run_cron.main(
        ['clownductor.crontasks.update_yaml_parameters', '-t', '0'],
    )
    with pytest.raises(RuntimeError):
        await coro
    assert len(_get_file.calls) == 6


async def _get_params(cron_context):
    async with postgres.primary_connect(cron_context) as conn:
        records = await conn.fetch(PARAMS_QUERY)
    return _sorter([dict(record) for record in records])
