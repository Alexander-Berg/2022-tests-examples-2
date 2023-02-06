import pytest


@pytest.mark.parametrize('env, status', [('unstable', 200), ('testing', 400)])
async def test_create_cname(taxi_clowny_balancer_web, env, status):
    response = await taxi_clowny_balancer_web.post(
        '/balancers/v1/create-alias/',
        json={
            'fqdn': 'some-service.taxi.dev.yandex.net',
            'ticket': 'TAXIPLATFORM-1',
            'branch': {
                'project_id': 1,
                'service_id': 1,
                'id': 1,
                'full_name': 'taxi_some-service_unstable',
                'env': env,
            },
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == status
