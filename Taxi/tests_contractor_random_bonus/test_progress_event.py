import pytest

PARK_ID = 'someParkId'
DRIVER_ID = 'someDriverId'
UNIQUE_DRIVER_ID = 'uniqueDriverId'
SOME_ISO = '2020-11-11T11:11:11+03:00'


async def test_progress_event_ok(stq_runner, mockserver):
    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    async def _event_new(request):
        assert request.json['type'] == 'lootbox'
        assert request.json['descriptor']['type'] == 'progress_full'
        assert request.json['extra_data'] == {'is_first': True}
        return {}

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    async def _unique_drivers(request):
        assert request.json['profile_id_in_set'][0] == f'{PARK_ID}_{DRIVER_ID}'
        return {
            'uniques': [
                {
                    'park_driver_profile_id': f'{PARK_ID}_{DRIVER_ID}',
                    'data': {'unique_driver_id': UNIQUE_DRIVER_ID},
                },
            ],
        }

    await stq_runner.random_bonus_progress_events.call(
        task_id='some_task_id', args=[PARK_ID, DRIVER_ID, True, SOME_ISO],
    )

    assert _unique_drivers.times_called == 1
    assert _event_new.times_called == 1


@pytest.mark.parametrize(
    'ud_response',
    [
        ({'uniques': []}),
        ({'uniques': [{'park_driver_profile_id': f'{PARK_ID}_{DRIVER_ID}'}]}),
    ],
)
async def test_progress_event_unique_fail(stq_runner, mockserver, ud_response):
    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    async def _event_new(request):
        return {}

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    async def _unique_drivers(request):
        return ud_response

    await stq_runner.random_bonus_progress_events.call(
        task_id='some_task_id',
        args=[PARK_ID, DRIVER_ID, True, SOME_ISO],
        expect_fail=True,
    )

    assert _unique_drivers.times_called == 1
    assert _event_new.times_called == 0


async def test_progress_event_dms_fail(stq_runner, mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    async def _unique_drivers(request):
        assert request.json['profile_id_in_set'][0] == f'{PARK_ID}_{DRIVER_ID}'
        return {
            'uniques': [
                {
                    'park_driver_profile_id': f'{PARK_ID}_{DRIVER_ID}',
                    'data': {'unique_driver_id': UNIQUE_DRIVER_ID},
                },
            ],
        }

    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    async def _event_new(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    await stq_runner.random_bonus_progress_events.call(
        task_id='some_task_id', args=[PARK_ID, DRIVER_ID, True, SOME_ISO],
    )

    assert _unique_drivers.times_called == 1
    assert mock_stq_reschedule.times_called == 1
