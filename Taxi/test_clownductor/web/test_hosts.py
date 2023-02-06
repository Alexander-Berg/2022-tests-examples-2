import pytest


@pytest.mark.pgsql('clownductor')
@pytest.mark.parametrize(
    'handler, fqdn, dom0, datacenter, branch_id, result',
    [
        ('/api/hosts', 'fqdn1', None, None, None, []),
        ('/api/hosts', None, 'dom0_1', None, None, []),
        ('/api/hosts', None, None, 'myt', None, []),
        ('/api/hosts', None, None, None, 1, []),
        ('/v1/hosts/', 'fqdn1', None, None, None, []),
    ],
)
async def test_get_jobs_by_id(
        web_app_client, handler, fqdn, dom0, datacenter, branch_id, result,
):
    params = {
        'fqdn': fqdn,
        'dom0': dom0,
        'dc': datacenter,
        'branch_id': branch_id,
    }
    response = await web_app_client.get(
        handler,
        params={key: params[key] for key in params if params[key] is not None},
    )
    assert response.status == 200
    data = await response.json()
    assert sorted(result) == sorted(data)


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'enable_fqdn_actualize': True})
@pytest.mark.parametrize(
    'fqdn, result',
    [
        (
            'qqbyrftajycoh7q2.vla.yp-c.yandex.net',
            [
                {
                    'branch_id': 2,
                    'branch_name': 'testing_branch',
                    'datacenter': 'vla',
                    'name': 'qqbyrftajycoh7q2.vla.yp-c.yandex.net',
                    'direct_link': 'test-service-1-direct-testing',
                    'project_id': 1,
                    'project_name': 'test_project',
                    'service_id': 1,
                    'service_name': 'test-service',
                },
            ],
        ),
        ('test-service-1.yp-c.yandex.net', []),
        (
            'test-service-1.vla.yp-c.yandex.net',
            [
                {
                    'branch_id': 1,
                    'branch_name': 'stable_branch',
                    'datacenter': 'vla',
                    'name': 'test-service-1.vla.yp-c.yandex.net',
                    'direct_link': 'test-service-1-direct',
                    'project_id': 1,
                    'project_name': 'test_project',
                    'service_id': 1,
                    'service_name': 'test-service',
                },
            ],
        ),
    ],
)
@pytest.mark.parametrize('handler', ['/api/hosts', '/v1/hosts/'])
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_actualize_hosts(
        web_app_client, fqdn, result, handler, mockserver,
):
    @mockserver.json_handler('/yp-api/ObjectService/SelectObjects')
    def select_objects(request):
        assert request.json == {
            'object_type': 'pod',
            'filter': {
                'query': (
                    '[/status/dns/persistent_fqdn]='
                    '"qqbyrftajycoh7q2.vla.yp-c.yandex.net"'
                ),
            },
            'selector': {'paths': ['/labels']},
        }
        return {
            'results': [
                {
                    'values': [
                        {
                            'deploy_engine': 'YP_LITE',
                            'hq_synced_eviction_time': '1595422503841108',
                            'nanny_service_id': (
                                'test-service-1-direct-testing'
                            ),
                            'nanny_version': (
                                '002ae036-58fa-4ecb-83f8-fbf27bed39f6'
                            ),
                        },
                    ],
                },
            ],
            'timestamp': 1721336799617353876,
        }

    response = await web_app_client.get(handler, params={'fqdn': fqdn})
    assert response.status == 200
    data = await response.json()
    assert result == data
    if fqdn == 'qqbyrftajycoh7q2.vla.yp-c.yandex.net':
        assert select_objects.times_called == 1
    else:
        assert not select_objects.times_called


@pytest.mark.pgsql('clownductor')
@pytest.mark.parametrize('handler', ['/api/hosts/', '/v1/hosts/'])
async def test_get_hosts_missing_param(web_app_client, handler):
    response = await web_app_client.get(handler)
    assert response.status == 400
