import pytest


@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'calc_surge'}]},
    is_config=True,
)
@pytest.mark.experiments3(
    name='grocery_surge_delivery_type_to_js_pipeline_matching',
    consumers=['grocery_surge/js_pipeline_calculator'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'init': {
                    'arg_name': 'delivery_type',
                    'set_elem_type': 'string',
                    'set': ['pedestrian', 'yandex_taxi'],
                },
                'type': 'in_set',
            },
            'value': {'pipeline': 'calc_surge'},
        },
    ],
    is_config=True,
)
async def test_surge_calculated_event(
        taxi_grocery_surge, stq, stq_runner, testpoint, published_events,
):
    @testpoint('finished_pipeline_calculation')
    def surge_calculated(data):
        assert data == {'load_level': 12.3}

    await taxi_grocery_surge.enable_testpoints()

    task_id = 'task_id'
    depot_id = '1'
    pipeline = 'calc_surge'
    await stq_runner.grocery_surge_calculate_pipeline.call(
        task_id=task_id, kwargs={'pipeline': pipeline, 'depot_id': depot_id},
    )
    await surge_calculated.wait_call()
    assert stq.grocery_surge_calculate_pipeline.times_called == 1

    # wait logbroker publish
    assert (await published_events.wait('grocery-surge-calculated'))[1] == {
        'depot_id': depot_id,
        'load_level': 12.3,
        'pipeline': pipeline,
        'delivery_type': ['pedestrian', 'yandex_taxi'],
        'meta': {},
    }
