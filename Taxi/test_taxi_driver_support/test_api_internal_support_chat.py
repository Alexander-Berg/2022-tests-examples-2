import pytest

from taxi import discovery


@pytest.mark.now('2019-11-19T12:00:00+00:00')
@pytest.mark.parametrize(
    'params, status_code, support_info_response, expected_result',
    [
        (
            {'udid': '5ddba5a0772ddd3f966cac78'},
            200,
            {
                'chats': [
                    {
                        'id': '5bcdb13084b5976d23aa01bb',
                        'metadata': {
                            'new_messages': 3,
                            'updated': '2019-11-19T10:00:00+0000',
                        },
                    },
                ],
            },
            {'new_messages_count': 3, 'updated': '2019-11-19T10:00:00+0000'},
        ),
        ({}, 400, {}, None),
        (
            {'udid': '5ddba5a0772ddd3f966cac78'},
            200,
            {'chats': []},
            {'new_messages_count': 0, 'updated': '2019-11-19T12:00:00+0000'},
        ),
        ({'udid': 'not_object_id'}, 400, {}, None),
    ],
)
async def test_get_new_messages_count(
        taxi_driver_support_client,
        patch_aiohttp_session,
        response_mock,
        params,
        status_code,
        support_info_response,
        expected_result,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def _dummy_request(method, url, **kwargs):
        assert method == 'post'
        assert url == 'http://support-chat.taxi.dev.yandex.net/v1/chat/search'
        return response_mock(json=support_info_response)

    response = await taxi_driver_support_client.get(
        '/v1/internal/support_chat/summary', params=params,
    )
    assert response.status == status_code
    if status_code == 200:
        resp = await response.json()
        assert resp == expected_result
