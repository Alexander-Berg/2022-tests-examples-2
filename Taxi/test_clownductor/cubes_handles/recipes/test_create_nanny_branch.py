import pytest


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.usefixtures(
    'mock_internal_tp', 'create_file_change_proposal', 'create_branch_fixture',
)
@pytest.mark.features_on('use_new_juggler_merging_flow')
async def test_recipe_create_nanny_branch(
        task_processor, strongbox_get_groups, run_job_with_meta, load_json,
):
    job = await task_processor.start_job(
        job_vars=load_json('job_vars.json'),
        initiator='clownductor',
        name='CreateNannyBranch',
        idempotency_token='token-228',
    )
    await run_job_with_meta(job)
    assert job.job_vars == load_json('expected_job_vars.json')
    assert strongbox_get_groups.times_called == 1
