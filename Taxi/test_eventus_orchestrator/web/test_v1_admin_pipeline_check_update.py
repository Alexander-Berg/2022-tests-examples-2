import pytest

from .. import pipeline_tools


@pytest.mark.parametrize(
    'instance_name, pipeline_name, expected_status, '
    'pipeline_has_add_info, action',
    [
        ('order-events-producer', 'order-events', 200, True, 'update'),
        ('order-events-producer', 'communal-events', 200, False, 'update'),
        ('order-events-producer', 'doesnt-exist', 200, False, 'create'),
        ('order-events-producer', 'no-versions', 200, False, 'update'),
        ('doesnt-exist', 'order-events', 404, False, 'create'),
        ('doesnt-exist', 'communal-events', 404, False, 'create'),
    ],
)
async def test_pipeline_check_update(
        taxi_eventus_orchestrator_web,
        instance_name,
        pipeline_name,
        expected_status,
        pipeline_has_add_info,
        action,
):
    await pipeline_tools.update_schema_for_test(
        0, taxi_eventus_orchestrator_web,
    )
    req_json = pipeline_tools.get_test_pipeline_to_put(0, action)
    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/check-update',
        params={
            'instance_name': instance_name,
            'pipeline_name': pipeline_name,
        },
        json=req_json,
    )

    assert response.status == expected_status

    if expected_status != 200:
        return

    body = await response.json()

    pipeline_tools.add_thread_num(req_json['new_value'])

    diff_curr_expected = (
        {}
        if pipeline_name in ('doesnt-exist', 'no-versions')
        else {
            'main_version': pipeline_tools.get_test_pipeline(
                pipeline_name, pipeline_has_add_info,
            ),
        }
    )
    assert body == {
        'change_doc_id': (
            f'eventus-orchestrator_{instance_name}_{pipeline_name}'
        ),
        'data': req_json,
        'diff': {
            'new': {'main_version': req_json['new_value']},
            'current': diff_curr_expected,
        },
    }
