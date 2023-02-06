import pytest


@pytest.mark.now('2021-11-26T12:00:00+0000')
@pytest.mark.ydb(files=['insert_unmatched_mentorships.sql'])
@pytest.mark.yt(
    schemas=['yt_import_mentorships_schema.yaml'],
    static_table_data=['yt_import_mentorships.yaml'],
)
@pytest.mark.config(
    CONTRACTOR_MENTORSHIP_START_DATE='2019-11-11T00:02:00+00:00',
)
async def test_import_mentorships_distlock_ok(
        yt_apply, taxi_contractor_mentorship, ydb,
):

    await taxi_contractor_mentorship.run_distlock_task(
        'import-mentorships-distlock',
    )

    cursor = ydb.execute('SELECT * FROM mentorships')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 2
    assert cursor[0].rows[0] == {
        'created_at': 1635679200000000,
        'id': b'1',
        'mentor_full_name': b'\xd0\x9f\xd0\xb0\xd0\xb2\xd0\xb5\xd0\xbb',
        'mentor_last_read_at': None,
        'mentor_park_driver_profile_id': (
            b'e7d892bc186c4be8836ba6173c746532_e49e1f6'
            b'2e55941b0813df09ea9d38380'
        ),
        'mentor_phone_pd_id': b'+79930053093_id',
        'mentor_unique_driver_id': b'5c91f663d0be228bce70fe727',
        'newbie_last_read_at': None,
        'newbie_park_driver_profile_id': (
            b'431b2fa719494cceb1dc3b2c35a346ff_c92063f'
            b'a946c4e4da94b4ab67e20b694'
        ),
        'newbie_unique_driver_id': b'6064c7f28fe28d5ce4f2f8cf',
        'original_connected_dttm': 1617616840000000,
        'status': b'matched',
        'country_id': b'rus',
    }
    cursor = ydb.execute('SELECT * FROM status_transitions;')
    assert len(cursor[0].rows) == 2

    cursor = ydb.execute(
        'SELECT * FROM status_transitions WHERE to == "matched" '
        'order by status_transitions.from',
    )
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 2
    assert cursor[0].rows[1]['from'] == b'requested'
    assert cursor[0].rows[1]['to'] == b'matched'


@pytest.mark.now('2021-11-26T12:00:00+0000')
@pytest.mark.ydb(files=['insert_already_matched_mentorships.sql'])
@pytest.mark.yt(
    schemas=['yt_import_mentorships_schema.yaml'],
    static_table_data=['yt_import_mentorships.yaml'],
)
@pytest.mark.config(
    CONTRACTOR_MENTORSHIP_START_DATE='2019-11-11T00:02:00+00:00',
)
async def test_import_mentorships_distlock_already_matched(
        yt_apply, taxi_contractor_mentorship, ydb,
):

    await taxi_contractor_mentorship.run_distlock_task(
        'import-mentorships-distlock',
    )

    cursor = ydb.execute('SELECT * FROM mentorships')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 2
    assert cursor[0].rows[0] == {
        'created_at': 1635679200000000,
        'id': b'1',
        'mentor_full_name': b'\xd0\x9f\xd0\xb0\xd0\xb2\xd0\xb5\xd0\xbb',
        'mentor_last_read_at': None,
        'mentor_park_driver_profile_id': (
            b'e7d892bc186c4be8836ba6173c746532_e49e1f6'
            b'2e55941b0813df09ea9d38380'
        ),
        'mentor_phone_pd_id': b'+79930053093_id',
        'mentor_unique_driver_id': b'5c91f663d0be228bce70fe727',
        'newbie_last_read_at': None,
        'newbie_park_driver_profile_id': (
            b'431b2fa719494cceb1dc3b2c35a346ff_c92063f'
            b'a946c4e4da94b4ab67e20b694'
        ),
        'newbie_unique_driver_id': b'6064c7f28fe28d5ce4f2f8cf',
        'original_connected_dttm': 1635679200000000,
        'status': b'matched',
        'country_id': b'rus',
    }

    cursor = ydb.execute('SELECT * FROM status_transitions;')

    assert len(cursor[0].rows) == 1

    cursor = ydb.execute(
        'SELECT * FROM status_transitions WHERE to == "matched"',
    )
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1
    assert cursor[0].rows[0]['from'] is None
    assert cursor[0].rows[0]['to'] == b'matched'


@pytest.mark.now('2021-11-26T12:00:00+0000')
@pytest.mark.yt(
    schemas=['yt_import_mentorships_schema.yaml'],
    static_table_data=['yt_import_mentorships.yaml'],
)
@pytest.mark.config(
    CONTRACTOR_MENTORSHIP_START_DATE='2021-11-11T00:02:00+00:00',
)
async def test_import_mentorships_distlock_only_new(
        yt_apply, taxi_contractor_mentorship, ydb,
):
    await taxi_contractor_mentorship.run_distlock_task(
        'import-mentorships-distlock',
    )

    cursor = ydb.execute('SELECT * FROM mentorships')
    assert len(cursor) == 1
    assert not cursor[0].rows


@pytest.mark.now('2022-01-01T12:00:00+0000')
@pytest.mark.yt(
    schemas=['yt_import_mentorships_schema.yaml'],
    static_table_data=['yt_import_mentorships_nulls.yaml'],
)
@pytest.mark.config(
    CONTRACTOR_MENTORSHIP_START_DATE='2019-11-11T00:02:00+00:00',
)
async def test_import_mentorships_with_nulls(
        yt_apply, taxi_contractor_mentorship, ydb,
):
    await taxi_contractor_mentorship.run_distlock_task(
        'import-mentorships-distlock',
    )

    cursor = ydb.execute('SELECT * FROM status_transitions;')
    assert cursor[0].rows == []
