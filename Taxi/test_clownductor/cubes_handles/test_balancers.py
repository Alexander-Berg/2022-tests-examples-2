import pytest


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'delete_balancer_alias': True})
@pytest.mark.parametrize(
    'file_name', ['DeleteAlias.json', 'DeleteTestingAlias.json'],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_task_processor_delete_alias(
        load_json,
        mock_clowny_balancer,
        call_cube_handle,
        file_name,
        tp_start_job_mock,
        assert_meta_jobs,
        assert_tp_meta_jobs,
):
    json_data = load_json(file_name)

    @mock_clowny_balancer('/v1/entry-points/fqdn/search/')
    def fqdn_search(request):
        input_data = json_data['data_request']['input_data']
        assert int(request.query['service_id']) == input_data['service_id']
        assert request.query['env'] == 'stable'
        assert request.query.keys() == {'service_id', 'env'}
        return {'fqdns': ['test_service.taxi.yandex.net']}

    tp_mock = tp_start_job_mock()
    cube_name = 'MetaDeleteBalancerAlias'
    await call_cube_handle(cube_name, json_data)
    await assert_meta_jobs(json_data)
    await assert_tp_meta_jobs(json_data, tp_mock)
    assert fqdn_search.times_called == json_data['fqdn_times_called']


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_change_quota_balancers(
        call_cube_handle, task_processor, get_job_from_internal,
):
    task_processor.load_recipe(
        {
            'name': 'ChangeQuotaAwacsNamespace',
            'stages': [],
            'job_vars': {},
            'provider_name': 'clowny-balancer',
        },
    )
    await call_cube_handle(
        'MetaChangeQuotaBalancers',
        {
            'content_expected': {
                'payload': {'job_id': 2},
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
    job = await get_job_from_internal(2)
    assert job.job_vars == {
        'new_quota_abc': 'abc-id',
        'service_id': 1,
        'st_ticket': None,
        'user': 'karachevda',
    }
