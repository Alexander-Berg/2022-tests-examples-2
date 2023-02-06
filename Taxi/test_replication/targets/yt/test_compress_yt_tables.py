# pylint: disable=protected-access
import datetime

import pytest

from taxi import settings

from replication.targets.yt import yt_rotate_raw_history


@pytest.mark.parametrize(
    'yt_target_name, expected, base_current_stamp',
    [
        (
            'test_raw_history_month',
            0,
            datetime.datetime.strptime('2021-08-02', '%Y-%m-%d'),
        ),
        (
            'test_raw_history_month',
            1,
            datetime.datetime.strptime('2021-10-02', '%Y-%m-%d'),
        ),
        (
            'test_raw_history_month',
            1,
            datetime.datetime.strptime('2021-11-01', '%Y-%m-%d'),
        ),
        (
            'test_raw_history_month',
            2,
            datetime.datetime.strptime('2021-11-02', '%Y-%m-%d'),
        ),
        (
            'test_raw_history_month',
            2,
            datetime.datetime.strptime('2021-12-02', '%Y-%m-%d'),
        ),
        (
            'test_raw_history_years',
            0,
            datetime.datetime.strptime('2021-01-01', '%Y-%m-%d'),
        ),
        (
            'test_raw_history_years',
            1,
            datetime.datetime.strptime('2021-01-02', '%Y-%m-%d'),
        ),
        (
            'test_raw_history_years',
            1,
            datetime.datetime.strptime('2022-01-02', '%Y-%m-%d'),
        ),
        (
            'test_raw_history_days',
            1,
            datetime.datetime.strptime('2021-12-03', '%Y-%m-%d'),
        ),
        (
            'test_raw_history_days',
            2,
            datetime.datetime.strptime('2021-12-04', '%Y-%m-%d'),
        ),
        (
            'test_raw_history_days',
            3,
            datetime.datetime.strptime('2021-12-05', '%Y-%m-%d'),
        ),
        (
            'test_raw_history_days',
            3,
            datetime.datetime.strptime('2021-12-06', '%Y-%m-%d'),
        ),
    ],
)
@pytest.mark.now('2022-01-10T18:29:12')
@pytest.mark.yt(
    dyn_table_data=['yt_2021_08_table.yaml', 'yt_2021_10_table.yaml'],
    static_table_data=['yt_2021_09_table.yaml'],
    schemas=['yt_compress_tables_schemas.yaml'],
)
@pytest.mark.use_yt_local
async def test_for_filter_tables_for_compress(
        replication_ctx,
        yt_target_name,
        expected,
        base_current_stamp,
        yt_apply,
        yt_client,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        target_names=[yt_target_name],
    )
    yt_target = rules[0].targets[0]
    all_tables_for_yt_target = await yt_rotate_raw_history._collect_tables(
        yt_target._async_yt_client, yt_target.meta.full_path,
    )
    tables_for_compress = yt_rotate_raw_history._filter_tables_to_compress(
        all_tables_for_yt_target, yt_target, base_current_stamp,
    )
    assert len(tables_for_compress) == expected


@pytest.mark.yt(
    schemas=['yt_schema_compress_one.yaml'],
    dyn_table_data=['yt_2021_08_table.yaml'],
)
@pytest.mark.use_yt_local
async def test_compress_one_table(replication_ctx, yt_apply_force, yt_client):
    yt_target = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        target_names=['test_raw_history_month'],
        target_unit_ids=['seneca-vla'],
    )[0].targets[0]
    table = '//home/taxi/unittests/test/test_raw_history/2021-08'
    assert yt_client.get(table + '/@dynamic')
    table_obj = await yt_rotate_raw_history._collect_tables(
        yt_target._async_yt_client, table,
    )
    assert len(table_obj) == 1
    result = await yt_rotate_raw_history.compress_one_table(
        yt_target, table_obj[0],
    )
    assert result
    assert not yt_client.get(table + '/@dynamic')


async def test_raw_history_pool(replication_ctx, monkeypatch):
    monkeypatch.setattr(settings, 'ENVIRONMENT', settings.PRODUCTION)

    yt_target = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        target_names=['test_raw_history_month'],
        target_unit_ids=['seneca-vla'],
    )[0].targets[0]
    assert yt_target.meta.get_raw_history_pool() is None

    yt_target = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        target_names=['test_raw_history_month'],
        target_unit_ids=['seneca-man'],
    )[0].targets[0]
    assert yt_target.meta.get_raw_history_pool() == 'pool2'

    monkeypatch.setattr(settings, 'ENVIRONMENT', settings.TESTING)

    yt_target = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        target_names=['test_raw_history_month'],
        target_unit_ids=['seneca-man'],
    )[0].targets[0]
    assert yt_target.meta.get_raw_history_pool() is None
