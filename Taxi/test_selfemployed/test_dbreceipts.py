# pylint: disable=redefined-outer-name,unused-variable

import datetime as dt

from selfemployed.db import dbreceipts


async def test_insert_new(se_web_context):
    park_id = 'park_1'

    receipt_at = dt.datetime.now()
    checkout_at = dt.datetime.now()

    shard = dbreceipts.get_shard_num(se_web_context.pg, park_id)
    await dbreceipts.insert_new(
        se_web_context.pg,
        shard,
        '1',
        dbreceipts.ORDER_TYPE,
        park_id,
        'driver_',
        '111',
        dbreceipts.NEW_STATUS,
        100.0,
        False,
        False,
        receipt_at,
        checkout_at,
    )

    row = await dbreceipts.get_receipt(se_web_context.pg, shard, '1')
    assert row['status'] == dbreceipts.NEW_STATUS
    assert row['receipt_type'] == dbreceipts.ORDER_TYPE
