async def test_zen_dash(library_context, patch_aiohttp_session, response_mock):
    url = 'https://zen-dash.taxi.yandex.net/api/testing/autoreply'

    @patch_aiohttp_session(url)
    def patched(method, url, params, json):
        return response_mock()

    result = await library_context.client_zen_dash.autoreply({'data': 'data'})

    assert result is None
    assert patched.calls == [
        {
            'method': 'post',
            'url': url,
            'json': {'data': 'data'},
            'params': None,
        },
    ]
