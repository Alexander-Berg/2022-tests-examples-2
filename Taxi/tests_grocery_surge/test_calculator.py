import pytest


@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'calc_surge'}]},
    is_config=True,
)
async def test_pipeline_calculating(
        taxi_grocery_surge, stq, stq_runner, testpoint,
):
    @testpoint('finished_pipeline_calculation')
    def surge_calculated(data):
        assert data == {'load_level': 12.3}

    await taxi_grocery_surge.enable_testpoints()

    task_id = 'task_id'
    await stq_runner.grocery_surge_calculate_pipeline.call(
        task_id=task_id, kwargs={'pipeline': 'calc_surge', 'depot_id': '1'},
    )
    await surge_calculated.wait_call()
    assert stq.grocery_surge_calculate_pipeline.times_called == 1
