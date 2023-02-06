import pytest

from archiving import core
from archiving import cron_run
from test_archiving import conftest

_NOW = '2019-11-21T09:00:00'


@pytest.mark.parametrize(
    'rule_name, replication_rule_name, replicate_by, expected_left_in_db, '
    'primary_key',
    [
        (
            'test_postgres',
            'test_postgres',
            'created_at_ts',
            set(map(str, range(8))),
            ['id'],
        ),
        (
            'test_postgres_tz_replication',
            'test_postgres',
            'created_at_ts_tz',
            set(map(str, range(7))),
            ['id'],
        ),
        (
            'test_postgres_tz_composite_pk',
            'test_postgres',
            'created_at_ts_tz',
            {
                ('0', '00'),
                ('1', '11'),
                ('2', '22'),
                ('3', '33'),
                ('4', '44'),
                ('5', '55'),
                ('6', '66'),
            },
            ['id', 'second_id'],
        ),
        ('test_postgres_tz', None, None, set(map(str, range(7))), ['id']),
    ],
)
@pytest.mark.now(_NOW)
@pytest.mark.pgsql('pg_test', files=['pg_test.sql'])
async def test_postgres_archiving(
        cron_context,
        replication_state_min_ts,
        replication_rule_name,
        replicate_by,
        rule_name,
        expected_left_in_db,
        primary_key,
        fake_task_id,
        requests_handlers,
        patch_test_env,
):
    if replicate_by is not None:
        replication_state_min_ts.apply(
            {replication_rule_name: (replicate_by, _NOW)},
        )
    archivers = await cron_run.prepare_archivers(
        cron_context, rule_name, fake_task_id,
    )
    archiver = next(iter(archivers.values()))
    await core.remove_documents(archiver, cron_context.client_solomon)
    assert (
        set(
            await conftest.load_pg_source_docs(
                archiver, primary_key=primary_key, get_all_columns=True,
            ),
        )
        == expected_left_in_db
    )
    await archiver.close()
