# pylint: disable=redefined-outer-name
import pytest

from eventus_orchestrator.generated.cron import run_cron
from .. import pipeline_tools


async def run_versions_clean():
    await run_cron.main(
        [
            'eventus_orchestrator.crontasks.remove_old_pipeline_versions',
            '-t',
            '0',
        ],
    )


async def insert_versions(
        taxi_eventus_orchestrator_web, pipeline_name, version_num,
):
    for i in range(version_num):
        action = 'create' if i == 0 else 'update'
        await pipeline_tools.insert_new_version(
            i, action, taxi_eventus_orchestrator_web, pipeline_name,
        )


async def check_versions(
        taxi_eventus_orchestrator_web, pipeline_name, version_indexes,
):
    if not version_indexes:
        return

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/versions/list',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': pipeline_name,
        },
        json={'limit': 1000},
    )

    assert response.status == 200

    body = await response.json()
    for i, version_info in enumerate(body['versions']):
        p_config = version_info['version']
        assert (
            p_config['description']
            == f'pipeline description {version_indexes[i]}'
        )
        assert (
            p_config['source']['name'] == f'source_name_{version_indexes[i]}'
        )
        assert p_config['root']['sink_name'] == f'sink_{version_indexes[i]}'


async def make_test(taxi_eventus_orchestrator_web, num):
    name_to_version_num = {
        'pipeline-test-lt': num - 1,
        'pipeline-test-eq': num,
        'pipeline-test-gt': num + 1,
        'pipeline-test-gt2': num + 5,
    }

    for name, version_num in name_to_version_num.items():
        await insert_versions(taxi_eventus_orchestrator_web, name, version_num)
        await check_versions(
            taxi_eventus_orchestrator_web, name, list(range(version_num)),
        )

    await run_versions_clean()

    for name, version_num in name_to_version_num.items():
        expected_indexes = list(range(version_num))
        if len(expected_indexes) > num:
            diff = len(expected_indexes) - num
            expected_indexes = expected_indexes[diff:]
        await check_versions(
            taxi_eventus_orchestrator_web, name, expected_indexes,
        )


@pytest.mark.parametrize('max_number', [1, 2, 4, 6])
async def test_remove_old_pipeline_versions(
        taxi_eventus_orchestrator_web, taxi_config, max_number,
):
    taxi_config.set_values(
        {'EVENTUS_ORCHESTRATOR_PIPELINE_VERSIONS_MAX_NUM': max_number},
    )
    await taxi_eventus_orchestrator_web.invalidate_caches()

    await make_test(taxi_eventus_orchestrator_web, max_number)
