import datetime as dt


async def test_simple(
        taxi_dorblu_agent_sidecar,
        mockserver,
        testpoint,
        mocked_time,
        start_dorblu_agent,
        fill_default_log_format,
        fill_default_access_log,
        request_agent,
        reset_agent_metrics,
        load_json_message,
):
    await start_dorblu_agent()

    @testpoint('aggregator_request_completed')
    def _aggregator_request_completed(data):
        pass

    await taxi_dorblu_agent_sidecar.enable_testpoints()

    fill_default_log_format('log_format.conf')

    mocked_time.set(dt.datetime(2021, 9, 17, 13, 13))
    await taxi_dorblu_agent_sidecar.invalidate_caches()
    fill_default_access_log('empty_access.log')
    await taxi_dorblu_agent_sidecar.run_periodic_task('logfile-watcher')

    mocked_time.set(dt.datetime(2021, 9, 17, 13, 14))
    await taxi_dorblu_agent_sidecar.invalidate_caches()
    fill_default_access_log('simple_nginx_access.log')
    await taxi_dorblu_agent_sidecar.run_periodic_task('logfile-watcher')

    @mockserver.json_handler('/juggler/events')
    def _juggler_agent_mock(request):
        return {
            'events': [{'code': 200}],
            'accepted_events': 777,
            'success': True,
        }

    @mockserver.json_handler('/solomon-agent/dorblu_agent')
    def _solomon_agent_mock(request):
        return mockserver.make_response(status=200)

    mocked_time.set(dt.datetime(2021, 9, 17, 13, 14, 10))
    await taxi_dorblu_agent_sidecar.invalidate_caches()
    await request_agent(load_json_message('simple_aggregator_request.json'))
    await _aggregator_request_completed.wait_call()

    mocked_time.set(dt.datetime(2021, 9, 17, 13, 14, 43))
    await taxi_dorblu_agent_sidecar.invalidate_caches()
    response = await taxi_dorblu_agent_sidecar.get('/stats')

    assert response.status == 200
    assert response.json() == {'uptime': 33, 'iterations': 1}
