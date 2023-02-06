import pytest


@pytest.mark.parametrize(
    'request_id, exp_resp_code, exp_resp',
    [
        (
            1,
            200,
            {
                'alerting_config': {
                    'juggler_namespace': (
                        'awacs.stq-agent-taxi-critical-taxi-yandex-net'
                    ),
                },
            },
        ),
        (
            2,
            404,
            {
                'code': 'NOT_FOUND',
                'message': 'awacs_namespace=bbb.net not found in awacs',
            },
        ),
        (
            3,
            404,
            {'code': 'NOT_FOUND', 'message': 'namespace id=3 not found in db'},
        ),
    ],
)
async def test_list(
        mockserver,
        taxi_clowny_balancer_web,
        load_json,
        request_id,
        exp_resp_code,
        exp_resp,
):
    @mockserver.json_handler('/client-awacs/api/GetNamespaceAlertingConfig/')
    def _mock_get_alerting_config(request):
        if request.json['namespaceId'] == 'aaa.net':
            return load_json('alerting_config_resp.json')

        return mockserver.make_response(status=404)

    response = await taxi_clowny_balancer_web.get(
        '/v1/namespaces/item/', params={'id': request_id},
    )

    assert response.status == exp_resp_code
    assert await response.json() == exp_resp
