import json

import pytest

BASE_URL = '/selfreg/v1/driver-lessons/v1/lessons'

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
    'token,selfreg_id,blocks,total',
    [
        ('token1', 'selfreg_id_1', [100, 100, 100, 100], 100),
        ('token3', 'selfreg_id_3', [100, 100, 0, 0], 50),
        ('token', 'selfreg_id', [50, 0, 0, 0], 12),
    ],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_mark_complete(
        web_app_client,
        mongo,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
        token,
        selfreg_id,
        blocks,
        total,
):
    lesson_id = '5bca0c9e7bcecff318fef2aa'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    request_data = {BLOCK_IDS[i]: blocks[i] for i in range(4)}

    response = await web_app_client.post(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params(token),
        data=json.dumps(request_data),
    )
    assert response.status == 200

    driver_progress = await mongo.driver_lessons_progress.find_one(
        {'selfreg_id': selfreg_id},
    )
    if token == 'token':
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
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
):
    lesson_id = '5bca0c9e7bcecff318fef2aa'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    request_data = {BLOCK_IDS[i]: 100 for i in range(4)}
    request_data['bad_id'] = 100

    response = await web_app_client.post(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('token'),
        data=json.dumps(request_data),
    )
    assert response.status == 400


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_wrong_status(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
):
    lesson_id = '5bca0c9e7bcecff318fef2aa'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    request_data = {BLOCK_IDS[i]: -10 for i in range(4)}
    response = await web_app_client.post(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('token'),
        data=json.dumps(request_data),
    )

    assert response.status == 400


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_already_completed(
        web_app_client,
        mongo,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
):
    lesson_id = '5bca0c9e7bcecff318fef2aa'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    request_data = {BLOCK_IDS[i]: 0 for i in range(4)}
    response = await web_app_client.post(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('token2'),
        data=json.dumps(request_data),
    )

    assert response.status == 200

    driver_progress = await mongo.driver_lessons_progress.find_one(
        {'selfreg_id': 'selfreg_id_2'},
    )
    assert driver_progress['progress'][lesson_id] == {
        'total': 100,
        'by_blocks': {},
        'reaction': 'liked',
    }


@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_mark_complete_nonexistent(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
):
    lesson_id = 'a0a0a0a0a0a0a0a0a0a0a0a0'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    response = await web_app_client.post(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('token1'),
        data=json.dumps({'progress': 100}),
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'data',
    [{'a': 'fwawefawe'}, {'a': 100, 'b': 'asas'}, {'a': 100, 'b': {'c': 100}}],
)
@pytest.mark.translations(taximeter_backend_driver_lessons=TRANSLATIONS)
async def test_bad_request(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
        data,
):
    lesson_id = 'aaaaaaaaa'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    response = await web_app_client.post(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('token1'),
        data=json.dumps(data),
    )
    assert response.status == 400


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
async def test_territories(
        web_app_client,
        web_app,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
        token,
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

    response = await web_app_client.post(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params(token),
        json={BLOCK_IDS[0]: 100},
    )
    assert response.status == response_code


async def test_selfreg_unauthorized(
        web_app_client,
        make_selfreg_headers,
        make_selfreg_params,
        make_lesson_url,
):
    lesson_id = '5bca0c9e7bcecff318fef2aa'
    url = make_lesson_url(BASE_URL, lesson_id, complete=True)
    blocks = [100, 100, 100, 100]
    request_data = {BLOCK_IDS[i]: blocks[i] for i in range(4)}

    response = await web_app_client.post(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('no_such_token'),
        data=json.dumps(request_data),
    )
    assert response.status == 401
