import pytest

ENDPOINT = '/drivematics/signalq-drivematics-api/v1/events/resolutions'


@pytest.mark.parametrize('event_id', ['ev1', 'ev2'])
async def test_drivematics_v1_event_resolutions(
        taxi_signalq_drivematics_api, mockserver, stq, stq_runner, event_id,
):
    @mockserver.json_handler(
        '/signal-device-api/internal/signal-device-api/v1/events/resolutions',
    )
    def post(request):
        assert request.json['serial_number'] == 'ab1'
        assert request.json['resolution'] == 'wrong_event'
        assert request.json['event_id'] == event_id
        if event_id == 'ev1':
            return mockserver.make_response(
                json={'code': '404', 'message': 'event not found'}, status=404,
            )
        return mockserver.make_response(json={}, status=200)

    response = await taxi_signalq_drivematics_api.post(
        ENDPOINT,
        json={
            'serial_number': 'ab1',
            'resolution': 'wrong_event',
            'event_id': event_id,
        },
    )
    assert response.status_code == 200, response.text
    assert (
        stq.signalq_drivematics_api_dm_to_fleet_resolutions.times_called == 1
    )
    stq_call = stq.signalq_drivematics_api_dm_to_fleet_resolutions.next_call()
    await stq_runner.signalq_drivematics_api_dm_to_fleet_resolutions.call(
        task_id=stq_call['id'],
        args=stq_call['args'],
        kwargs=stq_call['kwargs'],
    )
    assert post.times_called == 1
