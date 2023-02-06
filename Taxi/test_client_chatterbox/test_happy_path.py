async def test_chatterbox(
        library_context, patch_aiohttp_session, response_mock, patch,
):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def get_auth_headers(*args, **kwargs):
        return {'tvm': 'xxx'}

    @patch_aiohttp_session('http://chatterbox.taxi.dev.yandex.net/v1/tasks')
    def post_tasks(method, url, json, headers, params):
        return response_mock()

    await library_context.client_chatterbox.tasks(1, 'a')

    assert post_tasks.calls == [
        {
            'method': 'post',
            'url': 'http://chatterbox.taxi.dev.yandex.net/v1/tasks',
            'json': {'external_id': 1, 'type': 'a'},
            'headers': {'Content-Type': 'application/json', 'tvm': 'xxx'},
            'params': None,
        },
    ]

    assert len(get_auth_headers.calls) == 1
