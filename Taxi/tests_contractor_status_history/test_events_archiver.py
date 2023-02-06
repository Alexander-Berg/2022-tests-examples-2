# pylint: disable=import-error
# pylint: disable=import-only-modules
import datetime

import pytest

from tests_contractor_status_history.consts import OrderStatus
from tests_contractor_status_history.consts import Status
import tests_contractor_status_history.fbs_helpers as fbs
import tests_contractor_status_history.utils as utils

try:
    import lz4.block as lz4
except ImportError:
    import lz4


# corresponds to 2020-11-26
FILL_EVENTS_000 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_000 VALUES '
    '(\'park1\', \'profile1\', ARRAY['
    '(\'2020-11-26 15:00:00.0+03\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 15:01:00.0+03\', \'online\', \'{driving}\')::event_tuple,'
    '(\'2020-11-26 15:02:00.0+03\', \'busy\', '
    '\'{transporting,waiting}\')::event_tuple,'
    '(\'2020-11-26 15:03:00.0+03\', \'offline\', \'{}\')::event_tuple'
    ']), (\'park2\', \'profile2\',  ARRAY['
    '(\'2020-11-26 15:00:00.0+03\', \'online\', \'{}\')::event_tuple'
    ']);'
    'COMMIT;'
)

# corresponds to 2020-11-27
FILL_EVENTS_001 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_001 VALUES '
    '(\'park1\', \'profile1\', ARRAY['
    '(\'2020-11-27 15:00:00.0+03\', \'online\', \'{}\')::event_tuple],'
    '\'2020-11-28 11:00:00.0+00\');'
    'COMMIT;'
)

# corresponds to 2020-11-28
FILL_EVENTS_002 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_002 VALUES '
    '(\'park1\', \'profile1\', ARRAY['
    '(\'2020-11-28 15:00:00.0+03\', \'offline\', \'{}\')::event_tuple,'
    '(\'2020-11-28 15:00:01.0+03\', \'offline\', \'{}\')::event_tuple,'
    '(\'2020-11-28 15:00:02.0+03\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-28 15:00:03.0+03\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-28 15:00:04.0+03\', \'online\', \'{driving}\')::event_tuple,'
    '(\'2020-11-28 15:00:05.0+03\', \'online\', \'{driving}\')::event_tuple,'
    '(\'2020-11-28 15:00:06.0+03\', \'online\', '
    '\'{driving,waiting}\')::event_tuple,'
    '(\'2020-11-28 15:00:07.0+03\', \'online\', '
    '\'{waiting,driving}\')::event_tuple,'
    '(\'2020-11-28 15:00:08.0+03\', \'online\', \'{driving}\')::event_tuple,'
    '(\'2020-11-28 15:00:09.0+03\', \'busy\', \'{driving}\')::event_tuple'
    ']);'
    'COMMIT;'
)


def _get_mds_s3_history(mds_s3_storage, path):
    # NOTE: we add '/mds-s3' path in service.yaml
    # to distinguish mockserver requests
    # there is no '/mds-s3' prefix in production
    raw_data = mds_s3_storage.get_object('/mds-s3' + path)
    decompressed = lz4.decompress(raw_data)
    return fbs.unpack_status_history(decompressed)


@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
@pytest.mark.pgsql('contractor_status_history', queries=[FILL_EVENTS_000])
async def test_events_archiver(
        taxi_contractor_status_history, testpoint, mocked_time, mds_s3_storage,
):
    now = datetime.datetime(2020, 11, 27, 12, 00, 00)

    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, now,
    )
    mocked_time.set(now)

    await taxi_contractor_status_history.run_task(
        'worker-events-archiver.testsuite-task',
    )

    result = _get_mds_s3_history(mds_s3_storage, '/park1/profile1/2020-11-26')
    assert result == {
        'events': [
            {
                'ts': utils.parse_date_str('2020-11-26 15:00:00.0+03'),
                'status': Status.Online,
                'orders': [],
            },
            {
                'ts': utils.parse_date_str('2020-11-26 15:01:00.0+03'),
                'status': Status.Online,
                'orders': [OrderStatus.kDriving],
            },
            {
                'ts': utils.parse_date_str('2020-11-26 15:02:00.0+03'),
                'status': Status.Busy,
                'orders': [OrderStatus.kTransporting, OrderStatus.kWaiting],
            },
            {
                'ts': utils.parse_date_str('2020-11-26 15:03:00.0+03'),
                'status': Status.Offline,
                'orders': [],
            },
        ],
    }

    result = _get_mds_s3_history(mds_s3_storage, '/park2/profile2/2020-11-26')
    assert result == {
        'events': [
            {
                'ts': utils.parse_date_str('2020-11-26 15:00:00.0+03'),
                'status': Status.Online,
                'orders': [],
            },
        ],
    }


@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
@pytest.mark.pgsql('contractor_status_history', queries=[FILL_EVENTS_001])
async def test_events_archiver_retries(
        taxi_contractor_status_history, testpoint, mocked_time, mds_s3_storage,
):
    now = datetime.datetime(2020, 11, 28, 12, 00, 00)

    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, now,
    )
    mocked_time.set(now)

    await taxi_contractor_status_history.run_task(
        'worker-events-archiver.testsuite-task',
    )

    result = _get_mds_s3_history(mds_s3_storage, '/park1/profile1/2020-11-27')
    assert result == {
        'events': [
            {
                'ts': utils.parse_date_str('2020-11-27 15:00:00.0+03'),
                'status': Status.Online,
                'orders': [],
            },
        ],
    }


@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
@pytest.mark.pgsql('contractor_status_history', queries=[FILL_EVENTS_002])
async def test_merge(
        taxi_contractor_status_history, testpoint, mocked_time, mds_s3_storage,
):
    now = datetime.datetime(2020, 11, 29, 12, 00, 00)

    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, now,
    )
    mocked_time.set(now)

    await taxi_contractor_status_history.run_task(
        'worker-events-archiver.testsuite-task',
    )

    result = _get_mds_s3_history(mds_s3_storage, '/park1/profile1/2020-11-28')
    assert result == {
        'events': [
            {
                'ts': utils.parse_date_str('2020-11-28 15:00:00.0+03'),
                'status': Status.Offline,
                'orders': [],
            },
            {
                'ts': utils.parse_date_str('2020-11-28 15:00:02.0+03'),
                'status': Status.Online,
                'orders': [],
            },
            {
                'ts': utils.parse_date_str('2020-11-28 15:00:04.0+03'),
                'status': Status.Online,
                'orders': [OrderStatus.kDriving],
            },
            {
                'ts': utils.parse_date_str('2020-11-28 15:00:06.0+03'),
                'status': Status.Online,
                'orders': [OrderStatus.kDriving, OrderStatus.kWaiting],
            },
            {
                'ts': utils.parse_date_str('2020-11-28 15:00:07.0+03'),
                'status': Status.Online,
                'orders': [OrderStatus.kWaiting, OrderStatus.kDriving],
            },
            {
                'ts': utils.parse_date_str('2020-11-28 15:00:08.0+03'),
                'status': Status.Online,
                'orders': [OrderStatus.kDriving],
            },
            {
                'ts': utils.parse_date_str('2020-11-28 15:00:09.0+03'),
                'status': Status.Busy,
                'orders': [OrderStatus.kDriving],
            },
        ],
    }
