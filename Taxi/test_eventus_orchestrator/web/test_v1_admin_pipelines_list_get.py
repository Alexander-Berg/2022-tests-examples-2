import pytest


@pytest.mark.parametrize(
    'instance_name, expected_status, pipelines_list',
    [
        (
            'order-events-producer',
            200,
            [
                {
                    'last_update_author': 'drft23427',
                    'name': 'communal-events',
                    'source': 'communal-events',
                },
                {
                    'last_update_author': 'drft23425',
                    'name': 'order-events',
                    'source': 'order-events',
                },
            ],
        ),
        (
            'atlas-proxy',
            200,
            [
                {
                    'last_update_author': 'drft2347810',
                    'name': 'atlas-surge',
                    'source': 'communal-events',
                },
            ],
        ),
        ('doesnt-exist', 404, None),
    ],
)
async def test_pipelines_list_get_oep(
        taxi_eventus_orchestrator_web,
        instance_name,
        expected_status,
        pipelines_list,
):
    response = await taxi_eventus_orchestrator_web.get(
        '/v1/admin/pipelines/list', params={'instance_name': instance_name},
    )

    assert response.status == expected_status

    if expected_status != 200:
        return

    body = await response.json()
    assert body['pipelines'] == pipelines_list
