# pylint: disable=invalid-name

import pytest

from taxi.clients import postgres


@pytest.mark.parametrize(
    'db_id,table,expected',
    [
        ('bar', postgres.Table.ORDERS, (0, 'orders_0')),
        ('foo', postgres.Table.ORDERS, (1, 'orders_1')),
        ('separate', postgres.Table.ORDERS, (2, 'orders_separate')),
        ('foo', postgres.Table.TRANSACTIONS, (0, 'transactions_1')),
    ],
)
@pytest.mark.mongodb_collections(
    'dbparks_table_shard_map', 'dbparks_park_table_map',
)
async def test_park_table_mapper(
        db, unittest_settings, monkeypatch, db_id, table, expected,
):
    monkeypatch.setattr(unittest_settings, 'COMPOSITE_TABLES_COUNT', 2)

    park_table_mapper = postgres.ParkTableMapper(db, unittest_settings)
    await park_table_mapper.refresh_cache()
    shard_num, table_name = park_table_mapper.get_shard_num_and_table_name(
        db_id, table,
    )

    assert (shard_num, table_name) == expected


def test_park_table_mapper_not_init_error(db, unittest_settings):
    park_table_mapper = postgres.ParkTableMapper(db, unittest_settings)

    with pytest.raises(postgres.MapCacheNotInitialized):
        park_table_mapper.get_shard_num_and_table_name(
            'foo', postgres.Table.ORDERS,
        )
