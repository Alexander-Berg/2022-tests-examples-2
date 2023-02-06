import asyncio
import logging
import typing

from generated.models import testpalm as testpalm_module
from taxi.clients_wrappers import testpalm
from taxi.maintenance import run

from eats_automation_statistics.crontasks.eats_metrics.datasets import (
    testpalm_dataset,
)
from eats_automation_statistics.generated.cron import (
    cron_context as context_module,
)
from eats_automation_statistics.utils import pg_queries

logger = logging.getLogger(__name__)


async def get_definitions(
        testpalm_client: testpalm.TestpalmClient, project_id: str,
) -> typing.List[testpalm_module.Definition]:
    response = await testpalm_client.get_definitions(project_id)
    if response.status == 200:
        return response.body
    logger.error(
        'failed to get definitions from testpalm, '
        'status code must be 200, but: %s, testpalm project: %s',
        response.status,
        project_id,
    )
    return []


async def get_testcases(
        testpalm_client: testpalm.TestpalmClient, project_id: str,
) -> typing.List[testpalm_module.Testcase]:
    response = await testpalm_client.get_testcases(project_id)
    if response.status == 200:
        return response.body
    logger.error(
        'failed to get testcases from testpalm, '
        'status code must be 200, but: %s, testpalm project: %s',
        response.status,
        project_id,
    )
    return []


async def collect_testpalm_metrics(
        testpalm_client: testpalm.TestpalmClient, pg_client, project_id: str,
) -> int:
    tablename = ''.join(filter(str.isalpha, project_id))
    definitions = await get_definitions(testpalm_client, project_id)
    testcases = await get_testcases(testpalm_client, project_id)
    testcases_dataset = testpalm_dataset.TestpalmDataset(
        definitions=definitions,
    )
    testcases_dataset.aggregate(testcases)
    async with pg_client.master_pool.acquire() as conn:
        records_for_insert = [
            (
                row['testcase_id'],
                row['snapshot_time'],
                row['created_time'],
                row['status'],
                row['is_autotest'],
                row['automation_status'],
                row['priority'],
                row['case_group'],
            )
            for row in testcases_dataset.data
        ]
        initial_count = await conn.fetchval(
            pg_queries.TABLE_ROW_COUNT % tablename,
        )
        await conn.executemany(
            pg_queries.EATS_METRICS_INSERT_TESTPALM_INFO % tablename,
            records_for_insert,
        )
        changed_count = await conn.fetchval(
            pg_queries.TABLE_ROW_COUNT % tablename,
        )
        affected_count = changed_count - initial_count
        logger.info('Table %s: inserted %s records', tablename, affected_count)
        return affected_count


async def do_stuff(
        task_context: run.StuffContext,
        loop: asyncio.AbstractEventLoop,
        *,
        log_extra: typing.Optional[dict] = None,
):
    context = typing.cast(context_module.Context, task_context.data)
    logger.info('%s: starting task %s', context.unit_name, task_context.id)
    testpalm_projects = context.config.TESTPALM_PROJECTS
    for testpalm_project in testpalm_projects:
        testcases_count = await collect_testpalm_metrics(
            context.clients.testpalm, context.pg, testpalm_project,
        )
        if testpalm_project == 'ios-client':
            context.testpalm_metrics_stats.ios_client_testcases.add(
                testcases_count,
            )
        elif testpalm_project == 'new_tests':
            context.testpalm_metrics_stats.new_tests_testcases.add(
                testcases_count,
            )
