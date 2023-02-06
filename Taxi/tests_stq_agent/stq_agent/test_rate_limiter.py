async def test_basic_rate_limiter_proxy(
        taxi_stq_agent, load_yaml, mockserver, testpoint,
):
    @testpoint('rate_limiter_proxy_transport')
    def _change_transport(request):
        return {'transport': 'tcp'}

    @mockserver.json_handler('/limits')
    def rate_limiter_proxy(request):
        rate_limiter_proxy.limits = request.json

    # initial call when stq-agent starts
    expected_limits = {
        '/queues/api/add/queue1': {
            'service1': {'rate': 10, 'unit': 1},
            'service2': {'rate': 5, 'unit': 1},
        },
        '/queues/api/add/queue2': {
            'service1': {'rate': 5, 'unit': 1},
            'service2': {'rate': 7, 'unit': 1},
        },
    }

    await taxi_stq_agent.run_periodic_task('rate_limit_sending_task')
    await rate_limiter_proxy.wait_call()
    assert rate_limiter_proxy.limits == expected_limits
