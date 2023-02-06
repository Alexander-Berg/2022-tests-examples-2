import pytest


@pytest.mark.config(
    COMMUNICATION_SCENARIO_SCENARIOS={
        'push_push': {'steps': [], 'initial_steps': []},
        'asdasdasda': {'steps': [], 'initial_steps': []},
    },
)
async def test_db_not_empty(taxi_communication_scenario, taxi_config, pgsql):
    await taxi_communication_scenario.run_task('distlock/config-updater')
    response = await taxi_communication_scenario.get('/ping')
    assert response.status_code == 200
    cursor = pgsql['communication_scenario'].cursor()
    cursor.execute('SELECT name FROM scenarios;')
    assert len(taxi_config.get('COMMUNICATION_SCENARIO_SCENARIOS')) == len(
        list(cursor),
    )
