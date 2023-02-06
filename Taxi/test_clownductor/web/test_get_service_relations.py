import pytest


@pytest.mark.parametrize(
    'service_id,expected_related_services',
    [
        (
            1,
            [
                {
                    'service_id': 3,
                    'service_name': 'test-db1',
                    'cluster_type': 'postgres',
                    'project_id': 1,
                    'relation_type': 'database',
                },
            ],
        ),
        (
            2,
            [
                {
                    'service_id': 3,
                    'service_name': 'test-db1',
                    'cluster_type': 'postgres',
                    'project_id': 1,
                    'relation_type': 'database',
                },
                {
                    'service_id': 4,
                    'service_name': 'test-db2',
                    'cluster_type': 'mongo_mdb',
                    'project_id': 1,
                    'relation_type': 'database',
                },
            ],
        ),
        (
            3,
            [
                {
                    'service_id': 1,
                    'service_name': 'test-service1',
                    'cluster_type': 'nanny',
                    'project_id': 1,
                    'relation_type': 'database_consumer',
                },
                {
                    'service_id': 2,
                    'service_name': 'test-service2',
                    'cluster_type': 'nanny',
                    'project_id': 1,
                    'relation_type': 'database_consumer',
                },
            ],
        ),
        (
            4,
            [
                {
                    'service_id': 2,
                    'service_name': 'test-service2',
                    'cluster_type': 'nanny',
                    'project_id': 1,
                    'relation_type': 'database_consumer',
                },
                {
                    'service_id': 5,
                    'service_name': 'test-service3',
                    'cluster_type': 'conductor',
                    'project_id': 1,
                    'relation_type': 'database_consumer',
                },
            ],
        ),
        (
            5,
            [
                {
                    'service_id': 4,
                    'service_name': 'test-db2',
                    'cluster_type': 'mongo_mdb',
                    'project_id': 1,
                    'relation_type': 'database',
                },
            ],
        ),
        (6, []),
        (7, []),
    ],
)
@pytest.mark.pgsql('clownductor', files=['add_test_data.sql'])
async def test_get_related_services(
        web_app_client, service_id, expected_related_services,
):
    response = await web_app_client.get(
        '/v1/service/related', params={'service_id': service_id},
    )
    assert response.status == 200
    assert (await response.json()) == {
        'related_services': expected_related_services,
    }


@pytest.mark.pgsql('clownductor', files=['add_test_data.sql'])
async def test_get_related_services_404(web_app_client):
    response = await web_app_client.get(
        '/v1/service/related', params={'service_id': 8},
    )
    assert response.status == 404
    assert (await response.json()) == {
        'code': 'SERVICE_NOT_FOUND',
        'message': 'service not found',
    }
