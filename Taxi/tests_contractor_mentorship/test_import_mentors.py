import pytest


@pytest.mark.now('2021-11-26T12:00:00+0000')
@pytest.mark.yt(
    schemas=['yt_update_mentors_schema.yaml'],
    static_table_data=['yt_update_mentors.yaml'],
)
async def test_update_mentors_distlock_ok(
        yt_apply, testpoint, taxi_contractor_mentorship, ydb,
):

    await taxi_contractor_mentorship.run_distlock_task(
        'import-mentors-distlock',
    )

    cursor = ydb.execute('SELECT * FROM mentors')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1
    assert cursor[0].rows[0]['phone'] == b'2bd6f485624742f0999360574bfeb9b6'


@pytest.mark.now('2021-11-26T12:00:00+0000')
@pytest.mark.ydb(files=['insert_outdated_mentor.sql'])
@pytest.mark.yt(
    schemas=['yt_update_mentors_schema.yaml'],
    static_table_data=['yt_update_mentors.yaml'],
)
async def test_update_mentors_distlock_outdated(
        yt_apply, testpoint, taxi_contractor_mentorship, ydb,
):

    await taxi_contractor_mentorship.run_distlock_task(
        'import-mentors-distlock',
    )

    cursor = ydb.execute('SELECT * FROM mentors')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1
    assert cursor[0].rows[0]['last_name'] == b'Igumenov'


@pytest.mark.now('2021-11-26T12:00:00+0000')
@pytest.mark.ydb(files=['insert_up_to_date_mentor.sql'])
@pytest.mark.yt(
    schemas=['yt_update_mentors_schema.yaml'],
    static_table_data=['yt_update_mentors.yaml'],
)
async def test_update_mentors_distlock_up_to_date(
        yt_apply, testpoint, taxi_contractor_mentorship, ydb,
):

    await taxi_contractor_mentorship.run_distlock_task(
        'import-mentors-distlock',
    )

    cursor = ydb.execute('SELECT * FROM mentors')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1
    assert cursor[0].rows[0]['last_name'] == b'Igumenov_uptodate'
