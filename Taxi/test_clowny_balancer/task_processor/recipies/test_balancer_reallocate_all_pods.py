import pytest


@pytest.mark.usefixtures('reallocate_balancer_pods_mocks')
async def test_recipe(load_yaml, task_processor, run_job_common):
    recipe = task_processor.load_recipe(
        load_yaml('BalancerReallocateAllPods.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={'awacs_namespace_id': 'ns1'}, initiator='clowny-balancer',
    )
    await run_job_common(job, sleep_is_expected=True)
    assert job.job_vars == {
        'awacs_namespace_id': 'ns1',
        'balancer_service_man': 'some-long-name_man',
        'balancer_service_sas': '',
        'balancer_service_vla': '',
        'man_reallocation_id': '123abc',
        'sas_reallocation_id': '',
        'vla_reallocation_id': '',
    }
