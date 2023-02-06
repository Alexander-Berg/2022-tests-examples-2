# pylint: disable=protected-access
import datetime

import pytest

from replication.common import source_stamp
from replication.foundation.sources import stamp_info as stamp_info_mod
from replication.replication.core import replication


_RAW_DOCS = [
    {
        '_id': '1',
        'updated': datetime.datetime(2018, 11, 25, 12, 30),
        'value_1': 1,
        'value_2': 2,
    },
    {
        '_id': '2',
        'updated': datetime.datetime(2018, 11, 25, 18, 30),
        'value_1': 11,
        'value_2': 22,
    },
]
_SHARDED_RULE = 'test_sharded_mongo_sharded_queue'


async def test_compat_update_stamp_info(replication_ctx):
    stamp_info = stamp_info_mod.QueueStampInfo(
        datetime.datetime(2021, 1, 1, 12, 30),
    )
    source = replication_ctx.rule_keeper.rules_storage.get_source(
        'queue_mongo-staging_test_rule',
    )
    queue_docs = [{'data': doc} for doc in _RAW_DOCS]
    replication._compat_update_stamp_info(
        stamp_info, queue_docs, replication_ctx, source,
    )
    assert stamp_info.base_stamp_objects == {
        None: source_stamp.StampObject(
            raw_base_current_stamp=datetime.datetime(2018, 11, 25, 18, 30),
        ),
    }


@pytest.mark.parametrize(
    'source_id, stamp, expected_stamp, expected_stamp_after_update',
    [
        (
            'mongo-test_rule',
            None,
            source_stamp.StampObject(
                raw_base_current_stamp=datetime.datetime(2018, 11, 25, 18, 30),
            ),
            source_stamp.StampObject(
                raw_base_current_stamp=datetime.datetime(2018, 11, 25, 18, 30),
            ),
        ),
        (
            'mongo-test_rule',
            source_stamp.StampObject(
                raw_base_current_stamp=datetime.datetime(2018, 11, 25, 18, 20),
            ),
            source_stamp.StampObject(
                raw_base_current_stamp=datetime.datetime(2018, 11, 25, 18, 30),
            ),
            source_stamp.StampObject(
                raw_base_current_stamp=datetime.datetime(2018, 11, 25, 18, 30),
            ),
        ),
        (
            'mongo-test_rule',
            source_stamp.StampObject(
                raw_base_current_stamp=datetime.datetime(2018, 11, 25, 20, 30),
            ),
            source_stamp.StampObject(
                raw_base_current_stamp=datetime.datetime(2018, 11, 25, 18, 30),
            ),
            source_stamp.StampObject(
                raw_base_current_stamp=datetime.datetime(2018, 11, 25, 20, 30),
            ),
        ),
        (
            f'mongo-{_SHARDED_RULE}_shard1',
            source_stamp.StampObject(
                source_unit_name='shard1',
                raw_base_current_stamp=datetime.datetime(2018, 11, 25, 20, 30),
            ),
            source_stamp.StampObject(
                source_unit_name='shard1',
                raw_base_current_stamp=datetime.datetime(2018, 11, 25, 18, 30),
            ),
            source_stamp.StampObject(
                source_unit_name='shard1',
                raw_base_current_stamp=datetime.datetime(2018, 11, 25, 20, 30),
            ),
        ),
    ],
)
async def test_aggregate_stamp_info_by_docs(
        replication_ctx,
        source_id,
        stamp,
        expected_stamp,
        expected_stamp_after_update,
):
    stamp_info = stamp_info_mod.StampInfo(base_stamp=stamp)

    source = replication_ctx.rule_keeper.rules_storage.get_source(source_id)
    current_stamp_info = source.aggregate_stamp_info_by_docs(_RAW_DOCS)
    assert current_stamp_info.base_stamp == expected_stamp

    stamp_info.update_max_stamp_info(current_stamp_info)

    assert stamp_info.base_stamp == expected_stamp_after_update


_BASE_UPDATED = datetime.datetime(2021, 1, 1, 12, 30)


@pytest.mark.parametrize(
    'source_id, stamp, expected_stamp_objects, expected_stamp_after_update',
    [
        (
            'queue_mongo-staging_test_rule',
            None,
            {
                'shard0': source_stamp.StampObject(
                    source_unit_name='shard0',
                    raw_base_current_stamp=_BASE_UPDATED,
                ),
                'shard1': source_stamp.StampObject(
                    source_unit_name='shard1',
                    raw_base_current_stamp=_BASE_UPDATED,
                ),
            },
            {
                'shard0': source_stamp.StampObject(
                    source_unit_name='shard0',
                    raw_base_current_stamp=_BASE_UPDATED,
                ),
                'shard1': source_stamp.StampObject(
                    source_unit_name='shard1',
                    raw_base_current_stamp=_BASE_UPDATED,
                ),
            },
        ),
        (
            f'queue_mongo-staging_{_SHARDED_RULE}_2_4',
            source_stamp.StampObject(
                source_unit_name='shard0',
                raw_base_current_stamp=_BASE_UPDATED
                + datetime.timedelta(minutes=1),
            ),
            {
                'shard0': source_stamp.StampObject(
                    source_unit_name='shard0',
                    raw_base_current_stamp=_BASE_UPDATED,
                ),
                'shard1': source_stamp.StampObject(
                    source_unit_name='shard1',
                    raw_base_current_stamp=_BASE_UPDATED,
                ),
            },
            {
                'shard0': source_stamp.StampObject(
                    source_unit_name='shard0',
                    raw_base_current_stamp=_BASE_UPDATED
                    + datetime.timedelta(minutes=1),
                ),
                'shard1': source_stamp.StampObject(
                    source_unit_name='shard1',
                    raw_base_current_stamp=_BASE_UPDATED,
                ),
            },
        ),
    ],
)
async def test_aggregate_stamp_info_by_queue_docs(
        replication_ctx,
        source_id,
        stamp,
        expected_stamp_objects,
        expected_stamp_after_update,
):
    stamp_info = stamp_info_mod.QueueStampInfo(
        datetime.datetime(2021, 1, 1, 12, 30), base_stamp_object=stamp,
    )

    source = replication_ctx.rule_keeper.rules_storage.get_source(source_id)

    queue_updated = datetime.datetime(2021, 1, 1, 12, 35)
    base_updated = _BASE_UPDATED
    queue_docs = [
        {
            'data': {},
            'updated': queue_updated,
            'unit': f'shard{num}',
            'bs': base_updated,
        }
        for num in range(2)
    ]
    current_stamp_info = source.aggregate_stamp_info_by_docs(queue_docs)

    assert current_stamp_info.queue_timestamp == queue_updated
    assert current_stamp_info.base_stamp_objects == expected_stamp_objects

    stamp_info.update_max_stamp_info(current_stamp_info)

    assert current_stamp_info.queue_timestamp == queue_updated
    assert stamp_info.base_stamp_objects == expected_stamp_after_update
