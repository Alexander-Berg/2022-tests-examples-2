import pytest


RECIPE_NAME = 'RemoveEntryPointWrapper'


async def _make_step(job):
    task, _ = await job.step()
    assert task
    assert task.status.is_success


@pytest.mark.parametrize(
    'entry_point_id, started_job_name, wrapper_job_vars, wrapped_job_vars',
    [
        (
            1,
            'RemoveAwacsBalancer',
            {
                'awacs_namespace_id': 'ns-1',
                'entry_point_id': 1,
                'namespace_can_be_deleted': True,
                'remove_job_id': 2,
            },
            {'namespace_id': 1},
        ),
        (
            2,
            'EntryPointRemove',
            {
                'awacs_namespace_id': 'ns-2',
                'entry_point_id': 2,
                'namespace_can_be_deleted': False,
                'remove_job_id': 2,
            },
            {'entry_point_id': 2, 'lock_name': 'service-fqdn-2.net:default'},
        ),
    ],
)
async def test_recipe(
        load_yaml,
        task_processor,
        awacs_mock,
        entry_point_id,
        started_job_name,
        wrapper_job_vars,
        wrapped_job_vars,
):
    awacs_mock(load_yaml('awacs_mock.yaml'))
    task_processor.load_recipe(load_yaml('RemoveAwacsBalancer.yaml')['data'])
    task_processor.load_recipe(load_yaml('EntryPointRemove.yaml')['data'])
    recipe = task_processor.load_recipe(
        load_yaml('RemoveEntryPointWrapper.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={'entry_point_id': entry_point_id},
        initiator='clowny-balancer',
    )
    # call InternalFindModelsToRemove
    await _make_step(job)
    # call AwacsNamespaceCanBeDeleted
    await _make_step(job)
    # call MetaRunRemoveJob
    await _make_step(job)

    running_jobs = {x.recipe.name: x for x in task_processor.jobs.values()}
    assert running_jobs.keys() == {RECIPE_NAME, started_job_name}

    wrapper_job = task_processor.job(running_jobs[RECIPE_NAME].id)
    assert wrapper_job.job_vars == wrapper_job_vars

    wrapped_job = task_processor.job(running_jobs[started_job_name].id)
    assert wrapped_job.job_vars == wrapped_job_vars
