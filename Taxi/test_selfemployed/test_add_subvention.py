# pylint: disable=invalid-name,unused-variable

import datetime as dt

import pytest

from selfemployed.db import dbreceipts

EPSILON_TIMEDELTA_SEC = 10


@pytest.mark.pgsql('selfemployed_main', files=['add_simple_profile.sql'])
@pytest.mark.parametrize(
    'park_id,driver_id,has_mapping',
    [('p1', 'd1', True), ('p1', 'd1', False), ('uber_p1', 'uber_d1', True)],
)
async def test_add_subvention(
        se_client, se_web_context, park_id, driver_id, has_mapping, mockserver,
):
    if not has_mapping:

        @mockserver.json_handler('/fleet-synchronizer/v1/mapping/driver')
        def _mapping_driver(request):
            return {'mapping': []}

    json_body = {
        'park_id': park_id,
        'driver_id': driver_id,
        'subvention_id': 's1',
        'total': 120.1,
        'receipt_date': '2018-12-29T17:29:30.742701Z',
        'checkout_date': '2018-12-29T17:29:30.742701Z',
    }

    response = await se_client.post('/add-subvention', json=json_body)
    assert response.status == 200

    pg = se_web_context.pg
    shard = dbreceipts.get_shard_num(pg, park_id)
    receipt = await dbreceipts.get_receipt(pg, shard, 's1')

    # Here dt.datetime.now() is smaller than db's timestamp
    # because time freezes during the test. This affects
    # dt.datetime.now() but doesn't affect db's now()::timestamp.
    assert (
        receipt['created_at'] - dt.datetime.now()
    ).seconds <= EPSILON_TIMEDELTA_SEC
    assert (
        receipt['modified_at'] - dt.datetime.now()
    ).seconds <= EPSILON_TIMEDELTA_SEC

    assert str(receipt['receipt_at']) == '2018-12-29 17:29:30.742701'
    assert str(receipt['checkout_at']) == '2018-12-29 17:29:30.742701'

    assert receipt['status'] == 'new'
    assert receipt['inn'] == '111'


@pytest.mark.pgsql('selfemployed_main', files=['add_simple_profile.sql'])
async def test_add_subvention_duplicate(se_client):
    json_body = {
        'park_id': 'p1',
        'driver_id': 'd1',
        'subvention_id': 's1',
        'total': 120.1,
        'receipt_date': '2018-12-29T17:29:30.742701Z',
        'checkout_date': '2018-12-29T17:29:30.742701Z',
    }

    # Order added for the first time
    response = await se_client.post('/add-subvention', json=json_body)
    assert response.status == 200

    response = await se_client.post('/add-subvention', json=json_body)
    assert response.status == 200


@pytest.mark.parametrize(
    'park_id,driver_id,has_mapping,has_original_inn',
    [
        ('p1', 'd1', True, False),
        ('p1', 'd1', False, False),
        ('uber_p1', 'uber_d1', True, False),
        ('uber_p1', 'uber_d1', False, True),
        ('uber_p1', 'uber_d1', False, False),
    ],
)
async def test_add_subvention_missing_inn(
        se_client,
        se_web_context,
        park_id,
        driver_id,
        has_mapping,
        has_original_inn,
        mockserver,
        pgsql,
        load,
):
    if not has_mapping:

        @mockserver.json_handler('/fleet-synchronizer/v1/mapping/driver')
        def _mapping_driver(request):
            return {'mapping': []}

    with pgsql['selfemployed_main'].cursor() as cursor:
        cursor.execute(
            load(
                'add_simple_profile.sql'
                if has_original_inn
                else 'add_simple_profile_no_inn.sql',
            ),
        )

    json_body = {
        'park_id': park_id,
        'driver_id': driver_id,
        'subvention_id': 's1',
        'total': 120.1,
        'receipt_date': '2018-12-29T17:29:30.742701Z',
        'checkout_date': '2018-12-29T17:29:30.742701Z',
    }

    response = await se_client.post('/add-subvention', json=json_body)
    assert response.status == 200

    pg = se_web_context.pg
    shard = dbreceipts.get_shard_num(pg, park_id)
    receipt = await dbreceipts.get_receipt(pg, shard, 's1')

    # Here dt.datetime.now() is smaller than db's timestamp
    # because time freezes during the test. This affects
    # dt.datetime.now() but doesn't affect db's now()::timestamp.
    assert (
        receipt['created_at'] - dt.datetime.now()
    ).seconds <= EPSILON_TIMEDELTA_SEC
    assert (
        receipt['modified_at'] - dt.datetime.now()
    ).seconds <= EPSILON_TIMEDELTA_SEC

    assert str(receipt['receipt_at']) == '2018-12-29 17:29:30.742701'
    assert str(receipt['checkout_at']) == '2018-12-29 17:29:30.742701'

    assert receipt['status'] == 'missing_inn'
    assert receipt['inn'] is None
