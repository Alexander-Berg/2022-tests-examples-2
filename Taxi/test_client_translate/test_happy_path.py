async def test_translate(
        library_context, patch_aiohttp_session, response_mock,
):
    url = 'http://translate.yandex.net/api/v1/tr.json/detect'
    mocked_result = {'some': 'tome'}

    @patch_aiohttp_session(url)
    def patched(method, url, params, json):
        return response_mock(json=mocked_result)

    result = await library_context.client_translate.detect_language('abacaba')

    assert result == mocked_result
    assert patched.calls == [
        {
            'method': 'get',
            'url': url,
            'json': None,
            'params': {'text': 'abacaba', 'srv': 'taxi'},
        },
    ]
