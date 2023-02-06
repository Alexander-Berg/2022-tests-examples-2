import pytest


def get_upload_progress(cursor):
    cursor.execute(
        f"""
        SELECT id, type, status, current_row
        from cashback_levels.upload_progress;
        """,
    )
    return [*cursor]


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
@pytest.mark.yt(static_table_data=['yt_data.yaml'])
@pytest.mark.parametrize(
    ('pre_query', 'json_data', 'expected_result', 'query'),
    [
        pytest.param(
            f"""
            INSERT INTO cashback_levels.users
            (yandex_uid, current_used_level, current_earned_level, stage_id)
            VALUES ('idempotency_uid', 2, 2, 'stage1'),
                   ('idempotency_uid', 2, 2, 'stage2');
            """,
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/user_levels',
                'type': 'user_levels',
            },
            [
                ('111', 2, 1, 'stage1'),
                ('222', 4, 2, 'stage1'),
                ('idempotency_uid', 2, 2, 'stage1'),
                ('idempotency_uid', 2, 2, 'stage2'),
            ],
            f"""
            SELECT yandex_uid, current_used_level,
            current_earned_level, stage_id
            from cashback_levels.users;
            """,
            id='user_levels',
        ),
        pytest.param(
            f"""
            INSERT INTO cashback_levels.users_segments
            ( yandex_uid, segment, stage_id)
            VALUES ('idempotency_uid', 'idempotency_segment', 'stage1'),
                   ('idempotency_uid', 'idempotency_segment', 'stage2');
            """,
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/user_segments',
                'type': 'user_segments',
            },
            [
                ('111', 'segment1', 'stage1'),
                ('222', 'segment2', 'stage1'),
                ('idempotency_uid', 'idempotency_segment', 'stage1'),
                ('idempotency_uid', 'idempotency_segment', 'stage2'),
            ],
            f"""
            SELECT yandex_uid, segment, stage_id
            from cashback_levels.users_segments;
            """,
            id='user_segments',
        ),
        pytest.param(
            f"""
            INSERT INTO cashback_levels.segments_tasks
            ( segment, task_description_id, stage_id )
            VALUES ('idempotency_segment', 'idempotency_task', 'stage1'),
                   ('idempotency_segment', 'idempotency_task', 'stage2');
            """,
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/segments_tasks',
                'type': 'segments_tasks',
            },
            [
                ('segment1', 'task1', 'stage1'),
                ('segment2', 'task2', 'stage1'),
                ('idempotency_segment', 'idempotency_task', 'stage1'),
                ('idempotency_segment', 'idempotency_task', 'stage2'),
            ],
            f"""
            SELECT segment, task_description_id, stage_id
            from cashback_levels.segments_tasks;
            """,
            id='segments_tasks',
        ),
    ],
)
async def test_upload_stq_users_levels(
        yt_apply,  # do not remove
        stq_runner,
        taxi_cashback_levels,
        pgsql,
        json_data,
        pre_query,
        expected_result,
        query,
):
    cursor = pgsql['cashback_levels'].cursor()
    cursor.execute(pre_query)
    response = await taxi_cashback_levels.post(
        'v1/internal/admin/bulk_load_from_yt', json=json_data,
    )
    assert response.status_code == 200

    values = get_upload_progress(cursor)
    assert len(values) == 1
    new_upload_uuid = values[0][0]
    assert values[0] == (new_upload_uuid, json_data['type'], 'in_progress', 0)

    await stq_runner.cashback_levels_yt_bulk_upload.call(
        task_id=json_data['type'], kwargs={'bulk_upload_request': json_data},
    )

    values = get_upload_progress(cursor)
    assert len(values) == 1
    assert values[0] == (new_upload_uuid, json_data['type'], 'complete', 500)

    cursor.execute(query)
    values = [*cursor]
    assert set(expected_result) == set(values)


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
@pytest.mark.yt(static_table_data=['yt_data.yaml'])
@pytest.mark.parametrize(
    ('pre_query', 'json_data', 'expected_result', 'query'),
    [
        pytest.param(
            f"""
            INSERT INTO cashback_levels.users
            (yandex_uid, current_used_level, current_earned_level, stage_id)
            VALUES ('idempotency_uid', 2, 2, 'stage1'),
                   ('idempotency_uid', 2, 2, 'stage2');
            """,
            {
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_table': '//home/testsuite/user_levels',
                'type': 'user_levels',
            },
            [
                ('111', 2, 1, 'stage1'),
                ('222', 4, 2, 'stage1'),
                ('idempotency_uid', 2, 2, 'stage1'),
                ('idempotency_uid', 2, 2, 'stage2'),
            ],
            f"""
            SELECT yandex_uid, current_used_level,
            current_earned_level, stage_id
            from cashback_levels.users;
            """,
            id='offset',
        ),
    ],
)
async def test_upload_stq_previous_uploads_do_not_change(
        yt_apply,  # do not remove
        stq_runner,
        taxi_cashback_levels,
        pgsql,
        json_data,
        pre_query,
        expected_result,
        query,
):
    old_upload_data = (
        '62f4af85-52f9-43a9-924d-0260810dbc65',
        'user_levels',
        'complete',
        10,
    )
    cursor = pgsql['cashback_levels'].cursor()
    cursor.execute(pre_query)
    cursor.execute(
        f"""
        INSERT INTO cashback_levels.upload_progress
        (id, type, status, current_row)
        VALUES {old_upload_data};
        """,
    )
    response = await taxi_cashback_levels.post(
        'v1/internal/admin/bulk_load_from_yt', json=json_data,
    )
    assert response.status_code == 200

    values = get_upload_progress(cursor)
    assert len(values) == 2
    assert values[0] == old_upload_data
    new_upload_uuid = values[1][0]
    assert values[1] == (new_upload_uuid, 'user_levels', 'in_progress', 0)

    await stq_runner.cashback_levels_yt_bulk_upload.call(
        task_id=json_data['type'], kwargs={'bulk_upload_request': json_data},
    )

    values = get_upload_progress(cursor)
    assert len(values) == 2
    assert values[0] == old_upload_data
    assert values[1] == (new_upload_uuid, 'user_levels', 'complete', 500)

    cursor.execute(query)
    values = [*cursor]
    assert set(expected_result) == set(values)
