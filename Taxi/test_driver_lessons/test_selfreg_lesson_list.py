import pytest

URL = '/selfreg/v1/driver-lessons/v1/lessons'

TRANSLATIONS = {
    'lesson1_title': {
        'ru': 'Как сохранять доступ к заказам',
        'en': 'How to save access to orders',
    },
    'lesson1_category': {'ru': 'Если вы новичок', 'en': 'For newbies'},
    'lesson2_title': {
        'ru': 'Если в поездке что-то пошло не так',
        'en': 'If something went wrong during the ride',
    },
    'lesson2_category': {'ru': 'Если вы новичок', 'en': 'For newbies'},
    'lesson2_img_url_pre': {
        'ru': 'http://image.jpg',
        'en': 'http://en.image.jpg',
    },
}


@pytest.mark.parametrize(
    'token,first_lesson_progress', [('token1', 0), ('token2', 100)],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_no_tag(
        web_app_client,
        make_selfreg_headers,
        make_selfreg_params,
        token,
        first_lesson_progress,
):
    response = await web_app_client.get(
        URL, headers=make_selfreg_headers(), params=make_selfreg_params(token),
    )
    assert response.status == 200
    content = await response.json()
    if first_lesson_progress == 0:
        assert content == {
            'lessons': [
                {
                    'id': '5bca0c9e7bcecff318fef2aa',
                    'type': 'default_lesson',
                    'title': 'Как сохранять доступ к заказам',
                    'icon': 'text',
                    'category': 'Если вы новичок',
                    'progress': first_lesson_progress,
                    'reactions_enabled': True,
                    'reaction': 'liked',
                    'is_new': False,
                    'is_completed': first_lesson_progress == 100,
                    'close_available': True,
                    'is_continuous': True,
                },
                {
                    'id': '5bca0c9e7bcecff318fef2bb',
                    'type': 'default_lesson',
                    'title': 'Если в поездке что-то пошло не так',
                    'icon': 'text',
                    'preview_image_url': 'http://image.jpg',
                    'category': 'Если вы новичок',
                    'progress': 0,
                    'reactions_enabled': False,
                    'is_new': False,
                    'is_completed': False,
                    'close_available': True,
                    'is_continuous': False,
                },
                {
                    'id': '5bca0c9e7bcecff318fef2ee',
                    'type': 'stories',
                    'title': 'Как сохранять доступ к заказам',
                    'icon': 'text',
                    'category': 'Если вы новичок',
                    'progress': 0,
                    'is_new': False,
                    'is_completed': False,
                    'close_available': True,
                    'is_continuous': False,
                },
                {
                    'id': '5bca0c9e7bcecff318fef2dd',
                    'type': 'stories',
                    'title': 'Как сохранять доступ к заказам',
                    'icon': 'text',
                    'category': 'Если вы новичок',
                    'progress': 0,
                    'is_new': False,
                    'is_completed': False,
                    'close_available': True,
                    'is_continuous': False,
                },
            ],
        }
    else:
        assert content == {
            'lessons': [
                {
                    'id': '5bca0c9e7bcecff318fef2bb',
                    'type': 'default_lesson',
                    'title': 'Если в поездке что-то пошло не так',
                    'icon': 'text',
                    'preview_image_url': 'http://image.jpg',
                    'category': 'Если вы новичок',
                    'progress': 0,
                    'reactions_enabled': False,
                    'is_new': False,
                    'is_completed': False,
                    'close_available': True,
                    'is_continuous': False,
                },
                {
                    'id': '5bca0c9e7bcecff318fef2ee',
                    'type': 'stories',
                    'title': 'Как сохранять доступ к заказам',
                    'icon': 'text',
                    'category': 'Если вы новичок',
                    'progress': 0,
                    'is_new': False,
                    'is_completed': False,
                    'close_available': True,
                    'is_continuous': False,
                },
                {
                    'id': '5bca0c9e7bcecff318fef2dd',
                    'type': 'stories',
                    'title': 'Как сохранять доступ к заказам',
                    'icon': 'text',
                    'category': 'Если вы новичок',
                    'progress': 0,
                    'is_new': False,
                    'is_completed': False,
                    'close_available': True,
                    'is_continuous': False,
                },
                {
                    'id': '5bca0c9e7bcecff318fef2aa',
                    'type': 'default_lesson',
                    'title': 'Как сохранять доступ к заказам',
                    'icon': 'text',
                    'category': 'Если вы новичок',
                    'progress': first_lesson_progress,
                    'reactions_enabled': True,
                    'reaction': 'liked',
                    'is_new': False,
                    'is_completed': first_lesson_progress == 100,
                    'close_available': True,
                    'is_continuous': True,
                },
            ],
        }


@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_locales(
        web_app_client, make_selfreg_headers, make_selfreg_params, locale,
):
    response = await web_app_client.get(
        URL,
        headers=make_selfreg_headers(
            additional_headers={'Accept-Language': locale},
        ),
        params=make_selfreg_params('token1'),
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'lessons': [
            {
                'id': '5bca0c9e7bcecff318fef2aa',
                'type': 'default_lesson',
                'title': TRANSLATIONS['lesson1_title'][locale],
                'icon': 'text',
                'category': TRANSLATIONS['lesson1_category'][locale],
                'progress': 0,
                'reactions_enabled': True,
                'reaction': 'liked',
                'is_new': False,
                'is_completed': False,
                'close_available': True,
                'is_continuous': True,
            },
            {
                'id': '5bca0c9e7bcecff318fef2bb',
                'type': 'default_lesson',
                'title': TRANSLATIONS['lesson2_title'][locale],
                'icon': 'text',
                'preview_image_url': TRANSLATIONS['lesson2_img_url_pre'][
                    locale
                ],
                'category': TRANSLATIONS['lesson2_category'][locale],
                'progress': 0,
                'reactions_enabled': False,
                'is_new': False,
                'is_completed': False,
                'close_available': True,
                'is_continuous': False,
            },
            {
                'id': '5bca0c9e7bcecff318fef2ee',
                'type': 'stories',
                'title': TRANSLATIONS['lesson1_title'][locale],
                'icon': 'text',
                'category': TRANSLATIONS['lesson1_category'][locale],
                'progress': 0,
                'is_new': False,
                'is_completed': False,
                'close_available': True,
                'is_continuous': False,
            },
            {
                'id': '5bca0c9e7bcecff318fef2dd',
                'type': 'stories',
                'title': TRANSLATIONS['lesson1_title'][locale],
                'icon': 'text',
                'category': TRANSLATIONS['lesson1_category'][locale],
                'progress': 0,
                'is_new': False,
                'is_completed': False,
                'close_available': True,
                'is_continuous': False,
            },
        ],
    }


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_single_tag(
        web_app_client, make_selfreg_headers, make_selfreg_params,
):
    response = await web_app_client.get(
        URL,
        headers=make_selfreg_headers(),
        params=make_selfreg_params(
            'token', additional_params={'tags': ','.join(['newbie', 'tag2'])},
        ),
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'lessons': [
            {
                'id': '5bca0c9e7bcecff318fef2aa',
                'type': 'default_lesson',
                'title': 'Как сохранять доступ к заказам',
                'icon': 'text',
                'category': 'Если вы новичок',
                'progress': 0,
                'reactions_enabled': True,
                'is_new': False,
                'is_completed': False,
                'close_available': True,
                'is_continuous': True,
            },
        ],
    }


@pytest.mark.parametrize(
    'token,etag,should_update',
    [
        ('token', '', True),
        ('token', 'd41d8cd98f00b204e9800998ecf8427e', True),
        (
            'token',
            'W/"d41d8cd98f00b204e9800998ecf8427e'
            '__ca5f14a9b65e819a417205ee3919ac97"',
            False,
        ),
        ('token1', 'd41d8cd98f00b204e9800998ecf8427e', True),
        (
            'token1',
            'W/"d41d8cd98f00b204e9800998ecf8427e'
            '_ca5f14a9b65e819a417205ee3919ac97'
            '_ca5f14a9b65e819a417205ee3919ac97"',
            False,
        ),
    ],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_etag(
        web_app_client,
        make_selfreg_headers,
        make_selfreg_params,
        token,
        etag,
        should_update,
):
    response = await web_app_client.get(
        URL,
        headers=make_selfreg_headers(
            additional_headers={'If-None-Match': etag},
        ),
        params=make_selfreg_params(token),
    )

    if should_update:
        assert response.status == 200
        content = await response.json()
        assert content['lessons']
    else:
        assert response.status == 304


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_etag_changing(
        web_app_client, web_app, make_selfreg_headers, make_selfreg_params,
):
    response = await web_app_client.get(
        URL,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('token'),
    )

    assert response.status == 200
    etag = response.headers['ETag']

    response = await web_app_client.get(
        URL,
        headers=make_selfreg_headers(
            additional_headers={'If-None-Match': etag},
        ),
        params=make_selfreg_params('token'),
    )
    assert response.status == 304
    assert response.headers['ETag'] == etag

    await web_app_client.post(
        '/admin/driver-lessons',
        headers={'X-API-Key': 'API-KEY'},
        json={
            'priority': 1,
            'tags': ['newbie'],
            'is_hidden': False,
            'title': 'lesson5_title',
            'icon': 'text',
            'preview_image_url': 'lesson5_img_url_pre',
            'category': 'category',
            'content': [{'type': 'html', 'payload': 'text'}],
            'allowed_territories': {},
        },
    )
    await web_app['context'].lessons_cache.refresh_cache()

    response = await web_app_client.get(
        URL,
        headers=make_selfreg_headers(
            additional_headers={'If-None-Match': etag},
        ),
        params=make_selfreg_params('token'),
    )
    assert response.status == 200
    content = await response.json()
    assert content['lessons']
    assert response.headers['ETag'] != etag


SAMPLE_LESSONS = [
    {
        'id': '5bca0c9e7bcecff318fef2aa',
        'title': 'Как сохранять доступ к заказам',
        'icon': 'text',
        'category': 'Если вы новичок',
        'progress': 0,
        'is_new': False,
        'is_completed': False,
    },
    {
        'id': '5bca0c9e7bcecff318fef2bb',
        'title': 'Если в поездке что-то пошло не так',
        'icon': 'text',
        'preview_image_url': 'http://image.jpg',
        'category': 'Если вы новичок',
        'progress': 0,
        'is_new': False,
        'is_completed': False,
    },
]


@pytest.mark.parametrize(
    'token,lessons_cnt',
    [
        ('token_spb', 0),
        ('token_hel', 1),
        ('token_minsk', 1),
        ('token_gom', 0),
        ('token_tallin', 1),
    ],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_territories(
        web_app_client,
        web_app,
        make_selfreg_headers,
        make_selfreg_params,
        token,
        lessons_cnt,
):
    response = await web_app_client.post(
        '/admin/driver-lessons',
        headers={'X-API-Key': 'API-KEY'},
        json={
            'priority': 1,
            'tags': ['newbie'],
            'is_hidden': False,
            'title': 'lesson5_title',
            'icon': 'text',
            'category': 'category',
            'content': [{'type': 'html', 'payload': 'text'}],
            'allowed_territories': {
                'fin': {'mode': 'include', 'cities': ['Хельсинки']},
                'blr': {'mode': 'exclude', 'cities': ['Гомель']},
                'est': {},
            },
        },
    )
    assert response.status == 200
    await web_app['context'].lessons_cache.refresh_cache()

    response = await web_app_client.get(
        URL, headers=make_selfreg_headers(), params=make_selfreg_params(token),
    )

    assert response.status == 200
    content = await response.json()
    assert len(content['lessons']) == lessons_cnt


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_filter_by_type(
        web_app_client, make_selfreg_headers, make_selfreg_params,
):
    response = await web_app_client.get(
        URL,
        headers=make_selfreg_headers(),
        params=make_selfreg_params(
            'token', additional_params={'type': 'stories'},
        ),
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'lessons': [
            {
                'id': '5bca0c9e7bcecff318fef2ee',
                'type': 'stories',
                'title': 'Как сохранять доступ к заказам',
                'icon': 'text',
                'category': 'Если вы новичок',
                'progress': 0,
                'is_new': False,
                'is_completed': False,
                'close_available': True,
                'is_continuous': False,
            },
            {
                'id': '5bca0c9e7bcecff318fef2dd',
                'type': 'stories',
                'title': 'Как сохранять доступ к заказам',
                'icon': 'text',
                'category': 'Если вы новичок',
                'progress': 0,
                'is_new': False,
                'is_completed': False,
                'close_available': True,
                'is_continuous': False,
            },
        ],
    }


async def test_selfreg_unauthorized(
        web_app_client, make_selfreg_headers, make_selfreg_params,
):
    response = await web_app_client.get(
        URL,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('no_such_token'),
    )
    assert response.status == 401
