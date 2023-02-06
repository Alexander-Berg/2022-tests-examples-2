async def test_tracker(library_context, mockserver):
    url = '/tracker-api/service/driver-categories'
    mocked_result = {'some': 'tome'}

    response_json = None

    @mockserver.json_handler(url)
    async def _mocked_response(request):
        nonlocal response_json
        assert request.method == 'POST'
        assert str(request.url).endswith(url)
        response_json = request.json
        return mocked_result

    await library_context.client_tracker.driver_categories(1, 2)

    assert response_json == {'driver_id': 1, 'point': 2}
