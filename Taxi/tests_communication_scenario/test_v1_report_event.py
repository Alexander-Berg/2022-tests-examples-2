import pytest


@pytest.mark.pgsql(
    'communication_scenario',
    files=['fill_scenarios.sql', 'test_report_event.sql'],
)
async def test_success(taxi_communication_scenario, testpoint):
    @testpoint('run-steps/processed-step')
    def processed_step(data):
        assert data.get('waiting_event_id') == event_id

    event_id = '0xFFFF'
    response = await taxi_communication_scenario.get(
        'v1/report-event',
        params={'event_id': event_id, 'event_name': 'error'},
    )
    await processed_step.wait_call()
    assert response.status_code == 200


@pytest.mark.pgsql(
    'communication_scenario',
    files=['fill_scenarios.sql', 'test_report_event.sql'],
)
async def test_invalid_id(taxi_communication_scenario):
    response = await taxi_communication_scenario.get(
        'v1/report-event',
        params={'event_id': 'invalid_id', 'event_name': 'error'},
    )
    assert response.status_code == 200
