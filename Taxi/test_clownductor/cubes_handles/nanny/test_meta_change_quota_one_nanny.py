import pytest


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_change_quota_one_nanny(
        call_cube_handle, task_processor, get_job_from_internal,
):
    task_processor.load_recipe(
        {
            'name': 'ChangeQuotaOneNanny',
            'stages': [],
            'job_vars': {},
            'provider_name': 'clownductor',
        },
    )
    job_ids = [2, 3, 4]
    await call_cube_handle(
        'MetaChangeServiceQuotaNanny',
        {
            'content_expected': {
                'payload': {'job_ids': job_ids},
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'service_id': 1,
                    'new_quota_abc': 'abc-id',
                    'user': 'karachevda',
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    change_doc_ids = {
        'ChangeQuotaOneNanny_3',
        'ChangeQuotaOneNanny_2',
        'ChangeQuotaOneNanny_1',
    }
    for job_id in job_ids:
        job = await get_job_from_internal(job_id)
        expected = {
            'new_quota_abc': 'abc-id',
            'regions': ['VLA', 'MAN', 'SAS'],
            'service_id': 1,
            'st_ticket': None,
            'user': 'karachevda',
        }
        change_doc_ids.remove(job.change_doc_id)
        if job.change_doc_id == 'ChangeQuotaOneNanny_3':
            expected.update(
                {'branch_id': 3, 'nanny_name': 'test_service_pre_stable'},
            )
        elif job.change_doc_id == 'ChangeQuotaOneNanny_2':
            expected.update(
                {'branch_id': 2, 'nanny_name': 'test_service_stable'},
            )
        elif job.change_doc_id == 'ChangeQuotaOneNanny_1':
            expected.update(
                {'branch_id': 1, 'nanny_name': 'test_service_testing'},
            )
        else:
            raise ValueError(f'Bad change doc id {job.change_doc_id}')
        assert job.job_vars == expected

    assert not change_doc_ids
