from aiohttp import web
import pytest


@pytest.mark.pgsql('clownductor', ['init_data.sql'])
@pytest.mark.parametrize(
    'params_input,params_expected',
    [
        (
            {
                'service_id': 1,
                'fqdn': 'zadmin-data.taxi.yandex.net',
                'datacenters': ['man', 'vla', 'sas'],
                'size': 'MICRO',
                'env': 'testing',
            },
            {
                'service_id': 1,
                'fqdn': 'zadmin-data.taxi.yandex.net',
                'datacenters': ['man', 'vla', 'sas'],
                'size': 'MICRO',
                'env': 'testing',
                'new_service_ticket': None,
                'network': '__DEFAULT_TEST__',
                'fqdn_suffix': None,
            },
        ),
        (
            {
                'service_id': 1,
                'fqdn': 'zadmin-data.taxi.yandex.net',
                'datacenters': ['man', 'vla', 'sas'],
                'size': 'MICRO',
                'env': 'stable',
            },
            {
                'service_id': 1,
                'fqdn': 'zadmin-data.taxi.yandex.net',
                'datacenters': ['man', 'vla', 'sas'],
                'size': 'MICRO',
                'env': 'stable',
                'new_service_ticket': None,
                'network': '__ELRUSSO_STABLE',
                'fqdn_suffix': None,
            },
        ),
    ],
)
async def test_add_balancers(
        web_app_client, mock_task_processor, params_input, params_expected,
):
    @mock_task_processor('/v1/jobs/start/')
    async def tp_handler(request):
        job_vars = request.json['job_vars']
        assert params_expected == job_vars
        return web.json_response({'job_id': 1})

    response = await web_app_client.post(
        '/v1/create_awacs_balancer/', json=params_input,
    )
    assert response.status == 200
    data = await response.json()
    assert data
    assert tp_handler.times_called == 1
