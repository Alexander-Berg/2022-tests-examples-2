async def test_mds(library_context, mockserver, response_mock):
    path = '/mds/delete-taxi/some-id'

    @mockserver.json_handler(path)
    def _request(request):
        return mockserver.make_response()

    await library_context.client_mds.remove('some-id')

    request_args = (await _request.wait_call())['request']
    assert request_args.path == path
    assert request_args.method == 'POST'
    assert request_args.headers['Authorization'] == 'Basic '
    assert request_args.headers['Content-Type'] == 'application/octet-stream'
