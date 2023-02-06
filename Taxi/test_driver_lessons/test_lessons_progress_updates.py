from aiohttp import ClientResponse
import pytest


async def test_lessons_progress_updates__no_param(web_app_client):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons-progress/updates', json={},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'lessons_progress': [
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 77,
                'driver_id': 'driver6',
                'park_id': 'park2',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 0,
                'driver_id': 'driver1',
                'park_id': 'park',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 100,
                'driver_id': 'driver2',
                'park_id': 'park',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 70,
                'driver_id': 'driver3',
                'park_id': 'park',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2bb',
                'progress': 75,
                'driver_id': 'driver3',
                'park_id': 'park',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2cc',
                'progress': 75,
                'driver_id': 'driver3',
                'park_id': 'park',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef3cc',
                'progress': 80,
                'driver_id': 'driver4',
                'park_id': 'park',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 77,
                'driver_id': 'driver5',
                'park_id': 'park',
            },
        ],
        'revision': '1638546080_607',
    }


async def test_lessons_progress_updates__check_limit(web_app_client):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons-progress/updates',
        json={'limit': 3},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'lessons_progress': [
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 77,
                'driver_id': 'driver6',
                'park_id': 'park2',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 0,
                'driver_id': 'driver1',
                'park_id': 'park',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 100,
                'driver_id': 'driver2',
                'park_id': 'park',
            },
        ],
        'revision': '1498754367_607',
    }


async def test_lessons_progress_updates_not_found_with_revision(
        web_app_client,
):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons-progress/updates',
        json={'last_known_revision': '1638880496_0', 'limit': 10},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'lessons_progress': [], 'revision': '1638880496_0'}


@pytest.mark.filldb(driver_lessons_progress='empty')
async def test_lessons_progress_updates_not_found_no_revision(web_app_client):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons-progress/updates', json={},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'lessons_progress': []}


async def test_lessons_progress_updates__with_timestamp__has_results(
        web_app_client,
):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons-progress/updates',
        json={'last_known_revision': '1638362096_0', 'limit': 100},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'lessons_progress': [
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 77,
                'driver_id': 'driver5',
                'park_id': 'park',
            },
        ],
        'revision': '1638546080_607',
    }


async def test_lessons_progress_updates__with_non_uniq_timestamp__return_equal(
        web_app_client,
):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons-progress/updates',
        json={'last_known_revision': '1498754367_367', 'limit': 3},
    )

    assert response.status == 200
    content = await response.json()

    assert content == {
        'lessons_progress': [
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 0,
                'driver_id': 'driver1',
                'park_id': 'park',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 100,
                'driver_id': 'driver2',
                'park_id': 'park',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 70,
                'driver_id': 'driver3',
                'park_id': 'park',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2bb',
                'progress': 75,
                'driver_id': 'driver3',
                'park_id': 'park',
            },
            {
                'lesson_id': '5bca0c9e7bcecff318fef2cc',
                'progress': 75,
                'driver_id': 'driver3',
                'park_id': 'park',
            },
        ],
        'revision': '1498754367_607',
    }


async def test_lessons_progress_updates__incorrect_revision__raises(
        web_app_client,
):
    response: ClientResponse = await web_app_client.post(
        '/internal/driver-lessons/v1/lessons-progress/updates',
        json={'last_known_revision': '4294967297_1', 'limit': 100},
    )

    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'bad_revision',
        'message': (
            'Incorrect revision format! '
            'Expected sting "1234567890_123" (timestamp_increment)'
        ),
    }


async def test_lessons_progress_latest_revision(taxi_driver_lessons):
    response = await taxi_driver_lessons.get(
        '/internal/driver-lessons/v1/lessons-progress/latest-revision',
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'revision': '1638546080_607'}


@pytest.mark.filldb(driver_lessons_progress='empty')
async def test_lessons_progress_latest_revision_not_found(taxi_driver_lessons):
    response = await taxi_driver_lessons.get(
        '/internal/driver-lessons/v1/lessons-progress/latest-revision',
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}
