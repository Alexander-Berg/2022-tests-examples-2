import pytest


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_start_change_quota(
        call_cube_handle, task_processor, get_job_from_internal,
):
    job_ids = [1, 2]
    await call_cube_handle(
        'MDBStartChangeQuotaBranches',
        {
            'content_expected': {
                'payload': {'job_ids': job_ids},
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'service_id': 2,
                    'destination_folder_id': 'destination-id',
                    'user': 'karachevda',
                    'db_type': 'pgaas',
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    for job_id in job_ids:
        job = await get_job_from_internal(job_id)
        expected = {
            'branch_id': 4,
            'cluster_id': 'stable_cluster_id',
            'db_type': 'pgaas',
            'destination_folder_id': 'destination-id',
            'service_id': 2,
            'user': 'karachevda',
        }
        if job_id == 2:
            expected['branch_id'] = 3
            expected['cluster_id'] = 'testing_cluster_id'
        assert job.job_vars == expected
