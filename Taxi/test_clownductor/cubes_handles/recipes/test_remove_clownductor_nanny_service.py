import pytest


@pytest.fixture(name='startrek_client_mock')
def _startrek_client_mock(
        st_get_myself, st_get_comments, st_create_comment, st_get_ticket,
):
    pass


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.features_on('delete_strongbox_from_arcadia')
async def test_remove_clownductor_nanny_service_with_creation_only(
        load_yaml,
        task_processor,
        run_job_with_meta,
        add_external_cubes,
        patch,
        startrek_client_mock,
):
    @patch('clownductor.internal.tasks.manager._create_job')
    async def _create_job(context, job_data, variables, recipe, conn):
        job = await task_processor.start_job(
            name=job_data['name'],
            job_vars=variables,
            initiator=job_data['initiator'],
            idempotency_token=job_data['idempotency_token'],
            change_doc_id=job_data['change_doc_id'],
        )
        return job.id

    @patch('clownductor.internal.tasks.manager.get_jobs')
    async def _get_jobs(context, db_conn, job_ids):
        jobs = task_processor.find_jobs(job_ids)
        return [job.to_api() for job in jobs]

    task_processor.load_recipe(
        {
            'name': 'RemoveNannyBranch',
            'provider_name': 'clownductor',
            'job_vars': ['branch_id', 'service_id'],
            'stages': [],
        },
    )

    add_external_cubes()
    job = await task_processor.start_job(
        job_vars={
            'service_id': 1,
            'st_ticket': 'COLLTICKET-1',
            'removal_end_comment': 'Some comment after delete service',
        },
        name='RemoveClownductorNannyService',
        initiator='clownductor',
        idempotency_token='some_token_1',
    )
    await run_job_with_meta(job)
    assert job.job_vars == {
        'service_id': 1,
        'st_ticket': 'COLLTICKET-1',
        'removal_end_comment': 'Some comment after delete service',
        'job_ids': [2, 3, 4],
        'diff_proposal': {
            'user': 'arcadia',
            'repo': 'taxi/infra/strongbox-conf-stable',
            'title': 'feat test_service: delete strongbox secdist config',
            'changes': [
                {
                    'filepath': 'secdist/test_service.tpl',
                    'state': 'deleting',
                    'data': '',
                },
            ],
            'base': 'trunk',
            'comment': 'delete Strongbox config',
        },
        'new_service_ticket': None,
        'merge_diff_job_id': 5,
    }
