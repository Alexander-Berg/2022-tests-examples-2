# pylint: disable=unused-variable
import dateutil.parser
import pytest

from signal_device_api_worker.generated.cron import run_cron  # noqa F401
from test_signal_device_api_worker import conftest as tst
from . import test_photos_and_videos_data


CRON_PARAMS = [
    'signal_device_api_worker.crontasks.external_photos_cleanup',
    '-t',
    '0',
]

DB_CHECK_QUERY = """
    SELECT
      last_deleted_event_type,
      last_deleted_external_photo_at,
      last_deleted_video_at,
      last_deleted_photo_at,
      last_deleted_external_video_at,
      last_deleted_external_photo_event_id
    FROM signal_device_api.last_videos_and_photos_deleted;
    """


@pytest.mark.config(
    SIGNAL_DEVICE_API_WORKER_PHOTOS_CLEANUP_SETTINGS={
        '__default__': 1,
        'smoking': 2,
        'distraction': 5,
        'some_unreal': 1,
        'fart': 4,
        'seatbelt': 6,
        'sleep': 7,
    },
    SIGNAL_DEVICE_API_WORKER_S3_DELETE_OBJECTS_V2={
        'delete_objects_parallel_requests_amount': 5,
        'delete_objects_total_requests_amount': 5,
        'delete_objects_keys_amount': 2,
        'delete_objects_delay_seconds': 1,
    },
    SIGNAL_DEVICE_API_WORKER_YT_PATHS_V4={
        'events': '//home/taxi/production/replica/postgres/signal_device_api_meta_db/events',  # noqa: E501
        'devices': '//home/taxi/production/replica/postgres/signal_device_api_meta_db/devices',  # noqa: E501
    },
)
@pytest.mark.pgsql(
    'signal_device_api_meta_db',
    files=['last_external_videos_and_photos_deleted.sql'],
)
@pytest.mark.parametrize(
    'yt_data', test_photos_and_videos_data.PARAMETRIZE_YT_DATA,
)
async def test_ok(pgsql, mocked_yql, yt_data):
    # YQL request should be checked manually
    # because there is no ability to test yql in testsuite
    mocked_yql.append(
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable(yt_data)]),
        ),
    )

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(DB_CHECK_QUERY)
    db_result = sorted(list(db), key=lambda x: x[0])
    assert len(db_result) == 5
    assert (
        db_result
        == test_photos_and_videos_data.get_db_external_photo_result_at_start()
    )

    await run_cron.main(CRON_PARAMS)

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(DB_CHECK_QUERY)
    db_result = sorted(list(db), key=lambda x: x[0])
    assert len(db_result) == 6
    assert db_result == [
        (
            '__default__',
            dateutil.parser.parse('2020-12-12T19:38:20+03:00'),
            dateutil.parser.parse('2220-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2120-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2000-10-01T00:00:00+03:00'),
            'event_id5',
        ),
        (
            'distraction',
            dateutil.parser.parse('2020-12-12T16:30:00+03:00'),
            dateutil.parser.parse('2222-11-01T00:00:00+03:00'),
            dateutil.parser.parse('2120-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2004-10-01T00:00:00+03:00'),
            'event_id1',
        ),
        (
            'fart',
            dateutil.parser.parse('2020-09-01T00:00:00+03:00'),
            dateutil.parser.parse('2221-09-01T00:00:00+03:00'),
            dateutil.parser.parse('2120-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2003-10-01T00:00:00+03:00'),
            '',
        ),
        (
            'seatbelt',
            dateutil.parser.parse('2020-12-12T20:00:00+03:00'),
            dateutil.parser.parse('2220-05-01T00:00:00+03:00'),
            dateutil.parser.parse('2120-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2001-10-01T00:00:00+03:00'),
            'event_id8',
        ),
        (
            'sleep',
            dateutil.parser.parse('2020-12-12T21:00:00+03:00'),
            dateutil.parser.parse('2010-01-01T00:00:00+03:00'),
            dateutil.parser.parse('2120-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2002-10-01T00:00:00+03:00'),
            'event_id9',
        ),
        (
            'smoking',
            dateutil.parser.parse('2020-12-12T19:38:20+03:00'),
            dateutil.parser.parse('2016-01-01T00:00:00+03:00'),
            dateutil.parser.parse('2016-01-01T00:00:00+03:00'),
            dateutil.parser.parse('2016-01-01T00:00:00+03:00'),
            'event_id7',
        ),
    ]
