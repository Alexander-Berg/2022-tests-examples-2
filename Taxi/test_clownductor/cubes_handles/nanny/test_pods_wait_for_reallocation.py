import pytest


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_pod_wait_for_reallocation(call_cube_handle, nanny_mockserver):
    await call_cube_handle(
        'ClownNannyWaitForReallocation',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {
                    'nanny_name': 'test_service_stable',
                    'reallocation_id': 'sepohhmdyqm6rqljvchenwbt',
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
