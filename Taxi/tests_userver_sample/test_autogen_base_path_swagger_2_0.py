import pytest


async def test_client_path(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/base-path/swagger-2-0')
    def _handler(request):
        return mockserver.make_response(json={'msg': 'OK'})

    response = await taxi_userver_sample.get('autogen/base-path/swagger-2-0')
    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'msg': 'OK'}


@pytest.mark.config(
    USERVER_SAMPLE_CLIENT_QOS={
        '__default__': {'timeout-ms': 30000, 'attempts': 2},
        '/userver-sample/autogen/base-path/swagger-2-0': {
            'timeout-ms': 30000,
            'attempts': 5,
        },
    },
)
async def test_client_path_qos_name(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/base-path/swagger-2-0')
    def _handler(request):
        return mockserver.make_response(status=501)

    response = await taxi_userver_sample.get('autogen/base-path/swagger-2-0')
    assert response.status_code == 500

    # assert that codegen client uses the correct QOS' config entry
    assert _handler.times_called == 5
