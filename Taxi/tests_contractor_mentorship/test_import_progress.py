import pytest


@pytest.mark.now('2021-11-26T12:00:00+0000')
@pytest.mark.ydb(files=['insert_matching_only.sql'])
@pytest.mark.yt(
    schemas=['yt_update_results_schema.yaml'],
    static_table_data=['yt_update_results.yaml'],
)
async def test_update_results_distlock_ok(
        yt_apply, testpoint, taxi_contractor_mentorship, ydb,
):

    await taxi_contractor_mentorship.run_distlock_task(
        'import-results-distlock',
    )

    cursor = ydb.execute('SELECT * FROM results')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1


@pytest.mark.now('2021-11-26T12:00:00+0000')
@pytest.mark.yt(
    schemas=['yt_update_results_schema.yaml'],
    static_table_data=['yt_update_results.yaml'],
)
async def test_update_results_distlock_no_matching(
        yt_apply, testpoint, taxi_contractor_mentorship, ydb,
):

    await taxi_contractor_mentorship.run_distlock_task(
        'import-results-distlock',
    )

    cursor = ydb.execute('SELECT * FROM results')
    assert len(cursor) == 1
    assert cursor[0].rows == []


@pytest.mark.now('2021-11-26T12:00:00+0000')
@pytest.mark.ydb(files=['insert_results_and_matching.sql'])
@pytest.mark.yt(
    schemas=['yt_update_results_schema.yaml'],
    static_table_data=['yt_update_results.yaml'],
)
async def test_update_results_distlock_already_has_result(
        yt_apply, testpoint, taxi_contractor_mentorship, ydb,
):
    cursor = ydb.execute('SELECT * FROM results')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1
    assert cursor[0].rows[0] == {
        'avg_dp_14d': b'100',
        'avg_dp_7d': b'100',
        'correct_answers': b'0',
        'mentorship_id': b'1',
        'passed_test_flg': 0,
        'rate_avg_14d': b'5',
        'rate_avg_7d': b'5',
        'sh_14d': b'3',
        'sh_7d': b'3',
    }

    cursor = ydb.execute('SELECT * FROM status_transitions')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 2
    original_status_created_at = cursor[0].rows[1]['created_at']

    await taxi_contractor_mentorship.run_distlock_task(
        'import-results-distlock',
    )
    cursor = ydb.execute('SELECT * FROM results')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1
    assert cursor[0].rows[0] == {
        'avg_dp_14d': b'88',
        'avg_dp_7d': b'99',
        'correct_answers': b'12',
        'mentorship_id': b'1',
        'passed_test_flg': 1,
        'rate_avg_14d': b'4.66',
        'rate_avg_7d': b'4.98',
        'sh_14d': b'5',
        'sh_7d': b'5',
    }
    cursor = ydb.execute('SELECT * FROM status_transitions')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 2
    assert cursor[0].rows[0]['mentorship_id'] == b'1'
    assert cursor[0].rows[0]['from'] == b'matched'
    assert cursor[0].rows[0]['to'] == b'in_progress'
    assert cursor[0].rows[0]['created_at'] == original_status_created_at


@pytest.mark.now('2022-01-01T12:00:00+0000')
@pytest.mark.yt(
    schemas=['yt_update_results_schema.yaml'],
    static_table_data=['yt_update_results_nulls.yaml'],
)
async def test_update_results_with_nulls(
        yt_apply, testpoint, taxi_contractor_mentorship, ydb,
):

    await taxi_contractor_mentorship.run_distlock_task(
        'import-results-distlock',
    )

    cursor = ydb.execute('SELECT * FROM results')
    assert len(cursor) == 1
    assert cursor[0].rows == []
