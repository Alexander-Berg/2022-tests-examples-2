import datetime as dt
import pathlib

import pytest


def _get_driver_activity_query():
    parent_path = pathlib.Path(__file__).parent.absolute()
    sql_file_path = f'{parent_path}/../../src/sql/select_driver_activity.sql'
    with open(sql_file_path) as sql_file:
        sql = sql_file.read()
    sql = sql.replace(f'$1', f'%(driver_id)s')
    sql = sql.replace(f'$2', f'%(min_created_at)s')
    sql = sql.replace(f'$3', f'%(max_created_at)s')
    sql = sql.replace(f'$4', f'%(min_event_at)s')
    sql = sql.replace(f'$5', f'%(max_event_at)s')
    sql = sql.replace(f'$6', f'%(sinces)s')
    sql = sql.replace(f'$7', f'%(tills)s')
    return sql


@pytest.mark.pgsql(
    'billing_time_events@1',
    files=['events_for_test_no_duplicates_when_event_join_with_payload.sql'],
)
@pytest.mark.now('2020-06-30T00:00:00.00000+00:00')
async def test_no_duplicates_when_joining_event_and_payload(pgsql):
    db_cursor = pgsql['billing_time_events@1'].cursor()
    query = _get_driver_activity_query()
    db_cursor.execute(
        query,
        {
            'driver_id': 'dbid_uuid1',
            'min_created_at': dt.datetime(
                2020, 6, 30, 10, 50, tzinfo=dt.timezone.utc,
            ),
            'max_created_at': dt.datetime(
                2020, 6, 30, 11, 10, tzinfo=dt.timezone.utc,
            ),
            'min_event_at': dt.datetime(
                2020, 6, 30, 9, 50, tzinfo=dt.timezone.utc,
            ),
            'max_event_at': dt.datetime(
                2020, 6, 30, 10, 10, tzinfo=dt.timezone.utc,
            ),
            'sinces': [
                dt.datetime(2020, 6, 30, 9, 50, tzinfo=dt.timezone.utc),
            ],
            'tills': [
                dt.datetime(2020, 6, 30, 10, 10, tzinfo=dt.timezone.utc),
            ],
        },
    )
    rows = list(db_cursor)
    assert len(rows) == 1
