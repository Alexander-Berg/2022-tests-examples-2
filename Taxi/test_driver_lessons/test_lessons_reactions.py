import json

import pytest

BASE_URL = '/driver/v1/driver-lessons/v1/lessons'


@pytest.mark.parametrize(
    'driver_id, lesson_id, reaction,response_reaction,response_status',
    [
        ('driver1', '5bca0c9e7bcecff318fef2aa', 'disliked', 'disliked', 200),
        ('driver3', '5bca0c9e7bcecff318fef2aa', 'bad_reaction', '', 400),
        ('driverNEW1', '5bca0c9e7bcecff318fef2aa', 'liked', 'liked', 200),
        ('driverNEW2', '5bca0c9e7bcecff318fef2bb', 'liked', '', 200),
        ('driver3', '5bca0c9e7bcecff318fef2bb', 'liked', '', 200),
    ],
)
async def test_submit_reaction(
        web_app_client,
        mongo,
        make_dap_headers,
        make_lesson_url,
        driver_id,
        lesson_id,
        reaction,
        response_reaction,
        response_status,
):
    url = make_lesson_url(BASE_URL, lesson_id, reaction=True)
    park_id = 'park'
    response = await web_app_client.post(
        url,
        headers=make_dap_headers(park_id=park_id, driver_id=driver_id),
        data=json.dumps({'reaction': reaction}),
    )
    assert response.status == response_status

    driver_progress = await mongo.driver_lessons_progress.find_one(
        {'park_id': park_id, 'driver_id': driver_id},
    )
    if driver_progress and response.status == 200:
        assert (
            driver_progress['progress'][lesson_id].get('reaction', '')
            == response_reaction
        )


async def test_nonexistent_lesson(
        web_app_client, make_dap_headers, make_lesson_url,
):
    lesson_id = 'a0a0a0a0a0a0a0a0a0a0a0a0'
    url = make_lesson_url(BASE_URL, lesson_id, reaction=True)
    park_id = 'park'
    driver_id = 'driver1'
    response = await web_app_client.post(
        url,
        headers=make_dap_headers(park_id=park_id, driver_id=driver_id),
        data=json.dumps({'reaction': 'liked'}),
    )
    assert response.status == 404
