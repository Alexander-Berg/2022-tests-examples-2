import pytest


@pytest.mark.parametrize(
    'include_history, include_actions, expected_params',
    [
        (True, False, {'include_history': 'true'}),
        (False, True, {'include_actions': 'true'}),
        (True, True, {'include_history': 'true', 'include_actions': 'true'}),
        (False, False, {}),
    ],
)
async def test_support_chat(
        library_context,
        patch_aiohttp_session,
        response_mock,
        include_history,
        include_actions,
        expected_params,
):
    url = 'http://support-chat.taxi.dev.yandex.net/v1/chat/1'
    mocked_result = {'some': 'tome'}

    @patch_aiohttp_session(url)
    def patched(method, url, data, json, headers, params):
        return response_mock(json=mocked_result)

    result = await library_context.client_support_chat.get_chat(1)
    await library_context.client_support_chat.get_chat(
        1, include_history=include_history, include_actions=include_actions,
    )

    assert result == mocked_result
    assert patched.calls == [
        {
            'method': 'get',
            'url': url,
            'json': None,
            'data': None,
            'headers': {},
            'params': {},
        },
        {
            'method': 'get',
            'url': url,
            'json': None,
            'data': None,
            'headers': {},
            'params': expected_params,
        },
    ]
