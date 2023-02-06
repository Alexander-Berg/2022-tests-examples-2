import pytest


@pytest.mark.parametrize(
    ['branch_id', 'status', 'expected', 'expected_job'],
    [
        (
            1,
            400,
            {
                'code': 'WRONG_SERVICE_TYPE',
                'message': (
                    'Service must be in redis_mdb, '
                    'mongo_mdb, postgres, clickhouse, mysql, ydb'
                ),
            },
            {},
        ),
        (
            2,
            200,
            {'clownductor_job_id': 1, 'task_processor_job_id': 1},
            {
                'abc_slug': 'abc_service',
                'branch_id': 2,
                'cluster_id': 'mongo_cluster',
                'db_type': 'mongo',
                'flavor_level_change': 2,
                'locale': 'ru',
                'roles_ids_to_check': [1, 17, 1258, 1259],
                'service_id': 2,
                'user': 'karachevda',
            },
        ),
        (
            3,
            200,
            {'clownductor_job_id': 1, 'task_processor_job_id': 1},
            {
                'abc_slug': 'abc_service',
                'branch_id': 3,
                'cluster_id': 'postgres_cluster',
                'db_type': 'pgaas',
                'flavor_level_change': 2,
                'locale': 'ru',
                'roles_ids_to_check': [1, 17, 1258, 1259],
                'service_id': 3,
                'user': 'karachevda',
            },
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_db.sql'])
async def test_mdb_force_reallocation_handle(
        web_app_client,
        task_processor,
        branch_id,
        status,
        expected,
        expected_job,
):
    response = await web_app_client.post(
        '/v1/services/mdb/force_reallocation/',
        params={'branch_id': branch_id},
        json={'flavor_change_level': 2},
        headers={'X-Yandex-Login': 'karachevda'},
    )
    data = await response.json()
    assert response.status == status, data
    assert data == expected
    if status == 200:
        job = task_processor.find_job(1)
        assert job.job_vars == expected_job
