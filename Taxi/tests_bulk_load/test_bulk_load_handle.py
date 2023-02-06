import pytest


@pytest.mark.parametrize(
    'json_data',
    [
        pytest.param(
            {
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/user_levels',
                'type': 'user_levels',
            },
            id='no_stage',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_table': '//home/testsuite/user_levels',
                'type': 'user_levels',
            },
            id='no_cluster',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'type': 'user_levels',
            },
            id='no_table',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/user_levels',
            },
            id='no_type',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'kek_hahn',
                'yt_table': '//home/testsuite/user_levels',
                'type': 'user_levels',
            },
            id='bad_cluster',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/user_levels',
                'type': 'kekeke',
            },
            id='bad_type',
        ),
    ],
)
async def test_handle_bad_input(taxi_cashback_levels, json_data):
    response = await taxi_cashback_levels.post(
        'v1/internal/admin/bulk_load_from_yt', json=json_data,
    )
    assert response.status_code == 400


async def test_no_stage_in_config(taxi_cashback_levels):
    response = await taxi_cashback_levels.post(
        'v1/internal/admin/bulk_load_from_yt',
        json={
            'stage_id': 'stage1',
            'yt_cluster': 'hahn',
            'yt_table': '//home/testsuite/user_levels',
            'type': 'user_levels',
        },
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
@pytest.mark.now('2021-09-25T12:00:00+0000')
async def test_handle_not_existing_table(taxi_cashback_levels):
    response = await taxi_cashback_levels.post(
        'v1/internal/admin/bulk_load_from_yt',
        json={
            'stage_id': 'stage1',
            'yt_cluster': 'hahn',
            'yt_table': '//home/testsuite/kekekek',
            'need_accept': True,
            'type': 'user_levels',
        },
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
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.parametrize(
    'json_data',
    [
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/user_levels_bad_schema0',
                'type': 'user_levels',
            },
            id='bad_column_name',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/user_levels_bad_schema1',
                'type': 'user_levels',
            },
            id='missing_column',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/user_levels_bad_schema2',
                'type': 'user_levels',
            },
            id='bad_column_type',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/bad-folder/wrong-columns-order',
                'type': 'user_levels',
            },
            id='wrong_columns_order',
        ),
    ],
)
async def test_handle_bad_table_schema(
        yt_apply, taxi_cashback_levels, json_data,
):
    response = await taxi_cashback_levels.post(
        'v1/internal/admin/bulk_load_from_yt', json=json_data,
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'Bad Request. Invalid yt base schema'


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
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.parametrize(
    'json_data',
    [
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/user_levels',
                'type': 'user_levels',
            },
            id='user_levels',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/user_segments',
                'type': 'user_segments',
            },
            id='user_segments',
        ),
        pytest.param(
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/segments_tasks',
                'type': 'segments_tasks',
            },
            id='segments_tasks',
        ),
    ],
)
async def test_handle_different_types(
        yt_apply, taxi_cashback_levels, pgsql, stq, json_data,
):
    response = await taxi_cashback_levels.post(
        'v1/internal/admin/bulk_load_from_yt', json=json_data,
    )
    assert response.status_code == 200
    cursor = pgsql['cashback_levels'].cursor()
    cursor.execute(
        f"""
        SELECT status
        from cashback_levels.upload_progress
        where type='{json_data['type']}';
        """,
    )
    values = [*cursor]
    assert len(values) == 1
    assert values[0] == ('in_progress',)

    assert stq.cashback_levels_yt_bulk_upload.times_called == 1

    task = stq.cashback_levels_yt_bulk_upload.next_call()
    assert task['kwargs']['bulk_upload_request'] == json_data
