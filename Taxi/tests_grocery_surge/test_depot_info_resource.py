import pytest


def make_depot_info(full_info):
    return {
        'country_iso2': full_info['country_iso2'],
        'country_iso3': full_info['country_iso3'],
        'depot_id': full_info['legacy_depot_id'],
        'location': full_info['location'],
        'region_id': full_info['region_id'],
        'timezone': full_info['timezone'],
    }


@pytest.mark.now('2020-07-07T00:00:00Z')
@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'test_pipeline'}]},
    is_config=True,
)
async def test_resources(stq_runner, testpoint, grocery_depots):
    depot_id = '1'

    depot = grocery_depots.depots()[depot_id]

    @testpoint('wrap_depot_info_resource_output')
    def depot_info_result(val):
        assert val == make_depot_info(depot.get_json())

    task_id = 'task_id'
    await stq_runner.grocery_surge_calculate_pipeline.call(
        task_id=task_id,
        kwargs={'pipeline': 'test_pipeline', 'depot_id': depot_id},
    )

    assert depot_info_result.times_called == 1
