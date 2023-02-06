from aiohttp import ClientResponse
import pytest


@pytest.mark.parametrize(
    'driver_id, lessons',
    [
        ('driver6', []),
        (
            'driver3',
            [
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
        ),
    ],
)
async def test_lessons_progress_bulk_retrieve__no_progress(
        web_app_client, driver_id, lessons,
):
    response: ClientResponse = await web_app_client.post(
        f'/internal/driver-lessons/v1/lessons-progress/bulk-retrieve',
        json={'drivers': [{'park_id': 'park', 'driver_id': driver_id}]},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'lessons_progress': lessons}


async def test_lessons_progress_bulk_retrieve__multiple_drivers(
        web_app_client,
):
    response: ClientResponse = await web_app_client.post(
        f'/internal/driver-lessons/v1/lessons-progress/bulk-retrieve',
        json={
            'drivers': [
                {'park_id': 'park', 'driver_id': 'driver2'},
                {'park_id': 'park', 'driver_id': 'driver3'},
                {'park_id': 'park', 'driver_id': 'driver5'},
                {'park_id': 'non_existent_park', 'driver_id': 'driver3'},
            ],
        },
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'lessons_progress': [
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
                'lesson_id': '5bca0c9e7bcecff318fef2aa',
                'progress': 77,
                'driver_id': 'driver5',
                'park_id': 'park',
            },
        ],
    }


@pytest.mark.config(DRIVERS_COUNT_FOR_PROGRESS_REQUEST_LIMIT=40)
async def test_lessons_progress_bulk_retrieve__out_of_driver_limits__raises(
        web_app_client,
):
    response: ClientResponse = await web_app_client.post(
        f'/internal/driver-lessons/v1/lessons-progress/bulk-retrieve',
        json={
            'drivers': [
                {'park_id': 'park', 'driver_id': 'driver1'} for _ in range(41)
            ],
        },
    )

    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'too_many_drivers',
        'message': 'API allows no more than 40 per request',
    }
