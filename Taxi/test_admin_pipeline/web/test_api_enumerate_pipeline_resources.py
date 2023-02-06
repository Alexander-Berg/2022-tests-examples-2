import pytest


@pytest.mark.parametrize(
    'body',
    [
        [],
        [{'name': 'sample_resource'}],
        [{'name': 'sample_resource1'}, {'name': 'sample_resource2'}],
        [
            {
                'name': 'sample_resource',
                'params_schema': {
                    'type': 'object',
                    'properties': {'arg1': {'type': 'integer'}},
                },
                'instance_schema': {
                    'type': 'object',
                    'properties': {'p1': {'type': 'boolean'}},
                },
            },
        ],
    ],
)
async def test_enumerate_resources(web_app_client, mockserver, body):
    consumer = 'new-consumer'
    service = 'new-service'
    await web_app_client.post(
        f'/{consumer}/register/',
        json={
            'service_balancer_hostname': service,
            'service_tvm_name': service,
        },
    )

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/resource/enumerate')
    def _taxi_resource_enumerate(request):
        return body

    response = await web_app_client.post(
        '/v2/pipeline/resource/enumerate', params={'consumer': consumer},
    )
    assert response.status == 200
    assert await response.json() == body
