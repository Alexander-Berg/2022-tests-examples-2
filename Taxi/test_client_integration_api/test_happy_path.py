async def test_integration_api(library_context, mockserver):
    url = '/yandex-int-api/v1/orders/commit'
    mocked_result = {'some': 'tome'}

    @mockserver.json_handler(url)
    def handle(request):
        assert request.headers['Content-Type'] == 'application/json'
        assert request.json == sent_json
        assert request.method == 'POST'
        return mocked_result

    sent_json = {'here': 'there'}
    result = await library_context.client_integration_api.order_commit(
        sent_json,
    )

    assert mocked_result == result.data
    assert handle.times_called == 1
