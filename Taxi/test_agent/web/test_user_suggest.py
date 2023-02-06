import pytest

AVATAR_TEMPLATE = 'https://center.yandex-team.ru/api/v1/user/%s/photo/300.jpg'


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
        },
    },
)
@pytest.mark.parametrize(
    'headers,request_data,expected_result_data',
    [
        (
            {'X-Yandex-Login': 'calltaxi_chief', 'Accept-Language': 'ru-ru'},
            {'search_string': ' fi  na '},
            {
                'users': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_chief',
                        'login': 'calltaxi_chief',
                        'first_name': 'first_name_1',
                        'last_name': 'last_name_1',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_support',
                        'login': 'calltaxi_support',
                        'first_name': 'first_name_2',
                        'last_name': 'last_name_2',
                    },
                    {
                        'avatar': (
                            AVATAR_TEMPLATE % 'calltaxi_support_without_data'
                        ),
                        'login': 'calltaxi_support_without_data',
                        'first_name': 'first_name_6',
                        'last_name': 'last_name_6',
                    },
                    {
                        'avatar': (
                            AVATAR_TEMPLATE % 'calltaxi_support_with_null_data'
                        ),
                        'login': 'calltaxi_support_with_null_data',
                        'first_name': 'first_name_7',
                        'last_name': 'last_name_7',
                    },
                ],
            },
        ),
        (
            {'X-Yandex-Login': 'calltaxi_chief', 'Accept-Language': 'en-en'},
            {'search_string': ' fi  na '},
            {
                'users': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_chief',
                        'login': 'calltaxi_chief',
                        'first_name': 'en_first_name_1',
                        'last_name': 'en_last_name_1',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_support',
                        'login': 'calltaxi_support',
                        'first_name': 'en_first_name_2',
                        'last_name': 'en_last_name_2',
                    },
                    {
                        'avatar': (
                            AVATAR_TEMPLATE % 'calltaxi_support_without_data'
                        ),
                        'login': 'calltaxi_support_without_data',
                        'first_name': 'en_first_name_6',
                        'last_name': 'en_last_name_6',
                    },
                    {
                        'avatar': (
                            AVATAR_TEMPLATE % 'calltaxi_support_with_null_data'
                        ),
                        'login': 'calltaxi_support_with_null_data',
                        'first_name': 'en_first_name_7',
                        'last_name': 'en_last_name_7',
                    },
                ],
            },
        ),
    ],
)
async def test_user_suggest(
        web_app_client, headers, request_data, expected_result_data,
):
    response = await web_app_client.post(
        '/user_suggest', headers=headers, json=request_data,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_result_data
