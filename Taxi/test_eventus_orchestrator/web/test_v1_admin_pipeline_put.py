import datetime

import pytest

import eventus_orchestrator.common.utils as utils
from .. import pipeline_tools


async def make_test_iter(
        i, thread_num, taxi_eventus_orchestrator_web, mongodb,
):
    action = 'create' if i == 1 else 'update'
    pipeline_json = pipeline_tools.get_test_pipeline_to_put(i, action)
    draft_id = f'draft_id_{i}'

    if thread_num is not None:
        pipeline_tools.add_thread_num(pipeline_json['new_value'], thread_num)

    await pipeline_tools.update_schema_for_test(
        i, taxi_eventus_orchestrator_web,
    )

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/update',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'test-pipeline',
        },
        json=pipeline_json,
        headers={'X-YaTaxi-Draft-Id': draft_id},
    )

    assert response.status == 200

    get_response = await taxi_eventus_orchestrator_web.get(
        '/v1/admin/pipeline',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'test-pipeline',
        },
    )

    pipeline_tools.add_thread_num(
        pipeline_json['new_value'], 3 if thread_num is None else thread_num,
    )

    assert get_response.status == 200
    body = await get_response.json()
    assert body['main_version'] == pipeline_json['new_value']

    pipeline_info = mongodb.eventus_pipelines.find_one(
        {'instance': 'order-events-producer', 'pipeline': 'test-pipeline'},
    )

    assert len(pipeline_info['versions']) == i

    for j in range(1, i):
        expected = pipeline_tools.get_test_pipeline_to_put(j, action)[
            'new_value'
        ]
        pipeline_tools.add_thread_num(
            expected, 3 if thread_num is None else thread_num,
        )
        assert pipeline_info['versions'][j - 1]['pipeline'] == expected

    last_version = pipeline_info['versions'][-1]
    assert last_version['pipeline'] == pipeline_json['new_value']
    assert last_version['draft_id'] == draft_id
    assert last_version['pipeline_hash'] == utils.build_cursor_from_pipeline(
        pipeline_json['new_value'],
    )


async def test_pipeline_put(taxi_eventus_orchestrator_web, mongodb):
    for i in range(1, 6):
        await make_test_iter(i, None, taxi_eventus_orchestrator_web, mongodb)


async def test_pipeline_put_no_instance(taxi_eventus_orchestrator_web):
    await pipeline_tools.update_schema_for_test(
        0, taxi_eventus_orchestrator_web,
    )

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/update',
        params={
            'instance_name': 'doesnt_exist',
            'pipeline_name': 'test-pipeline',
        },
        json=pipeline_tools.get_test_pipeline_to_put(0, 'create'),
        headers={'X-YaTaxi-Draft-Id': 'draft_id_0'},
    )

    assert response.status == 404


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_created_field(
        taxi_eventus_orchestrator_web, mongodb, mocked_time,
):
    for i in range(1, 25):
        await make_test_iter(i, None, taxi_eventus_orchestrator_web, mongodb)

        mocked_time.sleep(1)
        await taxi_eventus_orchestrator_web.invalidate_caches()

    pipeline_info = mongodb.eventus_pipelines.find_one(
        {'instance': 'order-events-producer', 'pipeline': 'test-pipeline'},
    )

    assert len(pipeline_info['versions']) == 24

    for i, version in enumerate(pipeline_info['versions']):
        assert version['created'] == datetime.datetime(2019, 1, 1, 12, 0, i)


@pytest.mark.parametrize('number_of_threads', [1, 9, 5, 7, 100])
async def test_number_of_threads(
        taxi_eventus_orchestrator_web, mongodb, number_of_threads,
):
    for i in range(1, 3):
        await make_test_iter(
            i, number_of_threads, taxi_eventus_orchestrator_web, mongodb,
        )


@pytest.mark.parametrize('number_of_threads', [-5, -1, 0, 101])
async def test_incorrect_number_of_threads(
        taxi_eventus_orchestrator_web, number_of_threads,
):
    pipeline_json = pipeline_tools.get_test_pipeline_to_put(0, 'create')
    draft_id = f'draft_id_0'

    pipeline_tools.add_thread_num(
        pipeline_json['new_value'], number_of_threads,
    )

    await pipeline_tools.update_schema_for_test(
        0, taxi_eventus_orchestrator_web,
    )

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/update',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'test-pipeline',
        },
        json=pipeline_json,
        headers={'X-YaTaxi-Draft-Id': draft_id},
    )

    assert response.status == 400
