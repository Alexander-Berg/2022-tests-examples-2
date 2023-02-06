import datetime
import json

import pytest


def convert_datetime_to_yt_format(timestamp: str) -> str:
    return datetime.datetime.strptime(
        timestamp, '%Y-%m-%dT%H:%M:%S%z',
    ).strftime('%Y-%m-%d %H:%M:%S')


def yt_mentors_table_cursor(db):
    rows = db.select_rows(
        'SELECT cursor FROM grocery_performer_mentorship.cursors '
        'WHERE name = \'yt_mentors_table\';',
    )
    assert len(rows) == 1
    return json.loads(rows[0][0])


def mentors(db):
    return db.select(
        ['mentor_id', 'mentor_shifts_count', 'status', 'updated'], 'mentors',
    )


def insert_cursor(db, cursor):
    meta_cursor = json.dumps(cursor)
    db.execute(
        'INSERT INTO grocery_performer_mentorship.cursors(name, cursor)'
        'VALUES (%s, %s)',
        ('yt_mentors_table', meta_cursor),
    )


def updated_ts(ms_ts):
    return datetime.datetime.fromtimestamp(
        ms_ts / 1000.0, tz=datetime.timezone.utc,
    )


NOW = datetime.datetime.now(datetime.timezone.utc)

SYNC_SETTINGS_CONFIG = {
    'enabled': True,
    'chunk_size': 10,
    'yt_read_timeout': 3000,
    'sync_period_seconds': 60,
    'yt_table_path': '//home/testsuite/mentors',
}


@pytest.mark.config(
    GROCERY_PERFORMER_MENTORSHIP_MENTORS_SYNC_SETTINGS=SYNC_SETTINGS_CONFIG,
)
@pytest.mark.yt(
    schemas=['yt_mentors_schema.yaml'],
    dyn_table_data=['yt_mentors_basic.yaml'],
)
@pytest.mark.now(NOW.isoformat())
async def test_basic(taxi_grocery_performer_mentorship, yt_apply, db):
    await taxi_grocery_performer_mentorship.invalidate_caches()

    await taxi_grocery_performer_mentorship.run_periodic_task(
        'mentors-sync-periodic',
    )
    assert mentors(db) == [
        {
            'mentor_id': '123_001',
            'mentor_shifts_count': 0,
            'status': 'active',
            'updated': updated_ts(1647000373),
        },
        {
            'mentor_id': '123_002',
            'mentor_shifts_count': 0,
            'status': 'inactive',
            'updated': updated_ts(1647000373),
        },
    ]

    assert yt_mentors_table_cursor(db) == {
        'last_dbid_uuid': '123_002',
        'last_update': 1647000373,
    }


@pytest.mark.config(
    GROCERY_PERFORMER_MENTORSHIP_MENTORS_SYNC_SETTINGS=SYNC_SETTINGS_CONFIG,
)
@pytest.mark.yt(
    schemas=['yt_mentors_schema.yaml'],
    dyn_table_data=['yt_mentors_basic.yaml'],
)
@pytest.mark.now(NOW.isoformat())
async def test_update_by_id(taxi_grocery_performer_mentorship, yt_apply, db):
    insert_cursor(db, {'last_update': 1647000373, 'last_dbid_uuid': '123_001'})
    await taxi_grocery_performer_mentorship.invalidate_caches()
    await taxi_grocery_performer_mentorship.run_periodic_task(
        'mentors-sync-periodic',
    )
    assert mentors(db) == [
        {
            'mentor_id': '123_002',
            'mentor_shifts_count': 0,
            'status': 'inactive',
            'updated': updated_ts(1647000373),
        },
    ]
    assert yt_mentors_table_cursor(db) == {
        'last_dbid_uuid': '123_002',
        'last_update': 1647000373,
    }


@pytest.mark.config(
    GROCERY_PERFORMER_MENTORSHIP_MENTORS_SYNC_SETTINGS=SYNC_SETTINGS_CONFIG,
)
@pytest.mark.yt(
    schemas=['yt_mentors_schema.yaml'],
    dyn_table_data=['yt_mentors_deleted.yaml'],
)
@pytest.mark.now(NOW.isoformat())
async def test_update_deleted(taxi_grocery_performer_mentorship, yt_apply, db):
    insert_cursor(db, {'last_update': 1647000373, 'last_dbid_uuid': '123_001'})
    await taxi_grocery_performer_mentorship.invalidate_caches()
    await taxi_grocery_performer_mentorship.run_periodic_task(
        'mentors-sync-periodic',
    )
    assert mentors(db) == [
        {
            'mentor_id': '123_002',
            'mentor_shifts_count': 0,
            'status': 'deleted',
            'updated': updated_ts(1650600373),
        },
    ]
    assert yt_mentors_table_cursor(db) == {
        'last_dbid_uuid': '123_002',
        'last_update': 1650600373,
    }
