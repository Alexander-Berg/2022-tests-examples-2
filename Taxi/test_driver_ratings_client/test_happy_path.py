async def test_driver_ratings_retrieve(
        library_context, mockserver, response_mock,
):
    url = '/driver-ratings/v1/driver/ratings/retrieve'
    mocked_result = {'some': 'retrieve'}

    @mockserver.json_handler(url)
    def driver_ratings_by_licenses(request):
        return mocked_result

    result = await library_context.driver_ratings_client.retrieve(
        ['LICENSE'], None,
    )
    assert mocked_result == result
    assert driver_ratings_by_licenses.times_called == 1
    call = driver_ratings_by_licenses.next_call()
    method = call['request'].method
    headers = call['request'].headers
    assert method == 'POST'
    assert headers['content-type'] == 'application/json'
