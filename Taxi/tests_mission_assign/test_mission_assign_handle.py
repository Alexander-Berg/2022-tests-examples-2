import pytest


@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': '2021-08-25T12:00:00+0000',
            'end_time': '2021-11-25T12:00:00+0000',
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
    },
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.parametrize(
    'json_data',
    [
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/doesnt_exist',
            },
            id='not_existing_folder',
        ),
        pytest.param(
            {
                'stage_id': 'stage-not-existing',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
            },
            id='not_existing_stage',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/bad-folder/wrong-segment-name',
            },
            id='not_existing_stage',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/wrong-table-schema',
            },
            id='wrong-table-schema',
        ),
    ],
)
async def test_mission_assign_handle_bad_request(
        yt_apply, taxi_cashback_levels, json_data,
):
    response = await taxi_cashback_levels.post(
        'v1/internal/admin/assign_tasks_to_segments', json=json_data,
    )
    assert response.status_code == 400


@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': '2021-08-25T12:00:00+0000',
            'end_time': '2021-11-25T12:00:00+0000',
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
    },
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.parametrize(
    'setup_params,json_data,status_code',
    [
        pytest.param(
            ['(\'stage1\', \'in_progress\')'],
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': True,
            },
            400,
            id='in_progress',
        ),
        pytest.param(
            ['(\'stage1\', \'failed\')'],
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': True,
            },
            200,
            id='failed',
        ),
        pytest.param(
            ['(\'stage1\', \'complete\')'],
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': True,
            },
            200,
            id='complete',
        ),
        pytest.param(
            [
                '(\'stage1\', \'complete\')',
                '(\'stage1\', \'failed\')',
                '(\'stage1\', \'failed\')',
            ],
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': True,
            },
            200,
            id='multiple',
        ),
        pytest.param(
            [
                '(\'stage1\', \'complete\')',
                '(\'stage1\', \'failed\')',
                '(\'stage1\', \'in_progress\')',
                '(\'stage1\', \'failed\')',
            ],
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': True,
            },
            400,
            id='multiple_with_in_progress',
        ),
        pytest.param(
            [
                '(\'stage1\', \'complete\')',
                '(\'stage1\', \'failed\')',
                '(\'stage2\', \'in_progress\')',
                '(\'stage1\', \'failed\')',
            ],
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': True,
            },
            400,
            id='in_progress_other_stage',
        ),
    ],
)
async def test_mission_assign_with_assigns_in_db(
        yt_apply,
        taxi_cashback_levels,
        pgsql,
        setup_params,
        json_data,
        status_code,
):

    cursor = pgsql['cashback_levels'].cursor()
    for params in setup_params:
        cursor.execute(
            f"""
            INSERT INTO cashback_levels.assign_progress
            (stage_id, status)
            VALUES {params};
            """,
        )
    response = await taxi_cashback_levels.post(
        'v1/internal/admin/assign_tasks_to_segments', json=json_data,
    )
    assert response.status_code == status_code


@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': '2021-08-25T12:00:00+0000',
            'end_time': '2021-11-25T12:00:00+0000',
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
    },
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.parametrize(
    'json_data',
    [
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': True,
            },
            id='simple',
        ),
    ],
)
async def test_mission_assign_handle(
        yt_apply, taxi_cashback_levels, pgsql, stq, json_data,
):
    response = await taxi_cashback_levels.post(
        'v1/internal/admin/assign_tasks_to_segments', json=json_data,
    )
    assert response.status_code == 200
    cursor = pgsql['cashback_levels'].cursor()
    cursor.execute(
        f"""
        SELECT id, status
        from cashback_levels.assign_progress
        where stage_id='{json_data['stage_id']}';
        """,
    )
    values = [*cursor]
    assert len(values) == 1
    assert values[0][1] == 'in_progress'

    assert stq.cashback_levels_segments_assign.times_called == 1

    task = stq.cashback_levels_segments_assign.next_call()
    assert task['id'] == json_data['stage_id']
    assert task['kwargs']['yt_folder'] == json_data['yt_folder']
    assert task['kwargs']['stage_id'] == json_data['stage_id']
    assert task['kwargs']['need_accept'] == json_data['need_accept']


@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': '2021-08-25T12:00:00+0000',
            'end_time': '2021-11-25T12:00:00+0000',
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
    },
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.parametrize(
    'segments_tasks_setup_params,json_data,status_code',
    [
        pytest.param(
            [
                '(\'some-segment-not-in-yt\', \'123\', \'stage1\')',
                '(\'segment_one\', \'123\', \'stage2\')',
            ],
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': False,
            },
            200,
            id='bad_segment_and_good_with_different_stage_id',
        ),
        pytest.param(
            ['(\'segment_one\', \'123\', \'stage1\')'],
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': False,
            },
            200,
            id='ok_segment',
        ),
        pytest.param(
            [
                '(\'segment_one\', \'123\', \'stage1\')',
                '(\'segment_two\', \'123\', \'stage1\')',
            ],
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': False,
            },
            200,
            id='ok_segments',
        ),
    ],
)
async def test_mission_assign_folder_doesnt_have_all_segments(
        yt_apply,
        taxi_cashback_levels,
        pgsql,
        segments_tasks_setup_params,
        json_data,
        status_code,
):
    cursor = pgsql['cashback_levels'].cursor()
    for data in segments_tasks_setup_params:
        cursor.execute(
            f"""
                INSERT INTO cashback_levels.segments_tasks
                (segment, task_description_id, stage_id)
                VALUES {data};
                """,
        )
    response = await taxi_cashback_levels.post(
        'v1/internal/admin/assign_tasks_to_segments', json=json_data,
    )
    assert response.status_code == status_code
