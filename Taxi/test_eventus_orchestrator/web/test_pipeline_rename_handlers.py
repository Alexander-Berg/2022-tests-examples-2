async def make_test(
        taxi_eventus_orchestrator_web,
        instance,
        pipeline,
        new_name,
        expected_code,
):
    request_args = {
        'params': {'instance_name': instance, 'pipeline_name': pipeline},
        'json': {'new_name': new_name},
        'headers': {'X-YaTaxi-Draft-Id': 'draft'},
    }

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/check-rename', **request_args,
    )

    assert response.status == expected_code

    if expected_code == 200:
        body = await response.json()
        assert body == {
            'change_doc_id': f'eventus-orchestrator_{instance}_{pipeline}',
            'data': {'new_name': new_name},
            'diff': {'new': {'name': new_name}, 'current': {'name': pipeline}},
        }

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/rename', **request_args,
    )

    assert response.status == expected_code

    if expected_code == 200:
        response = await taxi_eventus_orchestrator_web.get(
            '/v1/admin/pipeline',
            params={'instance_name': instance, 'pipeline_name': new_name},
        )
        assert response.status == 200

        body = await response.json()
        assert body['main_version']['root'] is not None


async def test_correct_rename(taxi_eventus_orchestrator_web):
    await make_test(
        taxi_eventus_orchestrator_web,
        'order-events-producer',
        'order-events',
        'new-order-events',
        200,
    )
    await make_test(
        taxi_eventus_orchestrator_web,
        'order-events-producer',
        'communal-events',
        'new-communal-events',
        200,
    )


async def test_no_instance(taxi_eventus_orchestrator_web):
    await make_test(
        taxi_eventus_orchestrator_web,
        'order-events-no-instance',
        'order-events',
        'new-order-events',
        404,
    )


async def test_no_pipeline(taxi_eventus_orchestrator_web):
    await make_test(
        taxi_eventus_orchestrator_web,
        'order-events-producer',
        'order-events-no-pipeline',
        'new-order-events',
        404,
    )


async def test_pipeline_exists(taxi_eventus_orchestrator_web):
    await make_test(
        taxi_eventus_orchestrator_web,
        'order-events-producer',
        'order-events',
        'communal-events',
        409,
    )
