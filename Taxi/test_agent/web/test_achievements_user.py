import pytest


@pytest.mark.parametrize(
    'url,expected_data',
    [
        (
            '/v1/achievements/webalex',
            {
                'earned_total': 6,
                'availables': [],
                'earned': [
                    {
                        'name': 'achievement.key_6.name',
                        'description': 'achievement.key_6.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-06T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_5.name',
                        'description': 'achievement.key_5.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-05T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_4.name',
                        'description': 'achievement.key_4.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-04T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_3.name',
                        'description': 'achievement.key_3.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-03T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_2.name',
                        'description': 'achievement.key_2.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-02T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_1.name',
                        'description': 'achievement.key_1.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-01T00:00:00Z',
                    },
                ],
            },
        ),
        (
            '/v1/achievements/webalex?limit=3',
            {
                'earned_total': 6,
                'earned': [
                    {
                        'name': 'achievement.key_6.name',
                        'description': 'achievement.key_6.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-06T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_5.name',
                        'description': 'achievement.key_5.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-05T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_4.name',
                        'description': 'achievement.key_4.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-04T00:00:00Z',
                    },
                ],
            },
        ),
        (
            '/v1/achievements/test_login?limit=3',
            {'earned_total': 0, 'earned': []},
        ),
        (
            '/v1/achievements/webalex?limit=1',
            {
                'earned_total': 6,
                'earned': [
                    {
                        'name': 'achievement.key_6.name',
                        'description': 'achievement.key_6.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-06T00:00:00Z',
                    },
                ],
            },
        ),
    ],
)
async def test_achievement_user_not_config(
        web_context, web_app_client, url, expected_data,
):
    response = await web_app_client.get(
        url, headers={'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_data


@pytest.mark.parametrize(
    'url,expected_data',
    [
        (
            '/v1/achievements/webalex',
            {
                'earned_total': 6,
                'availables': [
                    {
                        'name': 'achievement.key_7.name',
                        'description': 'achievement.key_7.description',
                        'image_link': 'img_inactive',
                        'coins': 7,
                    },
                    {
                        'name': 'achievement.key_8.name',
                        'description': 'achievement.key_8.description',
                        'image_link': 'img_inactive',
                        'coins': 8,
                    },
                    {
                        'name': 'achievement.key_9.name',
                        'description': 'achievement.key_9.description',
                        'image_link': 'img_inactive',
                        'coins': 9,
                    },
                ],
                'earned': [
                    {
                        'name': 'achievement.key_6.name',
                        'description': 'achievement.key_6.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-06T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_5.name',
                        'description': 'achievement.key_5.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-05T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_4.name',
                        'description': 'achievement.key_4.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-04T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_3.name',
                        'description': 'achievement.key_3.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-03T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_2.name',
                        'description': 'achievement.key_2.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-02T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_1.name',
                        'description': 'achievement.key_1.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-01T00:00:00Z',
                    },
                ],
            },
        ),
        (
            '/v1/achievements/webalex?limit=3',
            {
                'earned_total': 6,
                'earned': [
                    {
                        'name': 'achievement.key_6.name',
                        'description': 'achievement.key_6.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-06T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_5.name',
                        'description': 'achievement.key_5.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-05T00:00:00Z',
                    },
                    {
                        'name': 'achievement.key_4.name',
                        'description': 'achievement.key_4.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-04T00:00:00Z',
                    },
                ],
            },
        ),
        (
            '/v1/achievements/webalex?limit=1',
            {
                'earned_total': 6,
                'earned': [
                    {
                        'name': 'achievement.key_6.name',
                        'description': 'achievement.key_6.description',
                        'image_link': 'img_active',
                        'earned_at': '2021-01-06T00:00:00Z',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'achievements_collection': '2c04b547a3da476e85b50ead69db1970',
            'main_permission': 'user_calltaxi',
        },
    },
)
async def test_achievement_user_with_config(
        web_context, web_app_client, url, expected_data,
):
    response = await web_app_client.get(
        url, headers={'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_data
