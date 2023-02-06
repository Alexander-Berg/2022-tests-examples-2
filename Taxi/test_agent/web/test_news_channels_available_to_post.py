import pytest

JUSTMARK0_HEADERS = {'X-Yandex-Login': 'justmark0', 'Accept-Language': 'ru-RU'}
WEBALEX_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'}


@pytest.mark.parametrize(
    'headers,expected_data',
    [
        (
            JUSTMARK0_HEADERS,
            [
                {
                    'channel_id': 'channel_1',
                    'avatar': 'https://s3.mds.yandex.net/taxiagent/avatar_id',
                    'name': 'channel_1_name',
                },
                {
                    'channel_id': 'channel_2',
                    'avatar': 'https://s3.mds.yandex.net/taxiagent/avatar_id',
                    'name': 'channel_2_name',
                },
            ],
        ),
        (WEBALEX_HEADERS, []),
    ],
)
async def test_news_channels_available_to_post(
        web_app_client, headers, expected_data,
):
    response = await web_app_client.get(
        '/channel/available_to_post', headers=headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_data
