import socket


async def test_cc_enabled(taxi_test_service, testpoint):
    @testpoint('congestion-control')
    def tp_cc_enable(data):
        return {'force-rps-limit': 0}

    @testpoint('congestion-control-apply')
    def tp_cc_apply(data):
        return {}

    # wait until server obtains the new limit, up to 1 second
    await taxi_test_service.enable_testpoints()
    await tp_cc_enable.wait_call()
    await tp_cc_apply.wait_call()

    # /ping is not throttled
    response = await taxi_test_service.get('ping')
    assert response.status_code == 200

    # Random non-ping handler
    response = await taxi_test_service.get('echo-no-body')

    assert response.status_code == 429
    assert (
        response.headers['X-YaTaxi-Ratelimit-Reason'] == 'congestion-control'
    )
    hostname = socket.gethostname()
    assert response.headers['X-YaTaxi-Ratelimited-By'] == hostname

    # A hack to disable CC for other tests
    @testpoint('congestion-control')
    def tp_cc_disable(data):
        return {}

    await tp_cc_disable.wait_call()
    await tp_cc_apply.wait_call()
