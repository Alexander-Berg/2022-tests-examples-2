import pytest

from tests_scooters_misc import utils


DISTLOCK_NAME = 'scooters-misc-compiled-rides-sender'


@pytest.mark.config(
    SCOOTERS_MISC_COMPILED_RIDES_SENDER_DISTLOCK={
        'sleep-time-ms': 200,
        'enabled': True,
    },
)
async def test_worker(taxi_scooters_misc, mockserver, generate_uuid, pgsql):
    @mockserver.json_handler(
        '/processing/v1/scooters/compiled_rides/create-event',
    )
    async def _create_event(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'compiled_ride:stub_session_id'
        )
        assert request.json == {
            'kind': 'created',
            'ride': {
                'session_id': 'stub_session_id',
                'vehicle_id': '537d15b4-b54b-47fc-a9e1-acd274153c9d',
                'price': 777,
                'duration_seconds': 111,
                'started_at': '2021-12-02T19:54:34+00:00',
                'finished_at': '2021-12-02T20:05:50+00:00',
                'point_start': {
                    'lat': 45.07289505004883,
                    'lon': 38.975948333740234,
                },
                'point_finish': {
                    'lat': 45.060691833496094,
                    'lon': 38.96168899536133,
                },
            },
            'version': 2,
        }
        return {'event_id': generate_uuid}

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)

    assert _create_event.times_called == 1
    assert (
        utils.get_drive_cursor(
            pgsql, name='compiled_rides_sender:compiled_rides',
        )
        == 492297
    )
