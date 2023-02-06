# pylint: disable=protected-access
import typing as tp

import attr
import pytest
import ydb


@attr.dataclass(frozen=True)
class _TableDescription:
    path_to_table: str
    columns: tp.List[ydb.Column]
    primary_keys: tp.List[str]
    compression: tp.Optional[ydb.Compression] = None


@pytest.mark.parametrize(
    'target_name, table_descriptions',
    [
        (
            'test_ydb',
            [
                _TableDescription(
                    path_to_table='test/ydb/test_ydb',
                    columns=[
                        ydb.Column(
                            name='id',
                            type=ydb.OptionalType(ydb.PrimitiveType.String),
                        ),
                        ydb.Column(
                            name='value_1',
                            type=ydb.OptionalType(ydb.PrimitiveType.Int64),
                        ),
                        ydb.Column(
                            name='value_2',
                            type=ydb.OptionalType(ydb.PrimitiveType.Int64),
                        ),
                    ],
                    primary_keys=['id'],
                    compression=ydb.Compression.LZ4,
                ),
            ],
        ),
        (
            'test_ydb_daily',
            [
                _TableDescription(
                    path_to_table='test/ydb/test_ydb_daily/2022-01-10',
                    columns=[
                        ydb.Column(
                            name='id',
                            type=ydb.OptionalType(ydb.PrimitiveType.String),
                        ),
                        ydb.Column(
                            name='value_1',
                            type=ydb.OptionalType(ydb.PrimitiveType.Int64),
                        ),
                        ydb.Column(
                            name='value_2',
                            type=ydb.OptionalType(ydb.PrimitiveType.Int64),
                        ),
                        ydb.Column(
                            name='updated',
                            type=ydb.OptionalType(ydb.PrimitiveType.Double),
                        ),
                    ],
                    primary_keys=['id'],
                    compression=ydb.Compression.LZ4,
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2022-01-10T18:29:12')
async def test_ensure_exists(
        monkeypatch, replication_ctx, target_name, table_descriptions,
):
    monkeypatch.setattr(
        replication_ctx,
        'secdist',
        {
            'ydb_settings': {
                'replication': {
                    'endpoint': 'endpoint',
                    'database': 'database',
                    'token': 'token',
                },
            },
        },
    )
    target = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        target_names=[target_name],
    )[0].targets[0]
    ydb_client = target._ydb_client
    result_table_descriptions = []

    async def _create_table(
            path_to_table: str,
            columns: tp.List[ydb.Column],
            primary_keys: tp.List[str],
            compression: tp.Optional[ydb.Compression],
    ):
        result_table_descriptions.append(
            _TableDescription(
                path_to_table=path_to_table,
                columns=columns,
                primary_keys=primary_keys,
                compression=compression,
            ),
        )

    monkeypatch.setattr(ydb_client, 'create_table', _create_table)
    await target.ensure_exists()
    assert result_table_descriptions == table_descriptions
