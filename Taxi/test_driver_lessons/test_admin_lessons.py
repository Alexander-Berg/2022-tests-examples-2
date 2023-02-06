import pytest


def _parse_object_id(lesson):
    lesson['id'] = str(lesson['_id'])
    lesson['type'] = lesson.get('type', 'default_lesson')
    lesson['close_available'] = lesson.get('close_available', True)
    lesson['is_continuous'] = lesson.get('is_continuous', False)
    lesson.pop('_id')
    lesson.pop('modified_date')
    return lesson


@pytest.mark.parametrize(
    'url', ['/admin/driver-lessons', '/admin/driver-lessons/'],
)
async def test_admin_lesson_list(web_app_client, web_app, mongo, url):
    response = await web_app_client.get(url)
    assert response.status == 200

    content = await response.json()
    data = [
        _parse_object_id(lesson)
        async for lesson in mongo.driver_lessons.find({})
    ]

    assert content == {'lessons': data}
