# pylint: disable=protected-access
import pytest
import ydb

from replication.foundation import map_doc_classes


class _TableClient:
    def __init__(self, bulk_upsert):
        self.bulk_upsert = bulk_upsert


class _Driver:
    def __init__(self, table_client):
        self.table_client = table_client


@pytest.mark.parametrize(
    'target_name, data, correct_path_to_table, '
    'correct_rows, correct_column_types',
    [
        (
            'test_ydb',
            [
                map_doc_classes.MapDocInfo(
                    raw_doc_index=1,
                    mapped_doc={'id': 'id1', 'value_1': 1, 'value_2': 2},
                    doc_id='id1',
                ),
                map_doc_classes.MapDocInfo(
                    raw_doc_index=2,
                    mapped_doc={'id': 'id2', 'value_1': 3, 'value_2': 4},
                    doc_id='id2',
                ),
            ],
            '/database/test/ydb/test_ydb',
            [
                {'id': 'id1'.encode(), 'value_1': 1, 'value_2': 2},
                {'id': 'id2'.encode(), 'value_1': 3, 'value_2': 4},
            ],
            ydb.BulkUpsertColumns()
            .add_column('id', ydb.OptionalType(ydb.PrimitiveType.String))
            .add_column('value_1', ydb.OptionalType(ydb.PrimitiveType.Int64))
            .add_column('value_2', ydb.OptionalType(ydb.PrimitiveType.Int64)),
        ),
        (
            'test_ydb_daily',
            [
                map_doc_classes.MapDocInfo(
                    raw_doc_index=1,
                    mapped_doc={
                        'id': 'id1',
                        'updated': 1642162105.358196,
                        'value_1': 1,
                        'value_2': 2,
                    },
                    doc_id='id1',
                ),
            ],
            '/database/test/ydb/test_ydb_daily/2022-01-14',
            [
                {
                    'id': 'id1'.encode(),
                    'updated': 1642162105.358196,
                    'value_1': 1,
                    'value_2': 2,
                },
            ],
            ydb.BulkUpsertColumns()
            .add_column('id', ydb.OptionalType(ydb.PrimitiveType.String))
            .add_column('value_1', ydb.OptionalType(ydb.PrimitiveType.Int64))
            .add_column('value_2', ydb.OptionalType(ydb.PrimitiveType.Int64))
            .add_column('updated', ydb.OptionalType(ydb.PrimitiveType.Double)),
        ),
        (
            'test_ydb_monthly',
            [
                map_doc_classes.MapDocInfo(
                    raw_doc_index=1,
                    mapped_doc={
                        'id': 'id1',
                        'updated': 1642162105.358196,
                        'value_1': 1,
                        'value_2': 2,
                    },
                    doc_id='id1',
                ),
            ],
            '/database/test/ydb/test_ydb_monthly/2022-01',
            [
                {
                    'id': 'id1'.encode(),
                    'updated': 1642162105.358196,
                    'value_1': 1,
                    'value_2': 2,
                },
            ],
            ydb.BulkUpsertColumns()
            .add_column('id', ydb.OptionalType(ydb.PrimitiveType.String))
            .add_column('value_1', ydb.OptionalType(ydb.PrimitiveType.Int64))
            .add_column('value_2', ydb.OptionalType(ydb.PrimitiveType.Int64))
            .add_column('updated', ydb.OptionalType(ydb.PrimitiveType.Double)),
        ),
        (
            'test_ydb_annually',
            [
                map_doc_classes.MapDocInfo(
                    raw_doc_index=1,
                    mapped_doc={
                        'id': 'id1',
                        'updated': 1642162105.358196,
                        'value_1': 1,
                        'value_2': 2,
                    },
                    doc_id='id1',
                ),
            ],
            '/database/test/ydb/test_ydb_annually/2022',
            [
                {
                    'id': 'id1'.encode(),
                    'updated': 1642162105.358196,
                    'value_1': 1,
                    'value_2': 2,
                },
            ],
            ydb.BulkUpsertColumns()
            .add_column('id', ydb.OptionalType(ydb.PrimitiveType.String))
            .add_column('value_1', ydb.OptionalType(ydb.PrimitiveType.Int64))
            .add_column('value_2', ydb.OptionalType(ydb.PrimitiveType.Int64))
            .add_column('updated', ydb.OptionalType(ydb.PrimitiveType.Double)),
        ),
    ],
)
async def test_insert_data(
        monkeypatch,
        replication_ctx,
        target_name,
        data,
        correct_path_to_table,
        correct_rows,
        correct_column_types,
):
    target = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        target_names=[target_name],
    )[0].targets[0]
    ydb_client = target._ydb_client

    async def _bulk_upsert(path_to_table, rows, column_types):
        assert path_to_table == correct_path_to_table
        assert rows == correct_rows
        assert str(column_types) == str(correct_column_types)

    async def _get_driver():
        return _Driver(_TableClient(_bulk_upsert))

    async def _create_table(*args, **kwargs):
        pass

    monkeypatch.setattr(ydb_client, '_get_driver', _get_driver)
    monkeypatch.setattr(ydb_client, 'create_table', _create_table)
    await target.insert_data(data)
