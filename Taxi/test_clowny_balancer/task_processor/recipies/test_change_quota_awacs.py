import pytest


@pytest.fixture(name='job_checker')
def _job_checker(task_processor, run_job_common):
    async def do_it(job):
        await run_job_common(job)
        assert job.job_vars == {
            'job_ids': [2],
            'namespace_ids': ['awacs-ns-1'],
            'new_quota_abc': 'abc-id',
            'service_id': 1,
            'user': 'karachevda',
        }

        jobs = list(task_processor.jobs.values())
        assert [x.id for x in jobs] == [1, 2]
        assert jobs[-1].job_vars == {
            'namespace_id': 'awacs-ns-1',
            'new_quota_abc': 'abc-id',
            'user': 'karachevda',
        }

    return do_it


async def test_change_quota_awacs(task_processor, load_yaml, job_checker):
    recipe = task_processor.load_recipe(
        load_yaml('ChangeQuotaAwacsNamespace.yaml')['data'],
    )
    task_processor.load_recipe(
        {
            'name': 'ChangeQuotaAwacsForBalancer',
            'provider_name': 'clowny-balancer',
            'job_vars': {},
            'stages': [],
        },
    )
    job = await recipe.start_job(
        job_vars={
            'new_quota_abc': 'abc-id',
            'service_id': 1,
            'user': 'karachevda',
        },
        initiator='clowny-balancer',
    )
    await job_checker(job)
