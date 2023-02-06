import pytest

DEFAULT_HEADERS = {
    'locale': 'ru',
    'X-Yandex-UID': '123456',
    'x-device-id': 'test_simple',
    'x-request-id': 'hello',
    'x-platform': 'superapp_taxi_web',
    'x-app-version': '1.12.0',
    'cookie': 'just a cookie',
    'x-eats-user': 'user_id=333,personal_phone_id=phone_id',
    'X-Eats-Session': 'blablabla',
}


@pytest.mark.parametrize(
    'phone_id,messages',
    [
        (
            'phone_id-1',
            [
                {
                    'timeout': 0,
                    'payload': {
                        'type': 'text',
                        'author': {
                            'name': {
                                'text': 'Раиль Мазгутов',
                                'color': '#C0C0C0',
                            },
                            'avatar': 'http://example.com/rails_avatar.png',
                        },
                        'side': 'left',
                        'text': (
                            'Вы вошли в самый обычный не секретный чат, '
                            'тут ничего не будет хоть вы и сделали 1 заказ, '
                            'уходите.'
                        ),
                        'image': 'http://example.com/not_secret_at_all.png',
                    },
                },
            ],
        ),
        (
            'phone_id-2',
            [
                {
                    'timeout': 0,
                    'payload': {
                        'type': 'text',
                        'author': {
                            'name': {
                                'text': 'Раиль Мазгутов',
                                'color': '#C0C0C0',
                            },
                            'avatar': 'http://example.com/rails_avatar.png',
                        },
                        'side': 'left',
                        'text': (
                            'Вы вошли в самый обычный не секретный чат, '
                            'тут ничего не будет хоть вы и сделали 10 '
                            'заказов, уходите.'
                        ),
                        'image': 'http://example.com/not_secret_at_all.png',
                    },
                },
            ],
        ),
        (
            'phone_id-3',
            [
                {
                    'timeout': 0,
                    'payload': {
                        'type': 'text',
                        'author': {
                            'name': {
                                'text': 'Раиль Мазгутов',
                                'color': '#C0C0C0',
                            },
                            'avatar': 'http://example.com/rails_avatar.png',
                        },
                        'side': 'left',
                        'text': (
                            'Вы вошли в самый обычный не секретный чат, '
                            'тут ничего не будет хоть вы и сделали 2 заказа, '
                            'уходите.'
                        ),
                        'image': 'http://example.com/not_secret_at_all.png',
                    },
                },
            ],
        ),
        (
            'phone_id-4',
            [
                {
                    'timeout': 0,
                    'payload': {
                        'type': 'text',
                        'author': {
                            'name': {
                                'text': 'Раиль Мазгутов',
                                'color': '#C0C0C0',
                            },
                            'avatar': 'http://example.com/rails_avatar.png',
                        },
                        'side': 'left',
                        'text': (
                            'Вы вошли в самый обычный не секретный чат, '
                            'тут ничего не будет хоть вы и сделали 0 заказов, '
                            'уходите.'
                        ),
                        'image': 'http://example.com/not_secret_at_all.png',
                    },
                },
            ],
        ),
    ],
)
@pytest.mark.experiments3(filename='chat_view_config.json')
async def test_chat_view_api_mock(
        taxi_eats_special_communications, phone_id, messages,
):
    headers = DEFAULT_HEADERS.copy()
    headers['x-eats-user'] = f'user_id=333,personal_phone_id={phone_id}'
    response = await taxi_eats_special_communications.post(
        'eats/v1/eats-special-communications/v1/view',
        params={'view_id': 'chat_view'},
        headers=headers,
    )

    assert response.status_code == 200
    response = response.json()
    assert response['messages'] == messages
    del response['messages']
    assert response == {
        'header': {
            'title': 'Default Title',
            'subtitle': 'Default Subtitle',
            'avatar': 'http://example.com/chat_avatar.png',
        },
        'background': 'http://example.com/chat_background.png',
        'color_scheme': {
            'title_color': '#FFFFFF',
            'subtitle_color': '#C0C0C0',
            'header_background_color': '#000000',
            'message_text_color': '#FFFFFF',
            'message_background_color': '#000000',
            'event_text_color': '#FFFFFF',
        },
    }
