import datetime

import pytest

from taxi_driver_metrics.common.models import blocking_journal
from taxi_driver_metrics.common.models import BlockingType


UDID_1 = '5b05621ee6c22ea2654849c9'
TIMESTAMP = datetime.datetime(2016, 5, 6, 10, 0, 0, 0)
TWO_DAYS_BEFORE = TIMESTAMP - datetime.timedelta(days=2)


@pytest.mark.filldb()
async def test_fetching(stq3_context):
    # missing driver, no data
    res = await blocking_journal.fetch_blocking_history(
        stq3_context, '5b05621ee6c22ea2654849c0', TWO_DAYS_BEFORE,
    )
    assert not res
    res = await blocking_journal.fetch_current_blocking(
        stq3_context, '5b05621ee6c22ea2654849c0',
    )
    assert not res

    # check fetching
    res = await blocking_journal.fetch_blocking_history(
        stq3_context, UDID_1, TWO_DAYS_BEFORE,
    )
    assert len(res) == 3
    assert res[0].until == datetime.datetime(2016, 5, 6, 10)
    assert res[0].type == BlockingType.BY_ACTIONS
    assert res[1].until == datetime.datetime(2016, 5, 6, 9)

    res = await blocking_journal.fetch_current_blocking(stq3_context, UDID_1)
    assert len(res) == 2
    assert res[0].until == datetime.datetime(2016, 5, 8, 10)
    assert res[0].type == BlockingType.BY_ACTIVITY

    # check update
    item = res[1]
    await blocking_journal.reset_blocking(stq3_context, item)
    res = await blocking_journal.fetch_current_blocking(stq3_context, UDID_1)
    assert len(res) == 1
    assert res[0].until == datetime.datetime(2016, 5, 8, 10)
    await blocking_journal.reset_blocking(stq3_context, item)
    res = await blocking_journal.fetch_blocking_history(
        stq3_context, UDID_1, TWO_DAYS_BEFORE,
    )
    assert len(res) == 4
    assert res[0].until == datetime.datetime(2016, 5, 7, 10)

    # new blocking
    await blocking_journal.save_to_db(
        stq3_context,
        UDID_1,
        TIMESTAMP,
        TIMESTAMP,
        BlockingType.BY_ACTIVITY,
        'super_rule',
        'rule_id1',
        'tanker_super_key',
        'profile_id',
        'ref_id',
        'zone_test',
        'order_Id',
        [],
    )
    res = await blocking_journal.fetch_current_blocking(stq3_context, UDID_1)
    assert len(res) == 2
    assert res[0].until == datetime.datetime(2016, 5, 8, 10)


@pytest.mark.filldb()
async def test_metrics(stq3_context):
    # missing driver, no data
    res = await blocking_journal.get_blocking_stats_by_rules(stq3_context)
    assert len(res) == 1
    assert res[0][1] == 1

    res = await blocking_journal.get_blocking_stats_by_types(stq3_context)
    assert len(res) == 3
    assert res[0][1] == 2
    assert res[0][0] == 'activity'

    res = await blocking_journal.get_actions_stats_by_zones(stq3_context)
    assert len(res) == 1
    assert res[0][1] == 1
    assert res[0][0] == 'spb'

    res = await blocking_journal.get_stale_blocking(stq3_context)

    assert res
    assert res[0].rule_name == 'actions_block_1'


@pytest.mark.filldb()
async def test_unique_key(stq3_context):
    res = await blocking_journal.fetch_current_blocking(stq3_context, UDID_1)
    assert len(res) == 2

    async def save_blocking():
        await blocking_journal.save_to_db(
            stq3_context,
            UDID_1,
            TIMESTAMP,
            TIMESTAMP,
            BlockingType.BY_ACTIVITY,
            'super_rule',
            'rule_id1',
            'tanker_super_key',
            'profile_id',
            'ref_id',
            'zone_test',
            'order_Id',
            [],
        )

    await save_blocking()
    res = await blocking_journal.fetch_current_blocking(stq3_context, UDID_1)
    assert len(res) == 3

    # check that a blocking with the same rule_id + message id is not saved
    with pytest.raises(blocking_journal.BlockingJournalDbException):
        await save_blocking()
    res = await blocking_journal.fetch_current_blocking(stq3_context, UDID_1)
    assert len(res) == 3
    assert res[0].until == datetime.datetime(2016, 5, 8, 10)
