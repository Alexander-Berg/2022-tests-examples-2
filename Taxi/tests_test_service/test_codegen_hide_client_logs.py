#  ->  test-service       ->  _handler       ->  test-service    ->  test
async def test_x_taxi_query_log_mode_hide(taxi_test_service, mockserver):
    @mockserver.json_handler('/test-client/logging/x-taxi-query-log-mode')
    async def _handler(request):
        assert request.query == {'value': 'secret'}
        return mockserver.make_response()

    async with taxi_test_service.capture_logs() as capture:
        response = await taxi_test_service.get(
            '/logging/x-taxi-query-log-mode/check',
        )
        assert _handler.times_called == 1
        assert response.status_code == 200

    logs = capture.select(stopwatch_name='external')
    for log in logs:
        if 'x-taxi-query-log-mode' not in log['http_url']:
            continue
        assert 'value=' not in log['http_url']
        assert '(some query params were hidden)' in log['http_url']
