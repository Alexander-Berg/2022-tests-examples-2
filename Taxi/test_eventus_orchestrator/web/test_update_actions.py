from .. import pipeline_tools


async def run_action(
        taxi_eventus_orchestrator_web, action, handler, expected_code,
):
    req_json = pipeline_tools.get_test_pipeline_to_put(0, action)
    draft_id = f'draft_id_{0}'

    await pipeline_tools.update_schema_for_test(
        0, taxi_eventus_orchestrator_web,
    )

    response = await taxi_eventus_orchestrator_web.post(
        f'/v1/admin/pipeline/{handler}',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'test-pipeline',
        },
        json=req_json,
        headers={'X-YaTaxi-Draft-Id': draft_id},
    )

    assert response.status == expected_code


async def update_pipeline(
        taxi_eventus_orchestrator_web, action, expected_code,
):
    return await run_action(
        taxi_eventus_orchestrator_web, action, 'update', expected_code,
    )


async def check_pipeline(taxi_eventus_orchestrator_web, action, expected_code):
    return await run_action(
        taxi_eventus_orchestrator_web, action, 'check-update', expected_code,
    )


async def test_create_when_exists(taxi_eventus_orchestrator_web):
    await check_pipeline(taxi_eventus_orchestrator_web, 'create', 200)
    await update_pipeline(taxi_eventus_orchestrator_web, 'create', 200)
    await check_pipeline(taxi_eventus_orchestrator_web, 'create', 409)
    await update_pipeline(taxi_eventus_orchestrator_web, 'create', 500)


async def test_update_when_doesnt_exist(taxi_eventus_orchestrator_web):
    await check_pipeline(taxi_eventus_orchestrator_web, 'update', 404)
    await update_pipeline(taxi_eventus_orchestrator_web, 'update', 404)


async def test_correct_sequence(taxi_eventus_orchestrator_web):
    await check_pipeline(taxi_eventus_orchestrator_web, 'create', 200)
    await update_pipeline(taxi_eventus_orchestrator_web, 'create', 200)
    await update_pipeline(taxi_eventus_orchestrator_web, 'update', 200)
    await check_pipeline(taxi_eventus_orchestrator_web, 'update', 200)
    await update_pipeline(taxi_eventus_orchestrator_web, 'update', 200)
    await check_pipeline(taxi_eventus_orchestrator_web, 'update', 200)
