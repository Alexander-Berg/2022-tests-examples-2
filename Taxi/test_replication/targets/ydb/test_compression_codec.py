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


@pytest.mark.parametrize(
    'target_name, compression',
    [
        ('test_ydb_compression_lz4', ydb.Compression.LZ4),
        ('test_ydb_compression_off', ydb.Compression.NONE),
        ('test_ydb', ydb.Compression.LZ4),
    ],
)
@pytest.mark.now('2022-01-10T18:29:12')
async def test_compression(
        monkeypatch, replication_ctx, target_name, compression,
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
    assert target.meta.table_meta.compression == compression
