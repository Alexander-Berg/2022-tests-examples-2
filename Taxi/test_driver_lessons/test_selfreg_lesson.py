import copy

import pytest

BASE_URL = '/selfreg/v1/driver-lessons/v1/lessons'

TAXIMETER_VERSION = '1.11'
EXPECTED_RESPONSE = {
    'id': '5bca0c9e7bcecff318fef3cc',
    'type': 'stories',
    'title': 'lesson1_title',
    'icon': 'text',
    'category': 'lesson1_category',
    'is_new': False,
    'is_completed': False,
    'close_available': True,
    'is_continuous': False,
    'progress': 80,
    'reactions_enabled': True,
    'preview': {
        'background': {'type': 'color', 'value': 'https://yandex.ru'},
        'title': {'color': '#FFFFFF', 'text': 'preview_tanker_key'},
    },
    'content': [
        {
            'id': '98b24196d27ab22471207e7ea71478fb',
            'type': 'stories',
            'stories_type': 'image_top',
            'timer': 3,
            'progress': 50,
            'text': {'title': 'something_amazing', 'color': '#FFFFFF'},
            'progress_bar': {
                'filled_color': '#FFFFFF',
                'unfilled_color': '#FFFFFF',
            },
            'buttons': [
                {
                    'title': 'title1',
                    'title_color': '#FFFFFF',
                    'background_color': '#000000',
                    'stroke_color': '#808080',
                    'action': {'url_open_type': 'webview', 'link': 'link1'},
                },
                {
                    'title': 'title2',
                    'title_color': '#FFFFFF',
                    'background_color': '#000000',
                    'stroke_color': '#808080',
                    'action': {'url_open_type': 'next', 'link': 'link2'},
                },
            ],
        },
    ],
}

TRANSLATIONS = {
    'lesson1_title': {
        'ru': 'Как сохранять доступ к заказам',
        'en': 'How to save access to orders',
    },
    'lesson1_text1': {
        'ru': 'Здесь какой-нибудь полезный текст',
        'en': 'Some appropriate text here',
    },
    'lesson1_text2': {
        'ru': 'Еще немного полезного текста',
        'en': 'A bit more text',
    },
    'lesson1_category': {'ru': 'Если вы новичок', 'en': 'For newbies'},
    'lesson1_img_url1': {
        'ru': 'https://yandex.disk/312d4d2d3sq345dsae3',
        'en': 'https://yandex.disk/312d4d2d3sq345dsae3',
    },
    'lesson1_youtube_url1': {
        'ru': 'https://www.youtube.com/watch?v=R5CRo4yaMfY',
        'en': 'https://www.youtube.com/watch?v=R5CRo4yaMfY',
    },
    'lesson_img_url_pre': {
        'ru': 'http://image.jpg',
        'en': 'http://en.image.jpg',
    },
    'something_amazing': {'ru': 'Тест сториса'},
    'preview_tanker_key': {'ru': 'Стори с витрины', 'en': 'Preview story'},
}


@pytest.fixture
def _expected_response():
    return copy.deepcopy(EXPECTED_RESPONSE)


@pytest.mark.parametrize(
    'token,lesson_progress,blocks_progress',
    [
        ('token1', 0, [0, 0, 0, 0]),
        ('token2', 100, [100, 100, 100, 100]),
        ('token3', 70, [100, 100, 80, 0]),
    ],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_get_lesson(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
        token,
        lesson_progress,
        blocks_progress,
):
    url = make_lesson_url(BASE_URL, '5bca0c9e7bcecff318fef2aa')
    response = await web_app_client.get(
        url, headers=make_selfreg_headers(), params=make_selfreg_params(token),
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'id': '5bca0c9e7bcecff318fef2aa',
        'type': 'default_lesson',
        'title': 'Как сохранять доступ к заказам',
        'icon': 'text',
        'category': 'Если вы новичок',
        'progress': lesson_progress,
        'is_new': False,
        'is_completed': lesson_progress == 100,
        'close_available': True,
        'is_continuous': False,
        'content': [
            {
                'id': '1bc8930f92ccd39525390d7be11eefe4',
                'type': 'html',
                'payload': 'Здесь какой-нибудь полезный текст',
                'progress': blocks_progress[0],
            },
            {
                'id': 'b3cba4b41f5acec18073b1bb856c3934',
                'type': 'image',
                'payload': 'https://yandex.disk/312d4d2d3sq345dsae3',
                'progress': blocks_progress[1],
            },
            {
                'id': '580c4dee3a23c9397f13ceaca5fe3beb',
                'type': 'video',
                'payload': 'https://www.youtube.com/watch?v=R5CRo4yaMfY',
                'progress': blocks_progress[2],
            },
            {
                'id': '1ef7c0a082457f4b9af16bbd184ac516',
                'type': 'markdown',
                'payload': 'Еще немного полезного текста',
                'progress': blocks_progress[3],
            },
        ],
    }


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_get_stories(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
):
    url = make_lesson_url(BASE_URL, '5bca0c9e7bcecff318fef3cc')
    response = await web_app_client.get(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('token4'),
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'id': '5bca0c9e7bcecff318fef3cc',
        'type': 'stories',
        'title': 'Как сохранять доступ к заказам',
        'icon': 'text',
        'category': 'Если вы новичок',
        'is_new': False,
        'is_completed': False,
        'close_available': True,
        'is_continuous': False,
        'progress': 80,
        'content': [
            {
                'id': '98b24196d27ab22471207e7ea71478fb',
                'type': 'stories',
                'stories_type': 'image_top',
                'timer': 3,
                'progress': 50,
                'text': {'title': 'Тест сториса', 'color': '#FFFFFF'},
                'progress_bar': {
                    'filled_color': '#FFFFFF',
                    'unfilled_color': '#FFFFFF',
                },
                'buttons': [
                    {
                        'title': 'title1',
                        'title_color': '#FFFFFF',
                        'background_color': '#000000',
                        'stroke_color': '#808080',
                        'action': {
                            'url_open_type': 'webview',
                            'link': 'link1',
                        },
                    },
                ],
            },
        ],
        'preview': {
            'title': {'text': 'Стори с витрины', 'color': '#FFFFFF'},
            'background': {'type': 'color', 'value': 'https://yandex.ru'},
        },
        'reactions_enabled': True,
    }


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_preview_url(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
):
    url = make_lesson_url(BASE_URL, '5bca0c9e7bcecff318fef2dd')
    response = await web_app_client.get(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('token'),
    )
    assert response.status == 200
    content = await response.json()
    assert content['preview_image_url'] == 'http://image.jpg'


@pytest.mark.parametrize('token,progress', [('token1', 0), ('token2', 100)])
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_get_lesson_another_locale(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
        token,
        progress,
):
    url = make_lesson_url(BASE_URL, '5bca0c9e7bcecff318fef2aa')
    response = await web_app_client.get(
        url,
        headers=make_selfreg_headers(
            additional_headers={'Accept-Language': 'en'},
        ),
        params=make_selfreg_params(token),
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'id': '5bca0c9e7bcecff318fef2aa',
        'type': 'default_lesson',
        'title': 'How to save access to orders',
        'icon': 'text',
        'category': 'For newbies',
        'progress': progress,
        'is_new': False,
        'close_available': True,
        'is_continuous': False,
        'is_completed': progress == 100,
        'content': [
            {
                'id': '1bc8930f92ccd39525390d7be11eefe4',
                'type': 'html',
                'payload': 'Some appropriate text here',
                'progress': progress,
            },
            {
                'id': 'b3cba4b41f5acec18073b1bb856c3934',
                'type': 'image',
                'payload': 'https://yandex.disk/312d4d2d3sq345dsae3',
                'progress': progress,
            },
            {
                'id': '580c4dee3a23c9397f13ceaca5fe3beb',
                'type': 'video',
                'payload': 'https://www.youtube.com/watch?v=R5CRo4yaMfY',
                'progress': progress,
            },
            {
                'id': '1ef7c0a082457f4b9af16bbd184ac516',
                'type': 'markdown',
                'payload': 'A bit more text',
                'progress': progress,
            },
        ],
    }


async def test_get_nonexistent_lesson(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
):
    url = make_lesson_url(BASE_URL, 'a0a0a0a0a0a0a0a0a0a0a0a0')
    response = await web_app_client.get(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('token1'),
    )
    assert response.status == 404


async def test_get_hidden_lesson(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
):
    url = make_lesson_url(BASE_URL, '5bca0c9e7bcecff318fef2cc')
    response = await web_app_client.get(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('token1'),
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'token,response_code',
    [
        ('token_spb', 404),
        ('token_hel', 200),
        ('token_minsk', 200),
        ('token_gom', 404),
        ('token_tallin', 200),
    ],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_territories(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
        token,
        response_code,
):
    url = make_lesson_url(BASE_URL, '4444444444444444deadbeaf')
    response = await web_app_client.get(
        url, headers=make_selfreg_headers(), params=make_selfreg_params(token),
    )
    assert response.status == response_code


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'next_button_in_stories': TAXIMETER_VERSION},
        },
    },
)
@pytest.mark.parametrize(
    'version',
    [
        pytest.param('1.12', id='greater'),
        pytest.param('1.11', id='equal'),
        pytest.param('0.99', id='less'),
    ],
)
async def test_story_next_button(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
        version,
        _expected_response,
):
    url = make_lesson_url(BASE_URL, '5bca0c9e7bcecff318fef3cc')
    response = await web_app_client.get(
        url,
        headers=make_selfreg_headers(app_version=version),
        params=make_selfreg_params('token4'),
    )
    assert response.status == 200
    content = await response.json()
    if version < TAXIMETER_VERSION:
        _expected_response['content'][0]['buttons'].pop(1)
    assert content == _expected_response


async def test_selfreg_unauthorized(
        web_app_client,
        make_selfreg_headers,
        make_selfreg_params,
        make_lesson_url,
):
    url = make_lesson_url(BASE_URL, '5bca0c9e7bcecff318fef2aa')
    response = await web_app_client.get(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('no_such_token'),
    )
    assert response.status == 401
