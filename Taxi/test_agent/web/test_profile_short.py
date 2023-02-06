import pytest

from agent import const


@pytest.mark.parametrize(
    'src_login,dst_login,status,expected_data',
    [
        (
            'webalex',
            'webalex',
            200,
            {
                'person': {
                    'avatar': const.STAFF_AVATAR_TEMPLATES_URL % 'webalex',
                    'first_name': 'Александр',
                    'last_name': 'Иванов',
                    'login': 'webalex',
                },
                'team': 'Команда Calltaxi',
                'telegrams': ['@telegram_account'],
                'department': 'Яндекс',
                'head': {
                    'avatar': const.STAFF_AVATAR_TEMPLATES_URL % 'orangevl',
                    'first_name': 'Семен',
                    'last_name': 'Решетняк',
                    'login': 'orangevl',
                },
                'full_profile': True,
            },
        ),
        (
            'webalex',
            'liambaev',
            200,
            {
                'person': {
                    'avatar': const.STAFF_AVATAR_TEMPLATES_URL % 'liambaev',
                    'first_name': 'Лиам',
                    'last_name': 'Баев',
                    'login': 'liambaev',
                },
                'team': 'Команда Calltaxi',
                'telegrams': ['@telegram_account'],
                'full_profile': False,
            },
        ),
        (
            'webalex',
            'orangevl',
            403,
            {'code': 'access_denied', 'message': 'General error'},
        ),
    ],
)
async def test_short_profile(
        web_app_client,
        web_context,
        src_login,
        dst_login,
        status,
        expected_data,
        mock_retrieve_telegrams,
):
    response = await web_app_client.get(
        f'/profile/short/{dst_login}',
        headers={'X-Yandex-Login': src_login, 'Accept-Language': 'ru-RU'},
    )

    assert response.status == status
    content = await response.json()
    assert content == expected_data
