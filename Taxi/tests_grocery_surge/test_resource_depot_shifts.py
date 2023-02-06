import pytest


DEPOT_SHIFTS = {
    'shifts': [
        {
            'performer_id': 'dbid_uuid_1',
            'shift_id': 'some_shift_id_1',
            'shift_type': 'eats',
            'shift_status': 'in_progress',
            'started_at': '2020-07-06T21:00:00+00:00',
            'paused_at': '2020-07-06T22:00:00+00:00',
            'unpauses_at': '2020-07-06T23:00:00+00:00',
            'closes_at': '2020-07-07T02:58:00+00:00',
            'updated_ts': '2020-07-06T23:00:00+00:00',
        },
        {
            'performer_id': 'dbid_uuid_2',
            'shift_id': 'some_shift_id_2',
            'shift_type': 'wms',
            'shift_status': 'waiting',
            'started_at': '2020-07-07T03:00:00+00:00',
        },
    ],
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
async def test_resources(stq_runner, mockserver, testpoint):
    depot_id = '1'

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v1/shifts/shifts-info',
    )
    def _g_checkins_shifts(request):
        return DEPOT_SHIFTS

    @testpoint('wrap_depot_shifts_resource_output')
    def depot_shifts_result(val):
        assert val == DEPOT_SHIFTS

    task_id = 'task_id'
    await stq_runner.grocery_surge_calculate_pipeline.call(
        task_id=task_id,
        kwargs={'pipeline': 'test_pipeline', 'depot_id': depot_id},
    )

    assert depot_shifts_result.times_called == 1
