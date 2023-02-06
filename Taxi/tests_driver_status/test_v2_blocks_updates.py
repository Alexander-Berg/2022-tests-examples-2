# pylint: disable=wrong-import-order, import-error
import datetime
import gzip

import lz4.block as lz4
import pytest
import pytz

from driver_status.fbs.v2.blocks import List as FbsDriverBlocksList

import tests_driver_status.pg_helpers as helpers


PG_DRIVER_STATUS_RECORDS = {
    ('driver001', 'park001'): {
        'blocks': {
            'fns_unbound': datetime.datetime(
                2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
            ),
        },
    },
    ('driver002', 'park001'): {
        'blocks': {
            'driver_dkk': datetime.datetime(
                2019, 10, 3, 0, 1, 1, tzinfo=pytz.utc,
            ),
        },
    },
    ('driver003', 'park001'): {
        'blocks': {
            'none': datetime.datetime(2019, 10, 3, 0, 1, 2, tzinfo=pytz.utc),
        },
    },
    ('driver004', 'park001'): {
        'blocks': {
            'driver_dkk': datetime.datetime(
                2019, 10, 3, 0, 1, 3, tzinfo=pytz.utc,
            ),
        },
    },
    ('driver005', 'park001'): {
        'blocks': {
            'driver_dkk': datetime.datetime(
                2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc,
            ),
        },
    },
    ('driver006', 'park001'): {
        'blocks': {
            'driver_dkk': datetime.datetime(
                2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
            ),
        },
    },
    ('driver007', 'park001'): {
        'blocks': {
            'driver_dkk': datetime.datetime(
                2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc,
            ),
        },
    },
    ('driver008', 'park001'): {
        'blocks': {
            'driver_dkk': datetime.datetime(
                2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
            ),
        },
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
    response = FbsDriverBlocksList.List.GetRootAsList(decompressed, 0)
    result['revision'] = response.Revision()
    blocks = {}
    for i in range(0, response.ItemLength()):
        block = response.Item(i)
        key = (
            block.DriverId().decode('utf-8'),
            block.ParkId().decode('utf-8'),
        )
        assert key not in blocks
        reason_name = (
            block.Reason().decode('utf-8') if block.Reason() else 'none'
        )
        if key in blocks:
            assert reason_name not in blocks[key]
            blocks[key][reason_name] = block.UpdatedTs()
        else:
            blocks[key] = {reason_name: block.UpdatedTs()}
        result['block'] = blocks
    return result


async def handle_block_updates(
        pgsql, mocked_time, taxi_driver_status, req, expected,
):
    # set mocked_time
    mocked_time.set(datetime.datetime(2019, 10, 3, 0, 0, 0, tzinfo=pytz.utc))
    # wait mocked_time to be distributed all over the service
    await taxi_driver_status.tests_control(invalidate_caches=False)

    helpers.upsert_blocks(pgsql, PG_DRIVER_STATUS_RECORDS)
    await taxi_driver_status.invalidate_caches(clean_update=True)
    mocked_time.set(datetime.datetime(2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc))

    if 'revision' in req:
        req['revision'] = helpers.datetime_to_us(req['revision'])

    response = await taxi_driver_status.get('v2/blocks/updates', params=req)
    assert response.status_code == expected['code']

    if expected['code'] != 200:
        return

    parsed_response = parse_response(
        response.content, req.get('compression', 'gzip'),
    )
    response_blocks = parsed_response.get('block')
    assert parsed_response['revision'] == helpers.datetime_to_us(
        expected['revision'],
    )
    if response_blocks:
        assert len(response_blocks) == len(expected['drivers'])
        for driver_id, expected_reasons in expected['drivers'].items():
            assert driver_id in response_blocks
            response_reasons = response_blocks[driver_id]
            assert len(expected_reasons) == len(response_reasons)
            for reason in expected_reasons:
                assert reason in response_reasons
                expected_ts = PG_DRIVER_STATUS_RECORDS[driver_id]['blocks'][
                    reason
                ]
                assert (
                    helpers.datetime_to_us(expected_ts)
                    == response_reasons[reason]
                )
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
                'drivers': {
                    ('driver001', 'park001'): {'fns_unbound'},
                    ('driver002', 'park001'): {'driver_dkk'},
                    ('driver003', 'park001'): {'none'},
                    ('driver004', 'park001'): {'driver_dkk'},
                    ('driver005', 'park001'): {'driver_dkk'},
                    ('driver006', 'park001'): {'driver_dkk'},
                    ('driver007', 'park001'): {'driver_dkk'},
                    ('driver008', 'park001'): {'driver_dkk'},
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
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
                'drivers': {
                    ('driver004', 'park001'): {'driver_dkk'},
                    ('driver005', 'park001'): {'driver_dkk'},
                    ('driver006', 'park001'): {'driver_dkk'},
                    ('driver007', 'park001'): {'driver_dkk'},
                    ('driver008', 'park001'): {'driver_dkk'},
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
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
                'drivers': {},
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 2, 5, tzinfo=pytz.utc,
                ),
            },
        ),
    ],
)
async def test_incremental_update(
        pgsql, mocked_time, taxi_driver_status, req, expected,
):
    await handle_block_updates(
        pgsql, mocked_time, taxi_driver_status, req, expected,
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
                'parts_count': 1,
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
                'parts_count': 1,
            },
            {'code': 400},
        ),
    ],
)
async def test_wrong_requests(
        pgsql, mocked_time, taxi_driver_status, req, expected,
):
    await handle_block_updates(
        pgsql, mocked_time, taxi_driver_status, req, expected,
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'req, expected',
    [
        pytest.param(
            {'parts_count': 1, 'compression': 'lz4'},
            {
                'code': 200,
                'drivers': {
                    ('driver001', 'park001'): {'fns_unbound'},
                    ('driver002', 'park001'): {'driver_dkk'},
                    ('driver004', 'park001'): {'driver_dkk'},
                    ('driver005', 'park001'): {'driver_dkk'},
                    ('driver006', 'park001'): {'driver_dkk'},
                    ('driver007', 'park001'): {'driver_dkk'},
                    ('driver008', 'park001'): {'driver_dkk'},
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 2, 'part_no': 0, 'compression': 'none'},
            {
                'code': 200,
                'drivers': {
                    ('driver002', 'park001'): {'driver_dkk'},
                    ('driver004', 'park001'): {'driver_dkk'},
                    ('driver006', 'park001'): {'driver_dkk'},
                    ('driver008', 'park001'): {'driver_dkk'},
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 2, 'part_no': 1},
            {
                'code': 200,
                'drivers': {
                    ('driver001', 'park001'): {'fns_unbound'},
                    ('driver005', 'park001'): {'driver_dkk'},
                    ('driver007', 'park001'): {'driver_dkk'},
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 0},
            {
                'code': 200,
                'drivers': {('driver006', 'park001'): {'driver_dkk'}},
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 1},
            {
                'code': 200,
                'drivers': {
                    ('driver001', 'park001'): {'fns_unbound'},
                    ('driver004', 'park001'): {'driver_dkk'},
                    ('driver007', 'park001'): {'driver_dkk'},
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 2},
            {
                'code': 200,
                'drivers': {
                    ('driver002', 'park001'): {'driver_dkk'},
                    ('driver005', 'park001'): {'driver_dkk'},
                    ('driver008', 'park001'): {'driver_dkk'},
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        ),
    ],
)
async def test_clean_update(
        pgsql, mocked_time, taxi_driver_status, req, expected,
):
    await handle_block_updates(
        pgsql, mocked_time, taxi_driver_status, req, expected,
    )


# pylint: enable=redefined-outer-name
