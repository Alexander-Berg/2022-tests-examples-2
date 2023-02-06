async def test_driver_protocol(
        library_context, patch_aiohttp_session, response_mock,
):
    url = 'http://driver-protocol.taxi.dev.yandex.net/service/chat/add'
    mocked_result = {'some': 'tome'}

    @patch_aiohttp_session(url)
    def service_chat_add(method, url, headers, params, data):
        return response_mock(json=mocked_result)

    result = await library_context.client_driver_protocol.service_chat_add(
        'my_db', {'push_data': 'this'},
    )

    assert result is None
    assert service_chat_add.calls == [
        {
            'method': 'post',
            'url': url,
            'data': {'push_data': 'this'},
            'headers': {'content-type': 'application/json'},
            'params': {'db': 'my_db'},
        },
    ]
