import pytest


DEPOT_ID = '1'

COOKING_TIME = {
    'exp_list': [],
    'request_id': DEPOT_ID,
    'predicted_times': [{'id': 0, 'cooking_time': 155}],
}


@pytest.mark.now('2022-03-23T12:00:00Z')
@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'test_pipeline'}]},
    is_config=True,
)
async def test_resource_cooking_eta(
        mockserver, stq_runner, taxi_config, testpoint,
):
    @mockserver.json_handler(
        '/umlaas-grocery-eta/internal/umlaas-grocery-eta/v1/depot-eta',
    )
    def _umlaas_grocery_eta_depot_eta(request):
        return {'cooking_time': 156}

    @testpoint('cooking_eta_resource_output')
    def cooking_eta_result(val):
        assert val == {DEPOT_ID: {'cooking_time': 156}}

    await stq_runner.grocery_surge_calculate_pipeline.call(
        task_id='task_id',
        kwargs={'pipeline': 'test_pipeline', 'depot_id': DEPOT_ID},
    )

    assert cooking_eta_result.times_called == 1
    assert _umlaas_grocery_eta_depot_eta.times_called == 1
