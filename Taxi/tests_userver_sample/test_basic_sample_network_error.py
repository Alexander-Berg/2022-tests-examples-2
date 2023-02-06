# Emulating Network error
async def test_sample_network_error(taxi_userver_sample, mockserver):
    # Moking handle `/autogen/empty` of service `userver-sample`
    @mockserver.json_handler('/userver-sample/autogen/empty')
    def _handler(request):
        raise mockserver.NetworkError()

    # Do a request to `userver-sample` handle `/autogen/mockserver/test`. That
    # handle should go to the handle `/autogen/empty` of service
    # `userver-sample` (which is mocked).
    response = await taxi_userver_sample.get('autogen/mockserver/test')
    assert response.status_code == 200
    assert _handler.times_called >= 1  # make sure that _handler was called
