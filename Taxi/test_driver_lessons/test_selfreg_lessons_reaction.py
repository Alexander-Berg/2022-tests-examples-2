import json

import pytest

BASE_URL = '/selfreg/v1/driver-lessons/v1/lessons'


@pytest.mark.parametrize(
    'token, selfreg_id, lesson_id, reaction,response_reaction,response_status',
    [
        (
            'token1',
            'selfreg_id_1',
            '5bca0c9e7bcecff318fef2aa',
            'disliked',
            'disliked',
            200,
        ),
        (
            'token3',
            'selfreg_id_3',
            '5bca0c9e7bcecff318fef2aa',
            'bad_reaction',
            '',
            400,
        ),
        (
            'token',
            'selfreg_id',
            '5bca0c9e7bcecff318fef2aa',
            'liked',
            'liked',
            200,
        ),
        ('token', 'selfreg_id', '5bca0c9e7bcecff318fef2bb', 'liked', '', 200),
        (
            'token3',
            'selfreg_id_3',
            '5bca0c9e7bcecff318fef2bb',
            'liked',
            '',
            200,
        ),
    ],
)
async def test_submit_reaction(
        web_app_client,
        mongo,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
        token,
        selfreg_id,
        lesson_id,
        reaction,
        response_reaction,
        response_status,
):
    url = make_lesson_url(BASE_URL, lesson_id, reaction=True)
    response = await web_app_client.post(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params(token),
        data=json.dumps({'reaction': reaction}),
    )
    assert response.status == response_status

    driver_progress = await mongo.driver_lessons_progress.find_one(
        {'selfreg_id': selfreg_id},
    )
    if driver_progress and response.status == 200:
        assert (
            driver_progress['progress'][lesson_id].get('reaction', '')
            == response_reaction
        )


async def test_nonexistent_lesson(
        web_app_client,
        make_selfreg_headers,
        make_lesson_url,
        make_selfreg_params,
):
    lesson_id = 'a0a0a0a0a0a0a0a0a0a0a0a0'
    url = make_lesson_url(BASE_URL, lesson_id, reaction=True)
    response = await web_app_client.post(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('token1'),
        data=json.dumps({'reaction': 'liked'}),
    )
    assert response.status == 404


async def test_selfreg_unauthorized(
        web_app_client,
        make_selfreg_headers,
        make_selfreg_params,
        make_lesson_url,
):
    lesson_id = '5bca0c9e7bcecff318fef2aa'
    url = make_lesson_url(BASE_URL, lesson_id, reaction=True)

    response = await web_app_client.post(
        url,
        headers=make_selfreg_headers(),
        params=make_selfreg_params('no_such_token'),
        data=json.dumps({'reaction': 'liked'}),
    )
    assert response.status == 401
