# All tests should start with `async def test_`
# Params:
# * `taxi_SERVICE-NAME` to do requests to the service that we wish to test
# * `mockserver` to mock responses of other services
async def test_sample_base(taxi_userver_sample, mockserver):
    # Moking handle `/autogen/empty` of service `userver-sample`
    @mockserver.json_handler('/userver-sample/autogen/empty')
    def _handler(request):
        # `return mockserver.make_response()` does the same as:
        return mockserver.make_response(
            json={}, headers={}, content_type='application/json',
        )

    # Do a request to `userver-sample` handle `/autogen/mockserver/test`. That
    # handle should go to the handle `/autogen/empty` of service
    # `userver-sample` (which is mocked).
    response = await taxi_userver_sample.get(
        'autogen/mockserver/test',
        json={'Sample': 'JSON'},
        headers={'Foo': 'bar'},
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
    assert _handler.times_called == 1  # make sure that _handler was called
