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
    'target_name, correct_partition',
    [
        ('test_ydb_daily', '2022-01-10'),
        ('test_ydb_monthly', '2022-01'),
        ('test_ydb_annually', '2022'),
    ],
)
@pytest.mark.now('2022-01-10T18:29:12')
async def test_current_table(
        monkeypatch, replication_ctx, target_name, correct_partition,
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
    assert target.meta.partitioning.current_table == correct_partition
