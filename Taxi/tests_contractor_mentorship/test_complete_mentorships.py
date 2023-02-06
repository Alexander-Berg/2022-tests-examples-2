import pytest

RETRIEVE_BY_PROFILES_RESPONSE = {
    'uniques': [
        {
            'park_driver_profile_id': 'sample_id',
            'data': {'unique_driver_id': 'mentoruid1'},
        },
    ],
}


@pytest.mark.now('2021-11-26T12:00:00+0000')
@pytest.mark.ydb(files=['insert_mentorships.sql'])
@pytest.mark.yt(
    schemas=['yt_finished_promocodes_schema.yaml'],
    static_table_data=['yt_finished_promocodes.yaml'],
)
async def test_complete_mentorships_ok(
        yt_apply, testpoint, taxi_contractor_mentorship, ydb,
):

    await taxi_contractor_mentorship.run_distlock_task(
        'complete-mentorships-distlock',
    )

    cursor = ydb.execute('SELECT * FROM status_transitions ORDER BY to')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 2
    assert cursor[0].rows[0]['to'] == b'failed'
    assert cursor[0].rows[0]['from'] == b'in_progress'
    assert cursor[0].rows[1]['to'] == b'succeeded'
    assert cursor[0].rows[1]['from'] == b'in_progress'


@pytest.mark.now('2021-11-26T12:00:00+0000')
@pytest.mark.ydb(files=['insert_completed_and_not_matched_mentorships.sql'])
@pytest.mark.yt(
    schemas=['yt_finished_promocodes_schema.yaml'],
    static_table_data=['yt_finished_promocodes.yaml'],
)
async def test_mentorships_dont_fail(
        yt_apply, testpoint, taxi_contractor_mentorship, ydb,
):

    await taxi_contractor_mentorship.run_distlock_task(
        'complete-mentorships-distlock',
    )

    cursor = ydb.execute('SELECT * FROM status_transitions ORDER BY to')
    assert len(cursor) == 1
    assert cursor[0].rows == []


@pytest.mark.now('2022-01-01T12:00:00+0000')
@pytest.mark.yt(
    schemas=['yt_finished_promocodes_schema.yaml'],
    static_table_data=['yt_finished_promocodes_nulls.yaml'],
)
async def test_complete_mentorships_with_nulls(
        yt_apply, testpoint, taxi_contractor_mentorship, ydb,
):

    await taxi_contractor_mentorship.run_distlock_task(
        'complete-mentorships-distlock',
    )

    cursor = ydb.execute('SELECT * FROM mentorships;')
    assert len(cursor) == 1
    assert cursor[0].rows == []
