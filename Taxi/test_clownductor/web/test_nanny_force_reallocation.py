import pytest


@pytest.mark.pgsql('clownductor', files=['init_db.sql'])
async def test_nanny_force_reallocation_handle(web_app_client, task_processor):
    response = await web_app_client.post(
        '/v1/services/nanny/force_reallocation/',
        params={'branch_id': 1},
        json={'reallocation_coefficient': 2},
        headers={'X-Yandex-Login': 'karachevda'},
    )
    assert response.status == 200
    data = await response.json()
    assert data == {'clownductor_job_id': 1, 'task_processor_job_id': 1}
    job = task_processor.find_job(1)
    assert job.job_vars == {
        'reallocation_coefficient': 2,
        'nanny_name': 'taxi_cool_service_stable',
        'user': 'karachevda',
        'service_id': 1,
        'branch_id': 1,
        'role_to_check': 'nanny_admin_prod',
        'locale': 'ru',
    }
