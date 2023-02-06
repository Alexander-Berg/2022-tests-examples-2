import json

import pytest

BASE_URL = '/driver/v1/driver-lessons/v1/lessons'

BLOCK_IDS = [
    '1bc8930f92ccd39525390d7be11eefe4',
    'b3cba4b41f5acec18073b1bb856c3934',
    '580c4dee3a23c9397f13ceaca5fe3beb',
    '1ef7c0a082457f4b9af16bbd184ac516',
]
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
    'driver_id,blocks,total',
    [
        ('driver1', [100, 100, 100, 100], 100),
        ('driver3', [100, 100, 0, 0], 50),
        ('driverNEW', [50, 0, 0, 0], 12),
    ],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_mark_complete(
        web_app_client,
        mongo,
        make_dap_headers,
        make_lesson_url,
        driver_id,
        blocks,
        total,
):
    lesson_id = '5bca0c9e7bcecff318fef2aa'
    park_id = 'park'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    request_data = {BLOCK_IDS[i]: blocks[i] for i in range(4)}

    response = await web_app_client.post(
        url,
        headers=make_dap_headers(park_id=park_id, driver_id=driver_id),
        data=json.dumps(request_data),
    )
    assert response.status == 200

    driver_progress = await mongo.driver_lessons_progress.find_one(
        {'park_id': park_id, 'driver_id': driver_id},
    )
    if driver_id == 'driverNEW':
        assert driver_progress['progress'][lesson_id] == {
            'total': total,
            'by_blocks': request_data if total != 100 else {},
        }
    else:
        assert driver_progress['progress'][lesson_id] == {
            'reaction': 'liked',
            'total': total,
            'by_blocks': request_data if total != 100 else {},
        }


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_missing_blocks(
        web_app_client, make_dap_headers, make_lesson_url,
):
    lesson_id = '5bca0c9e7bcecff318fef2aa'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    park_id = 'park'
    driver_id = 'd'
    request_data = {BLOCK_IDS[i]: 100 for i in range(4)}
    request_data['bad_id'] = 100

    response = await web_app_client.post(
        url,
        headers=make_dap_headers(park_id=park_id, driver_id=driver_id),
        data=json.dumps(request_data),
    )
    assert response.status == 400


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_wrong_status(web_app_client, make_dap_headers, make_lesson_url):
    lesson_id = '5bca0c9e7bcecff318fef2aa'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    park_id = 'park'
    driver_id = 'd'
    request_data = {BLOCK_IDS[i]: -10 for i in range(4)}
    response = await web_app_client.post(
        url,
        headers=make_dap_headers(park_id=park_id, driver_id=driver_id),
        data=json.dumps(request_data),
    )

    assert response.status == 400


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_already_completed(
        web_app_client, mongo, make_dap_headers, make_lesson_url,
):
    lesson_id = '5bca0c9e7bcecff318fef2aa'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    park_id = 'park'
    driver_id = 'driver2'
    request_data = {BLOCK_IDS[i]: 0 for i in range(4)}
    response = await web_app_client.post(
        url,
        headers=make_dap_headers(park_id=park_id, driver_id=driver_id),
        data=json.dumps(request_data),
    )

    assert response.status == 200

    driver_progress = await mongo.driver_lessons_progress.find_one(
        {'park_id': park_id, 'driver_id': driver_id},
    )
    assert driver_progress['progress'][lesson_id] == {
        'total': 100,
        'by_blocks': {},
        'reaction': 'liked',
    }


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_mark_complete_nonexistent(
        web_app_client, make_dap_headers, make_lesson_url,
):
    lesson_id = 'a0a0a0a0a0a0a0a0a0a0a0a0'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    park_id = 'park'
    driver_id = 'driver1'
    response = await web_app_client.post(
        url,
        headers=make_dap_headers(park_id=park_id, driver_id=driver_id),
        data=json.dumps({'progress': 100}),
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'data',
    [{'a': 'fwawefawe'}, {'a': 100, 'b': 'asas'}, {'a': 100, 'b': {'c': 100}}],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_bad_request(
        web_app_client, make_dap_headers, make_lesson_url, data,
):
    lesson_id = 'aaaaaaaaa'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    park_id = 'park'
    driver_id = 'driver1'
    response = await web_app_client.post(
        url,
        headers=make_dap_headers(park_id=park_id, driver_id=driver_id),
        data=json.dumps(data),
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'park,response_code',
    [
        ('p_spb', 404),
        ('p_hel', 200),
        ('p_minsk', 200),
        ('p_gom', 404),
        ('p_tallin', 200),
    ],
)
async def test_territories(
        web_app_client,
        web_app,
        make_dap_headers,
        make_lesson_url,
        park,
        response_code,
):
    lesson_id = '5bca0c9e7bcecff318fef2aa'

    response = await web_app_client.post(
        f'/admin/driver-lessons/{lesson_id}',
        headers={'X-API-Key': 'API-KEY'},
        json={
            'priority': 1,
            'tags': ['newbie'],
            'is_hidden': False,
            'title': 'lesson1_title',
            'icon': 'text',
            'category': 'lesson1_category',
            'content': [{'payload': 'lesson1_text1', 'type': 'html'}],
            'allowed_territories': {
                'fin': {'mode': 'include', 'cities': ['Хельсинки']},
                'blr': {'mode': 'exclude', 'cities': ['Гомель']},
                'est': {},
            },
        },
    )
    assert response.status == 200
    await web_app['context'].lessons_cache.refresh_cache()

    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    driver_id = 'driverNew'

    response = await web_app_client.post(
        url,
        headers=make_dap_headers(park_id=park, driver_id=driver_id),
        json={BLOCK_IDS[0]: 100},
    )
    assert response.status == response_code
