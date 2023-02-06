import pytest


@pytest.mark.servicetest
async def test_deploy_callback(driver_route_watcher_ng_adv):
    drw = driver_route_watcher_ng_adv

    body = {
        'meta': {
            'service_name': 'superservice',
            'environment': 'testing',
            'hosts': ['aaa.yandex.net', 'bbb.yandex.net'],
            'direct_name': 'ccc.sas-01.yandex.net',
            'cluster_type': 'cluster-type',
            'docker_image': '0123456789abcdef',
            'changelog': 'all errors are fixed, this is aperfect service now',
        },
        'links': {
            'nanny': 'nanny.dsadsadsa.yandex.net',
            'grafana': 'grafana.yandex-team.ru/superservice',
            'golovan': 'golovan.yandex-team.ru/taxi_superservice_stable',
            'kibana': 'kibana.tiri-piri.yandex.net',
            'service_deploy': 'fdsafdsa.deploy.yandex.net',
        },
    }
    headers = {'X-Idempotency-Token': 'super-token'}
    response = await drw.post('deploy-callback', json=body, headers=headers)
    assert response.status_code == 200
