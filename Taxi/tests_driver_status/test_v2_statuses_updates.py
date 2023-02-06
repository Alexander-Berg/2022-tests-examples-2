# pylint: disable=import-error
# pylint: disable=import-only-modules
import datetime
import gzip

import lz4.block as lz4
import pytest
import pytz

from driver_status.fbs.v2.statuses import List as FbsDriverStatusesList
from driver_status.fbs.v2.statuses import Status as FbsDriverStatusesStatus

from tests_driver_status.enum_constants import DriverStatus
import tests_driver_status.pg_helpers as helpers
import tests_driver_status.utils as utils


class DriverStatusSource:
    Service = 'service'
    Client = 'client'
    PeriodicalUpdater = 'periodical-updater'


FBS_STATUS_TO_DRIVER_STATUS = {
    FbsDriverStatusesStatus.Status.Offline: DriverStatus.Offline,
    FbsDriverStatusesStatus.Status.Online: DriverStatus.Online,
    FbsDriverStatusesStatus.Status.Busy: DriverStatus.Busy,
}


PG_DRIVER_STATUS_RECORDS = {
    ('driver001', 'park001'): {
        'updated_ts': '2019-10-03 00:01:00.0+00',
        'status': DriverStatus.Offline,
    },
    ('driver002', 'park001'): {
        'updated_ts': '2019-10-03 00:01:01.0+00',
        'status': DriverStatus.Online,
    },
    ('driver003', 'park001'): {
        'updated_ts': '2019-10-03 00:01:02.0+00',
        'status': DriverStatus.Busy,
    },
    ('driver004', 'park001'): {
        'updated_ts': '2019-10-03 00:01:03.0+00',
        'status': DriverStatus.Online,
    },
    ('driver005', 'park001'): {
        'updated_ts': '2019-10-03 00:01:04.0+00',
        'status': DriverStatus.Busy,
    },
    ('driver006', 'park001'): {
        'updated_ts': '2019-10-03 00:01:05.0+00',
        'status': DriverStatus.Online,
    },
}


def parse_response(data, compression_method):
    result = dict()
    decompression_methods = {
        'none': lambda x: x,
        'gzip': gzip.decompress,
        'lz4': lz4.decompress,
    }
    decompressed = decompression_methods.get(
        compression_method, gzip.decompress,
    )(data)
    response = FbsDriverStatusesList.List.GetRootAsList(decompressed, 0)
    result['revision'] = response.Revision()
    statuses = {}
    for i in range(0, response.ItemsLength()):
        status = response.Items(i)
        key = (
            status.DriverId().decode('utf-8'),
            status.ParkId().decode('utf-8'),
        )
        assert key not in statuses
        statuses[key] = {
            'status': status.Status(),
            'updated_ts': status.UpdatedTs(),
        }
        result['statuses'] = statuses
    return result


def check_status(expected, rcvd):
    assert FBS_STATUS_TO_DRIVER_STATUS[rcvd['status']] == expected['status']


def check_upated_ts(expected, rcvd):
    assert rcvd['updated_ts'] == utils.date_str_to_us(expected['updated_ts'])


async def handle_statuses_updates(
        taxi_driver_status, mocked_time, pgsql, req, expected,
):
    # set mocked_time
    mocked_time.set(datetime.datetime(2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc))

    # wait mocked_time to be distributed all over the service
    await taxi_driver_status.tests_control(invalidate_caches=False)

    helpers.upsert_statuses(pgsql, PG_DRIVER_STATUS_RECORDS)
    await taxi_driver_status.invalidate_caches(clean_update=True)

    if 'revision' in req:
        req['revision'] = helpers.datetime_to_us(req['revision'])

    response = await taxi_driver_status.get('v2/statuses/updates', params=req)
    assert response.status_code == expected['code']

    if expected['code'] != 200:
        return

    parsed_response = parse_response(
        response.content, req.get('compression', 'gzip'),
    )
    statuses = parsed_response.get('statuses')
    assert parsed_response['revision'] == helpers.datetime_to_us(
        expected['revision'],
    )
    if statuses:
        assert len(statuses) == len(expected['drivers'])
        for key in expected['drivers']:
            assert key in statuses
            status = statuses[key]
            expected_val = PG_DRIVER_STATUS_RECORDS[key]
            check_status(expected_val, status)
            check_upated_ts(expected_val, status)
    else:
        assert not expected['drivers']


# pylint: disable=redefined-outer-name
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'req, expected',
    [
        pytest.param(
            {
                'revision': datetime.datetime(
                    1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc,
                ),
            },
            {
                'code': 200,
                'drivers': [
                    ('driver001', 'park001'),
                    ('driver002', 'park001'),
                    ('driver003', 'park001'),
                    ('driver004', 'park001'),
                    ('driver005', 'park001'),
                    ('driver006', 'park001'),
                ],
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 3, tzinfo=pytz.utc,
                ),
            },
            {
                'code': 200,
                'drivers': [
                    ('driver004', 'park001'),
                    ('driver005', 'park001'),
                    ('driver006', 'park001'),
                ],
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 2, 5, tzinfo=pytz.utc,
                ),
            },
            {
                'code': 200,
                'drivers': [],
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 2, 5, tzinfo=pytz.utc,
                ),
            },
        ),
    ],
)
async def test_incremental_update(
        taxi_driver_status, mocked_time, pgsql, req, expected,
):
    await handle_statuses_updates(
        taxi_driver_status, mocked_time, pgsql, req, expected,
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'req, expected',
    [
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
                'parts_count': 2,
            },
            {'code': 400},
        ),
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
                'part_no': 0,
            },
            {'code': 400},
        ),
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
                'part_no': 1,
            },
            {'code': 400},
        ),
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
                'part_no': 1,
                'parts_count': 1,
            },
            {'code': 400},
        ),
    ],
)
async def test_wrong_requests(
        taxi_driver_status, mocked_time, pgsql, req, expected,
):
    await handle_statuses_updates(
        taxi_driver_status, mocked_time, pgsql, req, expected,
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'req, expected',
    [
        pytest.param(
            {'parts_count': 1, 'compression': 'lz4'},
            {
                'code': 200,
                'drivers': [
                    ('driver002', 'park001'),
                    ('driver003', 'park001'),
                    ('driver004', 'park001'),
                    ('driver005', 'park001'),
                    ('driver006', 'park001'),
                ],
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 2, 'part_no': 0, 'compression': 'none'},
            {
                'code': 200,
                'drivers': [
                    ('driver002', 'park001'),
                    ('driver004', 'park001'),
                    ('driver006', 'park001'),
                ],
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 2, 'part_no': 1},
            {
                'code': 200,
                'drivers': [
                    ('driver003', 'park001'),
                    ('driver005', 'park001'),
                ],
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 0},
            {
                'code': 200,
                'drivers': [
                    ('driver003', 'park001'),
                    ('driver006', 'park001'),
                ],
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 1},
            {
                'code': 200,
                'drivers': [('driver004', 'park001')],
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 3, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 2},
            {
                'code': 200,
                'drivers': [
                    ('driver002', 'park001'),
                    ('driver005', 'park001'),
                ],
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc,
                ),
            },
        ),
    ],
)
async def test_clean_update(
        taxi_driver_status, mocked_time, pgsql, req, expected,
):
    await handle_statuses_updates(
        taxi_driver_status, mocked_time, pgsql, req, expected,
    )


# pylint: enable=redefined-outer-name
