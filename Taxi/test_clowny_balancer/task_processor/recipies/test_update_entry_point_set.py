async def test_recipe(
        load_yaml, task_processor, run_job_common, mockserver, awacs_mock,
):
    inst_awacs_mock = awacs_mock(load_yaml('awacs_mock.yaml'))
    recipe = task_processor.load_recipe(
        load_yaml('UpdateEntryPointSet.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'clown_service_id': 1,
            'clown_branch_id': 2,
            'active_regions': ['SAS'],
        },
        initiator='clowny-balancer',
    )
    await run_job_common(job)
    assert job.job_vars == {
        'active_regions': ['SAS'],
        'awacs_backend_id': 'some',
        'awacs_namespace_id': 'awacs-ns-1',
        'clown_branch_id': 2,
        'clown_service_id': 1,
    }
    mock_update = inst_awacs_mock.mocks['UpdateBackend']
    assert mock_update.times_called == 1
