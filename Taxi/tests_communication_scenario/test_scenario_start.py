import pytest

JOB_NAME = 'scenario-start-worker'


@pytest.mark.pgsql(
    'communication_scenario',
    files=['fill_scenarios.sql', 'test_scenario_start.sql'],
)
async def test_scenario_in_progress(
        taxi_communication_scenario, pgsql, testpoint, mock_ucommunications,
):
    @testpoint('run-steps/processed-step')
    def updated_row(data):
        updated_name = data.get('step')
        assert updated_name in wait_list
        wait_list.remove(updated_name)

    cursor = pgsql['communication_scenario'].cursor()
    cursor.execute('SELECT step FROM steps')
    wait_list = [item for (item,) in cursor]

    await taxi_communication_scenario.run_periodic_task(JOB_NAME)
    for _ in range(len(wait_list)):
        updated_row.wait_call()

    assert updated_row.times_called == 3
    assert not wait_list
