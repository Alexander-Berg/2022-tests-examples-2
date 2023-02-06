import aiohttp


async def test_zendesk(library_context, patch_aiohttp_session, response_mock):
    url = '/api/v2/tickets/111.json'

    @patch_aiohttp_session(url)
    def patched(method, url, params, data, headers, auth, timeout):
        return response_mock()

    result = await library_context.client_zendesk.get_ticket(111)

    assert result is None
    assert patched.calls == [
        {
            'method': 'get',
            'url': url,
            'params': None,
            'data': None,
            'headers': {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            'auth': aiohttp.BasicAuth('', ''),
            'timeout': 20,
        },
    ]
