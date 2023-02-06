# pylint: disable=redefined-outer-name,unused-variable
import pytest

from taxi.util import dates

from driver_event_detector.generated.cron import run_cron


@pytest.mark.now('2020-03-21 10:00:00')
@pytest.mark.pgsql(
    'driver_event_detector', files=['fill_pg_matched_drivers.sql'],
)
async def test_update_matched_drivers(pgsql, patch):
    plugin_path = (
        'driver_event_detector.generated.cron.'
        'yt_wrapper.plugin.AsyncYTClient'
    )

    @patch(plugin_path + '.read_table')
    async def yt_read_table(*args, **kwargs):
        return [
            {
                '_id': '0000ab732bcee0b3b6fa6977e45fdd71',
                'driver_ids': ['52b1fd1415a72575a42dbe591'],
                'udid': None,
                'dbid_uuids': [],
            },
            {
                '_id': '0000ab732bcee0b3b6fa6977e45fdd72',
                'driver_ids': ['52b1fd1415a72575a42dbe592'],
                'udid': 'test_udid',
                'dbid_uuids': ['test_dbid_uuid'],
            },
        ]

    await run_cron.main(
        ['driver_event_detector.crontasks.update_matched_drivers', '-t', '0'],
    )

    cursor = pgsql['driver_event_detector'].cursor()
    cursor.execute('SELECT * FROM driver_event_detector.matched_drivers ')

    num_rows = 0
    for row in cursor:
        if row[0] == '0000ab732bcee0b3b6fa6977e45fdd72':
            assert row[1] == ['52b1fd1415a72575a42dbe592']
            assert row[2] == dates.utcnow()
            assert row[3] == 'test_udid'
            assert row[4] == ['test_dbid_uuid']
        else:
            assert row[0] == '0000ab732bcee0b3b6fa6977e45fdd71'
            assert row[1] == ['52b1fd1415a72575a42dbe591']
            assert row[2] == dates.utcnow()
            assert row[3] is None
            assert row[4] == []
        num_rows += 1

    assert num_rows == 2
    cursor.close()
