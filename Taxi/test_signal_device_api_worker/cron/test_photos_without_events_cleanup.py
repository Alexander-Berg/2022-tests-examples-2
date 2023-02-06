# pylint: disable=unused-variable
import dateutil.parser
import pytest

from signal_device_api_worker.generated.cron import run_cron  # noqa F401
from test_signal_device_api_worker import conftest as tst


CRON_PARAMS = [
    'signal_device_api_worker.crontasks.photos_without_events_cleanup',
    '-t',
    '0',
]

DB_CHECK_QUERY = """
    SELECT last_deleted_photo_at
    FROM signal_device_api.last_videos_and_photos_deleted_without_events;
    """

YT_DATA = [
    ['some_file_id1a', 1607771000, 'd1'],  # 2020-12-12T14:03:20+03:00
    ['some_file_id2a', 1607779800, 'd2'],  # 2020-12-12T16:30:00+03:00
    ['some_file_id3a', 1607779900, 'd3'],  # 2020-12-12T16:31:00+03:00
]


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
        'photos': '//home/taxi/production/replica/postgres/signal_device_api_meta_db/photos',  # noqa: E501
    },
)
@pytest.mark.pgsql(
    'signal_device_api_meta_db',
    files=['last_photos_deleted_without_events.sql'],
)
async def test_ok(pgsql, mocked_yql):
    # YQL request should be checked manually
    # because there is no ability to test yql in testsuite
    mocked_yql.append(
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable(YT_DATA)]),
        ),
    )

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(DB_CHECK_QUERY)
    db_result = list(db)
    assert db_result == [(dateutil.parser.parse('2020-10-01T00:00:00+03:00'),)]

    await run_cron.main(CRON_PARAMS)

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(DB_CHECK_QUERY)
    db_result = list(db)
    assert db_result == [(dateutil.parser.parse('2020-12-12T16:31:40+03:00'),)]
