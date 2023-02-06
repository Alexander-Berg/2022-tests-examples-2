import datetime

import pytest


async def make_test(
        taxi_eventus_orchestrator_web,
        mongodb,
        mocked_time,
        time_to_set,
        instance,
        pipeline,
        expected_code,
):
    mocked_time.set(time_to_set)

    request_args = {
        'params': {'instance_name': instance, 'pipeline_name': pipeline},
        'headers': {'X-YaTaxi-Draft-Id': 'draft'},
    }

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/check-delete', **request_args,
    )

    assert response.status == expected_code

    if expected_code == 200:
        body = await response.json()
        assert body == {
            'change_doc_id': f'eventus-orchestrator_{instance}_{pipeline}',
            'data': {},
        }

    pipeline_before_delete = None
    if expected_code == 200:
        pipeline_before_delete = mongodb.eventus_pipelines.find_one(
            {'instance': instance, 'pipeline': pipeline},
        )

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/delete', **request_args,
    )

    assert response.status == expected_code

    if expected_code == 200:
        response = await taxi_eventus_orchestrator_web.get(
            '/v1/admin/pipeline',
            params={'instance_name': instance, 'pipeline_name': pipeline},
        )
        assert response.status == 404

        pipeline_after_delete = mongodb.eventus_deleted_pipelines.find_one(
            {'instance': instance, 'pipeline': pipeline},
        )

        assert pipeline_after_delete == {
            **pipeline_before_delete,
            'delete_date': time_to_set,
        }


@pytest.mark.parametrize(
    'time_to_set',
    [
        datetime.datetime(2019, 1, 1, 10, 10, 10),
        datetime.datetime(2017, 1, 1, 1, 1, 1),
        datetime.datetime(2000, 2, 2, 2, 2, 2),
    ],
)
async def test_correct_delete(
        taxi_eventus_orchestrator_web, mongodb, mocked_time, time_to_set,
):
    await make_test(
        taxi_eventus_orchestrator_web,
        mongodb,
        mocked_time,
        time_to_set,
        'order-events-producer',
        'order-events',
        200,
    )
    await make_test(
        taxi_eventus_orchestrator_web,
        mongodb,
        mocked_time,
        time_to_set,
        'order-events-producer',
        'communal-events',
        200,
    )
    await make_test(
        taxi_eventus_orchestrator_web,
        mongodb,
        mocked_time,
        time_to_set,
        'order-events-producer',
        'no-versions',
        200,
    )


async def test_no_instance(
        taxi_eventus_orchestrator_web, mongodb, mocked_time,
):
    await make_test(
        taxi_eventus_orchestrator_web,
        mongodb,
        mocked_time,
        datetime.datetime(2000, 2, 2, 2, 2, 2),
        'order-events-producer-no',
        'order-events',
        404,
    )


async def test_no_pipeline(
        taxi_eventus_orchestrator_web, mongodb, mocked_time,
):
    await make_test(
        taxi_eventus_orchestrator_web,
        mongodb,
        mocked_time,
        datetime.datetime(2000, 2, 2, 2, 2, 2),
        'order-events-producer',
        'order-events-no',
        404,
    )
