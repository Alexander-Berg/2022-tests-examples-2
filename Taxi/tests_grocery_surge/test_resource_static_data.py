import pytest


DEFAULT_STATIC_DATA = {'key': 'value', 'load_level': 12.4}
SPECIAL_STATIC_DATA = {
    'special_key': 420,
    'another_one': {'foo': 'bar'},
    'load_level': 14.5,
}


@pytest.mark.now('2020-07-07T00:00:00Z')
@pytest.mark.experiments3(
    name='grocery_surge_resource_static_data',
    consumers=['grocery_surge/common_resource'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'special',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': '1',
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                },
            },
            'value': SPECIAL_STATIC_DATA,
        },
    ],
    default_value=DEFAULT_STATIC_DATA,
    is_config=True,
)
@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'test_pipeline'}]},
    is_config=True,
)
@pytest.mark.parametrize(
    'depot_id, expected_data',
    [('2', DEFAULT_STATIC_DATA), ('1', SPECIAL_STATIC_DATA)],
)
async def test_resource_static_data(
        taxi_grocery_surge,
        admin_pipeline,
        stq,
        stq_runner,
        mocked_time,
        testpoint,
        depot_id,
        expected_data,
):
    @testpoint('wrap_static_data_resource_output')
    def static_data_result(val):
        assert val == expected_data

    @testpoint('finished_pipeline_calculation')
    def surge_calculated(data):
        assert data == {'load_level': expected_data['load_level']}

    task_id = 'task_id'
    await stq_runner.grocery_surge_calculate_pipeline.call(
        task_id=task_id,
        kwargs={'pipeline': 'test_pipeline', 'depot_id': depot_id},
    )
    assert static_data_result.times_called == 1
    assert surge_calculated.times_called == 1
