# pylint: disable=protected-access
import datetime

from replication.common import source_stamp
from replication.foundation.sources import stamp_info

_STATE_ID = 'queue_mongo-staging_test_rule-yt-test_rule_struct-hahn'
_BASE_STAMP = datetime.datetime(2021, 1, 10, 0, 0)


async def test_base_stamp(replication_ctx):
    state = replication_ctx.rule_keeper.states_wrapper.get_state(
        replication_id=_STATE_ID,
    )
    assert state.base_current_stamp == _BASE_STAMP
    assert state.raw_base_current_stamp == _BASE_STAMP
    assert state._base_stamp_objects == {
        'shard0': source_stamp.StampObject(
            source_unit_name='shard0',
            raw_base_current_stamp=datetime.datetime(2021, 1, 10, 0, 0),
        ),
        'shard1': source_stamp.StampObject(
            source_unit_name='shard1',
            raw_base_current_stamp=datetime.datetime(2021, 1, 11, 0, 0),
        ),
    }

    await state.update_last_replication(
        datetime.datetime(2021, 1, 1, 10, 0),
        stamp_info=stamp_info.QueueStampInfo(
            base_stamp_object=source_stamp.StampObject(
                source_unit_name='shard0',
                raw_base_current_stamp=datetime.datetime(2021, 1, 20, 10, 0),
            ),
        ),
    )
    await state.update_last_replication(
        datetime.datetime(2021, 1, 1, 10, 0),
        stamp_info=stamp_info.QueueStampInfo(
            base_stamp_object=source_stamp.StampObject(
                source_unit_name='shard3',
                raw_base_current_stamp=datetime.datetime(2021, 1, 20, 11, 0),
            ),
        ),
    )

    assert state.base_current_stamp == datetime.datetime(2021, 1, 11, 0, 0)
    assert state.raw_base_current_stamp == datetime.datetime(2021, 1, 11, 0, 0)
    assert state._base_stamp_objects == {
        'shard0': source_stamp.StampObject(
            source_unit_name='shard0',
            raw_base_current_stamp=datetime.datetime(2021, 1, 20, 10, 0),
        ),
        'shard1': source_stamp.StampObject(
            source_unit_name='shard1',
            raw_base_current_stamp=datetime.datetime(2021, 1, 11, 0, 0),
        ),
        'shard3': source_stamp.StampObject(
            source_unit_name='shard3',
            raw_base_current_stamp=datetime.datetime(2021, 1, 20, 11, 0),
        ),
    }


def test_dump_state(replication_ctx):
    state = replication_ctx.rule_keeper.states_wrapper.get_state(
        replication_id=_STATE_ID,
    )
    dump = {
        '_id': 'queue_mongo-staging_test_rule-yt-test_rule_struct-hahn',
        'base_stamp_object': {
            'shard0': {
                'raw_base_last_stamp': {'$datetime': '2021-01-10T00:00:00'},
            },
            'shard1': {
                'raw_base_last_stamp': {'$datetime': '2021-01-11T00:00:00'},
            },
        },
    }
    assert state.to_dict() == dump
    assert state.__class__.from_dump(dump).to_dict() == dump
