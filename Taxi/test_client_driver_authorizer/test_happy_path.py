async def test_driver_authorizer(
        library_context, patch_aiohttp_session, response_mock,
):
    url = 'http://driver-authorizer.taxi.yandex.net'

    check_result = {'x': 'y'}
    url += '/driver/sessions/check'

    @patch_aiohttp_session(url)
    def check(method, url, json, headers, params):
        return response_mock(json=check_result)

    result = (
        await library_context.client_driver_authorizer.check_driver_sessions(
            token='token', client_id='1', park_id='2',
        )
    )

    assert result == check_result
    assert check.calls == [
        {
            'headers': {'X-Driver-Session': 'token'},
            'method': 'post',
            'url': url,
            'params': None,
            'json': {'client_id': '1', 'park_id': '2', 'ttl': 1000},
        },
    ]
