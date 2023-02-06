async def test_startrek(library_context, patch_aiohttp_session, response_mock):
    url = 'http://startrek/issues/TAXITOOLS-348'
    mocked_result = {'some': 'tome'}

    @patch_aiohttp_session(url)
    def patched(method, url, data, json, headers, params, timeout):
        return response_mock(json=mocked_result)

    result = await library_context.client_startrek.get_ticket('TAXITOOLS-348')

    assert result == mocked_result
    assert patched.calls == [
        {
            'method': 'get',
            'url': url,
            'data': None,
            'json': None,
            'headers': {'Authorization': 'OAuth secret', 'X-Org-Id': '0'},
            'timeout': 5,
            'params': None,
        },
    ]
