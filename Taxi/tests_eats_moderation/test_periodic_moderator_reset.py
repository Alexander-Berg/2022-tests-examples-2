import pytest


@pytest.fixture(name='mock_processing', autouse=True)
def _mock_processing(mockserver):
    @mockserver.json_handler(
        '/processing/v1/eda/restapp_moderation_hero/create-event',
    )
    def _create_event(request):

        return mockserver.make_response(status=200, json={'event_id': '123'})

    return _create_event


async def test_periodic_moderator_reset_empty(
        taxi_eats_moderation, mock_processing,
):
    await taxi_eats_moderation.run_task(
        'distlock/periodic-reset-moderator-component',
    )

    assert mock_processing.times_called == 0


async def test_periodic_moderator_reset_happy_path(
        taxi_eats_moderation, mock_processing, mocked_time,
):
    mocked_time.sleep(61200)

    await taxi_eats_moderation.invalidate_caches()

    await taxi_eats_moderation.run_task(
        'distlock/periodic-reset-moderator-component',
    )

    assert mock_processing.times_called == 1
