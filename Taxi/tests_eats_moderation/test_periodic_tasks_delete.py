import pytest


@pytest.fixture(name='mock_processing', autouse=True)
def _mock_processing(mockserver):
    @mockserver.json_handler(
        '/processing/v1/eda/restapp_moderation_hero/create-event',
    )
    def _create_event(request):

        assert request.json == {
            'data': {
                'context': {'place_id': 1234567},
                'moderator': '{"moderator_id":"unknown"}',
                'origin_data': {'data': 'qwerty'},
            },
            'kind': 'update-status',
            'new-status': 'deleted',
        }

        return mockserver.make_response(status=200, json={'event_id': '123'})

    return _create_event


async def test_periodic_task_delete_empty(
        taxi_eats_moderation, mock_processing,
):
    await taxi_eats_moderation.run_task(
        'distlock/periodic-delete-rejected-task-component',
    )

    assert mock_processing.times_called == 0


async def test_periodic_task_delete_happy_path(
        taxi_eats_moderation, mock_processing, mocked_time,
):
    mocked_time.sleep(2628000)
    # 730-часов значение больше чем период жизни
    # отклонённой задачи (по умолчанию 720 часов)

    await taxi_eats_moderation.invalidate_caches()

    await taxi_eats_moderation.run_task(
        'distlock/periodic-delete-rejected-task-component',
    )

    assert mock_processing.times_called == 1
