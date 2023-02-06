from bson import ObjectId
import pytest


async def test_remove_nonexistent_lesson(web_app_client):
    response = await web_app_client.post(
        '/admin/driver-lessons/remove/5bc000999bcecffffff222aa',
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'lesson_id, response_status',
    [('5bca0c9e7bcecff318fef2bb', 200), ('5bca0c9e7bcecff318fef2aa', 400)],
)
async def test_removed(web_app_client, mongo, lesson_id, response_status):
    await web_app_client.post('/admin/driver-lessons/' + lesson_id)

    lesson = await mongo.driver_lessons.find_one({'_id': ObjectId(lesson_id)})
    assert lesson is not None

    response = await web_app_client.post(
        '/admin/driver-lessons/remove/' + lesson_id,
    )
    if response.status == 200:
        lesson = await mongo.driver_lessons.find_one(
            {'_id': ObjectId(lesson_id)},
        )
        assert lesson is None

    assert response.status == response_status
