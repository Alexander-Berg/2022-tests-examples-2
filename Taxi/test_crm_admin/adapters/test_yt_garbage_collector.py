# pylint: disable=protected-access

import pytest
import yt.wrapper as yt

from crm_admin.utils.yt import yt_garbage_collector as yt_gc


@pytest.mark.yt(static_table_data=['yt_gc_table1_merge_sample.yaml'])
async def test_yt_gc_remove(yt_apply, yt_client, cron_context):
    table = '//home/clear_node/table1_merge'

    assert yt_client.exists(table)
    await yt_gc._remove_table(cron_context, yt_gc.YTWithID(0, table))
    assert not yt_client.exists(table)


@pytest.mark.yt(
    static_table_data=[
        'yt_gc_table1_merge_sample.yaml',
        'yt_gc_table2_merge_sample.yaml',
        'yt_gc_table3_merge_sample.yaml',
        'yt_gc_table1_sample.yaml',
    ],
)
@pytest.mark.parametrize(
    'src_tables, dst_table, raises_exc',
    [
        [
            [
                '//home/clear_node/table1_merge',
                '//home/clear_node/table2_merge',
            ],
            '//home/clear_node/agg_table1',
            False,
        ],
        [
            [
                '//home/clear_node/table1_merge',
                '//home/clear_node/table3_merge',
            ],
            '//home/clear_node/agg_table2',
            False,
        ],
        [
            [
                '//home/clear_node/table2_merge',
                '//home/clear_node/table3_merge',
            ],
            '//home/clear_node/agg_table3',
            False,
        ],
        [
            [
                '//home/clear_node/table1_merge',
                '//home/clear_node/table2_merge',
                '//home/clear_node/table3_merge',
            ],
            '//home/clear_node/agg_table4',
            False,
        ],
        [
            ['//home/clear_node/table1_merge', '//home/clear_node/table1'],
            '//home/clear_node/agg_table5',
            True,
        ],
    ],
)
async def test_yt_gc_merge(
        yt_client, cron_context, patch, src_tables, dst_table, raises_exc,
):
    exp_agg_table = sum(
        [list(yt_client.read_table(table)) for table in src_tables], [],
    )

    try:
        await yt_gc._merge(
            cron_context,
            [yt_gc.YTWithID(0, table) for table in src_tables],
            dst_table,
        )
    except yt.YtError:
        assert raises_exc is True
    else:
        assert raises_exc is False
        assert yt_client.exists(dst_table)
        agg_table = list(yt_client.read_table(dst_table))
        assert exp_agg_table == agg_table


@pytest.mark.yt(static_table_data=['yt_gc_table1_sample.yaml'])
async def test_add_campaign_id(yt_apply, yt_client, cron_context, patch):
    table_path = '//home/clear_node/table1'

    old_table = list(yt_client.read_table(table_path))
    await yt_gc._run_add_campaign_id(
        cron_context, yt_gc.YTWithID(1, table_path),
    )
    new_table = list(yt_client.read_table(table_path))

    assert set(row['campaign_id'] for row in new_table) == {1}
    assert old_table == [row['data'] for row in new_table]

    yt_client.remove(table_path)
