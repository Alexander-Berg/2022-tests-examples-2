async def test_wiki(library_context, patch_aiohttp_session, response_mock):
    url = 'https://wiki-api.test.yandex-team.ru/_api/frontend/page_url'

    @patch_aiohttp_session(url)
    def patched(method, url, headers, params, json, **kwargs):
        return response_mock()

    _ = await library_context.client_wiki.publish_page(
        'page_url', 'title', 'body',
    )

    expected_calls = [
        {
            'method': 'post',
            'url': url,
            'headers': {'Authorization': 'OAuth 123-456-6789'},
            'json': {'body': 'body', 'title': 'title'},
            'params': None,
        },
    ]

    for patched_call, expected_call in zip(patched.calls, expected_calls):
        for key, expected_value in expected_call.items():
            assert patched_call[key] == expected_value
