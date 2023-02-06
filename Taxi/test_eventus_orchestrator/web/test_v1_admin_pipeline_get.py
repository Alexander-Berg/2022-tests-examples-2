import pytest

from .. import pipeline_tools


@pytest.mark.parametrize(
    'instance_name, pipeline_name, expected_status, pipeline_has_add_info',
    [
        ('order-events-producer', 'order-events', 200, True),
        ('order-events-producer', 'communal-events', 200, False),
        ('order-events-producer', 'doesnt-exist', 404, False),
        ('order-events-producer', 'no-versions', 404, False),
        ('doesnt-exist', 'order-events', 404, False),
        ('doesnt-exist', 'communal-events', 404, False),
    ],
)
async def test_pipeline_get(
        taxi_eventus_orchestrator_web,
        instance_name,
        pipeline_name,
        expected_status,
        pipeline_has_add_info,
):
    response = await taxi_eventus_orchestrator_web.get(
        '/v1/admin/pipeline',
        params={
            'instance_name': instance_name,
            'pipeline_name': pipeline_name,
        },
    )

    assert response.status == expected_status

    if expected_status != 200:
        return

    body = await response.json()
    pipeline = body['main_version']
    assert pipeline == pipeline_tools.get_test_pipeline(
        pipeline_name, pipeline_has_add_info,
    )
