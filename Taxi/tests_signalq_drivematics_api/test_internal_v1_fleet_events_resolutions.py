import pytest


ENDPOINT = '/internal/signalq-drivematics-api/v1/fleet/events/resolutions'


@pytest.mark.config(
    SIGNALQ_DRIVEMATICS_API_RESOLUTION_SYNC_FLEET_TO_DM_SETTINGS={
        'stq_try_seconds': 86400,
    },
)
async def test_internal_v1_fleet_events_resolutions(
        taxi_signalq_drivematics_api, mockserver, stq, stq_runner,
):
    @mockserver.json_handler(
        '/ext-drivematics/api/signalq/trace/tag/resolution/set',
    )
    def post(request):
        assert request.json['serial_number'] == 'ab1'
        assert request.json['resolution'] == 'wrong_event'
        assert request.json['event_id'] == 'evid1'
        return mockserver.make_response(json={}, status=200)

    response = await taxi_signalq_drivematics_api.post(
        ENDPOINT,
        json={
            'serial_number': 'ab1',
            'resolution': 'wrong_event',
            'event_id': 'evid1',
            'event_at': 1652721891,
        },
    )
    assert response.status_code == 200, response.text
    assert (
        stq.signalq_drivematics_api_fleet_to_dm_resolutions.times_called == 1
    )
    stq_call = stq.signalq_drivematics_api_fleet_to_dm_resolutions.next_call()
    await stq_runner.signalq_drivematics_api_fleet_to_dm_resolutions.call(
        task_id=stq_call['id'],
        args=stq_call['args'],
        kwargs=stq_call['kwargs'],
    )
    assert post.times_called == 1
