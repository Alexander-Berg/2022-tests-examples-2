import pytest


SERVICE_NAME = 'userver@userver-sample'
FALLBACK_NAME = 'handler.userver-sample./autogen/fallbacks-get.fallback'
CLIENT_QOS = {'__default__': {'attempts': 5, 'timeout-ms': 100}}


def _parse_metrics(json):
    success_name = 'handler.userver-sample./autogen/fallbacks-get.success'
    error_name = 'handler.userver-sample./autogen/fallbacks-get.error'

    value_success = 0
    value_error = 0

    if json['service'] == SERVICE_NAME:
        for metric in json['metrics']:
            name = metric['name']
            value = metric['value']
            if name == success_name:
                value_success += value
            elif metric['name'] == error_name:
                value_error += value

    return value_success, value_error


@pytest.mark.config(USERVER_SAMPLE_CLIENT_QOS=CLIENT_QOS)
async def test_retries_fallback_disabled(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/autogen/fallbacks')
    def _handler(request):
        raise mockserver.NetworkError()

    response = await taxi_userver_sample.get('autogen/fallbacks')
    assert response.status_code == 500
    assert _handler.times_called == 5


@pytest.mark.config(USERVER_SAMPLE_CLIENT_QOS=CLIENT_QOS)
async def test_retries_fallback_enabled(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/statistics/v1/service/health')
    def _health(request):
        if request.args['service'] == SERVICE_NAME:
            return mockserver.make_response(
                json={'fallbacks': [FALLBACK_NAME]},
            )
        return mockserver.make_response(json={'fallbacks': []})

    @mockserver.json_handler('/userver-sample/autogen/fallbacks')
    def _handler(request):
        raise mockserver.NetworkError()

    await taxi_userver_sample.invalidate_caches(clean_update=False)

    response = await taxi_userver_sample.get('autogen/fallbacks')
    assert response.status_code == 500
    assert _handler.times_called == 1


@pytest.mark.config(USERVER_SAMPLE_CLIENT_QOS=CLIENT_QOS)
async def test_store_error_metrics(taxi_userver_sample, mockserver):
    stored_success = 0
    stored_error = 0

    @mockserver.json_handler('/statistics/v1/metrics/store')
    def _store(request):
        parsed_success, parsed_error = _parse_metrics(request.json)

        nonlocal stored_success
        stored_success += parsed_success

        nonlocal stored_error
        stored_error += parsed_error

        return mockserver.make_response(json={})

    @mockserver.json_handler('/userver-sample/autogen/fallbacks')
    def _handler(request):
        raise mockserver.NetworkError()

    response = await taxi_userver_sample.get('autogen/fallbacks')
    assert response.status_code == 500
    assert _handler.times_called == 5

    await taxi_userver_sample.invalidate_caches(clean_update=False)

    assert stored_success == 0
    assert stored_error > 0


@pytest.mark.config(USERVER_SAMPLE_CLIENT_QOS=CLIENT_QOS)
async def test_store_success_metrics(taxi_userver_sample, mockserver):
    stored_success = 0
    stored_error = 0

    @mockserver.json_handler('/statistics/v1/metrics/store')
    def _store(request):
        parsed_success, parsed_error = _parse_metrics(request.json)

        nonlocal stored_success
        stored_success += parsed_success

        nonlocal stored_error
        stored_error += parsed_error

        return mockserver.make_response(json={})

    @mockserver.json_handler('/userver-sample/autogen/fallbacks')
    def _handler(request):
        return mockserver.make_response(json={})

    response = await taxi_userver_sample.get('autogen/fallbacks')
    assert response.status_code == 200
    assert _handler.times_called == 1

    await taxi_userver_sample.invalidate_caches(clean_update=False)

    assert stored_success > 0
    assert stored_error == 0
