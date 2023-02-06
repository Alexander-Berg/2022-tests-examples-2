import pytest

URL = '/driver/v1/driver-lessons/v1/lessons'

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
    'driver_id,first_lesson_progress', [('driver1', 0), ('driver2', 100)],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_no_tag(
        web_app_client, make_dap_headers, driver_id, first_lesson_progress,
):
    park_id = 'park'
    response = await web_app_client.get(
        URL, headers=make_dap_headers(park_id=park_id, driver_id=driver_id),
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
async def test_locales(web_app_client, make_dap_headers, locale):
    response = await web_app_client.get(
        URL,
        headers=make_dap_headers(
            park_id='park',
            driver_id='driver1',
            additional_headers={'Accept-Language': locale},
        ),
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
async def test_single_tag(web_app_client, make_dap_headers):
    response = await web_app_client.get(
        URL,
        headers=make_dap_headers(park_id='park', driver_id='d'),
        params={'tags': ','.join(['newbie', 'tag2'])},
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
    'driver,etag,should_update',
    [
        ('d', '', True),
        ('d', 'd41d8cd98f00b204e9800998ecf8427e', True),
        (
            'd',
            'W/"d41d8cd98f00b204e9800998ecf8427e'
            '__ca5f14a9b65e819a417205ee3919ac97"',
            False,
        ),
        ('driver1', 'd41d8cd98f00b204e9800998ecf8427e', True),
        (
            'driver1',
            'W/"d41d8cd98f00b204e9800998ecf8427e'
            '_ca5f14a9b65e819a417205ee3919ac97'
            '_ca5f14a9b65e819a417205ee3919ac97"',
            False,
        ),
    ],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_etag(
        web_app_client, make_dap_headers, driver, etag, should_update,
):
    response = await web_app_client.get(
        URL,
        headers=make_dap_headers(
            park_id='park',
            driver_id=driver,
            additional_headers={'If-None-Match': etag},
        ),
    )

    if should_update:
        assert response.status == 200
        content = await response.json()
        assert content['lessons']
    else:
        assert response.status == 304


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_etag_changing(web_app_client, web_app, make_dap_headers):
    response = await web_app_client.get(
        URL, headers=make_dap_headers(park_id='park', driver_id='d'),
    )

    assert response.status == 200
    etag = response.headers['ETag']

    response = await web_app_client.get(
        URL,
        headers=make_dap_headers(
            park_id='park',
            driver_id='d',
            additional_headers={'If-None-Match': etag},
        ),
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
        headers=make_dap_headers(
            park_id='park',
            driver_id='d',
            additional_headers={'If-None-Match': etag},
        ),
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
    'park,lessons_cnt',
    [
        ('p_spb', 0),
        ('p_hel', 1),
        ('p_minsk', 1),
        ('p_gom', 0),
        ('p_tallin', 1),
    ],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_territories(
        web_app_client, web_app, make_dap_headers, park, lessons_cnt,
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
        URL, headers=make_dap_headers(park_id=park, driver_id='driverNew'),
    )

    assert response.status == 200
    content = await response.json()
    assert len(content['lessons']) == lessons_cnt


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_filter_by_type(web_app_client, make_dap_headers):
    response = await web_app_client.get(
        URL,
        headers=make_dap_headers(park_id='park', driver_id='d'),
        params={'type': 'stories'},
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
