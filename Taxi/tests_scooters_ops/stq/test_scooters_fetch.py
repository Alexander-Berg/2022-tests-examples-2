import pytest

from tests_scooters_ops import db_utils

RESPONSES = {
    'dead': 'car_details/response_dead.json',
    'battery_low*-dead': 'car_details/response_battery_low.json',
}


@pytest.mark.experiments3(filename='exp3_scooters_workflows.json')
async def test_simple(stq_runner, pgsql, mockserver, load_json, stq):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def car_details(request):
        return load_json(filename=RESPONSES[request.query['tags_filter']])

    await stq_runner.scooters_fetch.call(task_id='task_id')

    assert car_details.times_called == 2
    drafts = db_utils.get_drafts(
        pgsql, fields=['typed_extra', 'type', 'status'],
    )
    assert drafts == [
        {
            'type': 'recharge',
            'status': 'pending',
            'typed_extra': {'vehicle_id': 's_id1'},
        },
        {
            'type': 'recharge',
            'status': 'pending',
            'typed_extra': {'vehicle_id': 's_id2'},
        },
        {
            'type': 'resurrect',
            'status': 'pending',
            'typed_extra': {'vehicle_id': 's_id3'},
        },
    ]

    assert stq.scooters_ops_process_draft.times_called == 6


@pytest.mark.experiments3(filename='exp3_scooters_workflows.json')
async def test_repeat(stq_runner, pgsql, mockserver, load_json, stq):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def car_details(request):
        return load_json(filename=RESPONSES[request.query['tags_filter']])

    await stq_runner.scooters_fetch.call(task_id='task_id')

    assert sorted(
        db_utils.get_drafts(pgsql, fields=['draft_id'], flatten=True),
    ) == ['s_id1_t_id1', 's_id2_t_id3', 's_id3_t_id6']

    await stq_runner.scooters_fetch.call(task_id='task_id')

    assert sorted(
        db_utils.get_drafts(pgsql, fields=['draft_id'], flatten=True),
    ) == ['s_id1_t_id1', 's_id2_t_id3', 's_id3_t_id6']

    assert stq.scooters_ops_process_draft.times_called == 6

    assert car_details.times_called == 4  # 4 because 2 workflows
