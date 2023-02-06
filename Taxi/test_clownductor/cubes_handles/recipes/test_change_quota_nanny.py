import pytest


def _assert_nanny_mock(mock):
    expected_paths = {
        (
            'GET',
            '/client-nanny/v2/services/test_service_pre_stable/info_attrs/',
        ),
        (
            'PUT',
            '/client-nanny/v2/services/test_service_pre_stable/info_attrs/',
        ),
        ('GET', '/client-nanny/v2/services/test_service_stable/info_attrs/'),
        ('PUT', '/client-nanny/v2/services/test_service_stable/info_attrs/'),
        ('GET', '/client-nanny/v2/services/test_service_testing/info_attrs/'),
        ('PUT', '/client-nanny/v2/services/test_service_testing/info_attrs/'),
    }

    assert mock.handler.times_called == len(expected_paths)
    while mock.handler.has_calls:
        call = mock.handler.next_call()['request']
        expected_paths.remove((call.method, call.path))
    assert not expected_paths


def _assert_nanny_yp_mock(mock):
    expected_paths = set()
    for path in [
            '/client-nanny-yp/api/yplite/pod-sets/GetPodSet/',
            '/client-nanny-yp/api/yplite/pod-sets/UpdatePodSet/',
    ]:
        for nanny_name in [
                'test_service_pre_stable',
                'test_service_stable',
                'test_service_testing',
        ]:
            for region in ['MAN', 'VLA', 'SAS']:
                expected_paths.add((path, nanny_name, region))

    assert mock.times_called == len(expected_paths)
    while mock.has_calls:
        call = mock.next_call()['request']
        expected_paths.remove(
            (call.path, call.json['serviceId'], call.json['cluster']),
        )
    assert not expected_paths


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_change_quota_nanny(
        load_yaml,
        task_processor,
        run_job_common,
        get_job_from_internal,
        nanny_mockserver,
        nanny_yp_mockserver,
        abc_mockserver,
        cookie_monster_mockserver,
        abc_nonofficial_mockserver,
):
    cookie_monster_mockserver()
    abc_nonoff_mock = abc_nonofficial_mockserver()
    nanny_yp_mock = nanny_yp_mockserver()
    abc_mock = abc_mockserver(services=True)
    recipe = task_processor.load_recipe(
        load_yaml('recipes/ChangeQuotaNanny.yaml')['data'],
    )
    task_processor.load_recipe(
        load_yaml('recipes/ChangeQuotaOneNanny.yaml')['data'],
    )
    task_processor.load_recipe(
        {
            'name': 'ChangeQuotaAwacsNamespace',
            'stages': [],
            'job_vars': {},
            'provider_name': 'clowny-balancer',
        },
    )

    async def _check_second_job(task):
        if task.cube.name == 'MetaChangeServiceQuotaNanny':
            job_ids = task.payload['job_ids']
            assert job_ids == [1, 2, 3]
            internal_jobs = [
                await get_job_from_internal(job_id) for job_id in job_ids
            ]
            for internal_job in internal_jobs:
                await run_job_common(internal_job)
        elif task.cube.name == 'MetaChangeQuotaBalancers':
            job_id = task.payload['job_id']
            assert job_id == 4
            internal_job = await get_job_from_internal(job_id)
            await run_job_common(internal_job)
        else:
            return

    job = await recipe.start_job(
        job_vars={
            'service_id': 1,
            'new_quota_abc': 'abc-new',
            'st_ticket': None,
            'project_id': 1,
            'user': 'karachevda',
            'service_abc': 'abc-slug',
        },
        initiator='clownductor',
    )
    await run_job_common(job, _check_second_job)
    assert abc_mock.times_called == 8
    assert abc_nonoff_mock.times_called == 2
    _assert_nanny_yp_mock(nanny_yp_mock)
    _assert_nanny_mock(nanny_mockserver)

    assert job.job_vars == {
        'job_id': 4,
        'job_ids': [1, 2, 3],
        'new_quota_abc': 'abc-new',
        'project_id': 1,
        'service_id': 1,
        'st_ticket': None,
        'user': 'karachevda',
        'move_id': 11468,
        'service_abc': 'abc-slug',
    }
