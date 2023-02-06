import pytest


@pytest.fixture(name='job_checker')
def _job_checker(task_processor, run_job_common):
    async def do_it(job):
        await run_job_common(job)
        assert job.job_vars == {
            'job_ids': [2, 3],
            'namespace_id': 'awacs-ns-1',
            'nanny_services': ['some-long-name_vla', 'some-long-name_man'],
            'new_quota_abc': 'abc-id',
            'user': 'karachevda',
        }

        jobs = list(task_processor.jobs.values())
        assert [x.id for x in jobs] == [1, 2, 3]
        assert jobs[-1].job_vars == {
            'nanny_name': 'some-long-name_man',
            'new_quota_abc': 'abc-id',
            'regions': ['man', 'vla', 'sas'],
        }
        assert jobs[-2].job_vars == {
            'nanny_name': 'some-long-name_vla',
            'new_quota_abc': 'abc-id',
            'regions': ['man', 'vla', 'sas'],
        }

    return do_it


async def test_change_quota_awacs_for_balancer(
        task_processor, load_yaml, job_checker, mockserver, abc_mockserver,
):
    abc_mock = abc_mockserver(services=True)

    @mockserver.json_handler('/client-awacs/api/ListBalancers/')
    def _list_balancers_handler(request):
        return {
            'balancers': [
                {
                    'meta': {
                        'id': 'existing_man',
                        'location': {
                            'yp_cluster': 'MAN',
                            'type': 'YP_CLUSTER',
                        },
                    },
                    'spec': {
                        'configTransport': {
                            'nannyStaticFile': {
                                'serviceId': 'some-long-name_man',
                            },
                        },
                    },
                },
                {
                    'meta': {
                        'id': 'existing_man',
                        'location': {
                            'yp_cluster': 'VLA',
                            'type': 'YP_CLUSTER',
                        },
                    },
                    'spec': {
                        'configTransport': {
                            'nannyStaticFile': {
                                'serviceId': 'some-long-name_vla',
                            },
                        },
                    },
                },
            ],
        }

    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_namespace_handler(request):
        assert request.method == 'POST'
        return {
            'namespace': {
                'meta': {'abcServiceId': 10, 'id': request.json['id']},
            },
        }

    @mockserver.json_handler('/client-awacs/api/UpdateNamespace/')
    def _update_namespace_handler(request):
        assert request.method == 'POST'
        return {}

    recipe = task_processor.load_recipe(
        load_yaml('ChangeQuotaAwacsForBalancer.yaml')['data'],
    )
    task_processor.load_recipe(
        {
            'name': 'ChangeQuotaOneNanny',
            'provider_name': 'clownductor',
            'job_vars': {},
            'stages': [],
        },
    )
    job = await recipe.start_job(
        job_vars={
            'namespace_id': 'awacs-ns-1',
            'new_quota_abc': 'abc-id',
            'user': 'karachevda',
        },
        initiator='clowny-balancer',
    )
    await job_checker(job)
    assert _list_balancers_handler.times_called == 1
    assert _update_namespace_handler.times_called == 1
    assert _get_namespace_handler.times_called == 1
    assert abc_mock.times_called == 1
    assert (
        _update_namespace_handler.next_call()['request'].json['meta'][
            'abcServiceId'
        ]
        == 3155
    )
