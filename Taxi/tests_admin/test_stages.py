import pytest

STAGES_DESCRIPTION = {
    'stage1': {
        'start_time': '2021-08-25T12:00:00+0000',
        'end_time': '2021-11-25T12:00:00+0000',
        'stage_id': 'stage1',
        'next_stage_id': 'stage2',
        'sort': 'random',
        'top_size': 2,
        'name': 'Some stage name',
        'description': 'Some stage descr',
    },
    'stage2': {
        'start_time': '2021-08-25T12:00:00+0000',
        'end_time': '2021-11-25T12:00:00+0000',
        'stage_id': 'stage2',
        'next_stage_id': 'stage3',
    },
}


@pytest.mark.config(CASHBACK_LEVELS_STAGES_DESCRIPTION=STAGES_DESCRIPTION)
async def test_admin_stage_handle(taxi_cashback_levels, compare_dct_lists):
    response = await taxi_cashback_levels.get(f'admin/stages')
    assert response.status == 200
    compare_dct_lists(
        response.json()['payload']['stages'],
        [
            {
                'start_time': '2021-08-25T12:00:00+0000',
                'end_time': '2021-11-25T12:00:00+0000',
                'id': 'stage1',
                'next_stage_id': 'stage2',
                'sort': 'random',
                'top_size': 2,
                'name': 'Some stage name',
                'description': 'Some stage descr',
            },
            {
                'start_time': '2021-08-25T12:00:00+0000',
                'end_time': '2021-11-25T12:00:00+0000',
                'id': 'stage2',
                'next_stage_id': 'stage3',
            },
        ],
    )
