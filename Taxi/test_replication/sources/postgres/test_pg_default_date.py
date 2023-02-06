import datetime

from dateutil.parser import parse
import pytest

from replication.sources.postgres import core as postgres

RULE_DEFAULT = '2020-03-22'

FORMAT = '%Y-%m-%dT%H:%M:%S'


def d_from(date_str):
    return parse(date_str)


@pytest.mark.pgsql('conditioned', files=['conditioned.sql'])
@pytest.mark.parametrize(
    'rule_name, expected',
    [
        (
            'pg_fix_date',
            {
                'id_1_ok': {
                    'created_at': datetime.datetime(2019, 1, 24, 9, 0),
                    'updated_at': datetime.datetime(2019, 1, 24, 11, 0),
                    'magic_ts': datetime.datetime(2019, 1, 24, 11, 0),
                    'magic_date': datetime.date(2019, 1, 24),
                },
                'id_2_tp': {
                    'created_at': datetime.datetime(2019, 1, 24, 5, 0),
                    'updated_at': datetime.datetime(2019, 1, 24, 11, 0),
                    'magic_ts': datetime.datetime(2020, 3, 22, 0, 0),
                    'magic_date': datetime.date(2019, 1, 24),
                },
                'id_3_tpx': {
                    'created_at': datetime.datetime(2020, 3, 22, 0, 0),
                    'updated_at': datetime.datetime(2019, 1, 24, 11, 0),
                    'magic_ts': datetime.datetime(2019, 1, 24, 11, 0),
                    'magic_date': datetime.date(2019, 1, 24),
                },
                'id_4_date': {
                    'created_at': datetime.datetime(2019, 1, 24, 9, 0),
                    'updated_at': datetime.datetime(2019, 1, 24, 11, 0),
                    'magic_ts': datetime.datetime(2019, 1, 24, 11, 0),
                    'magic_date': datetime.date(2020, 3, 22),
                },
                'id_5_null': {
                    'created_at': None,
                    'magic_ts': None,
                    'updated_at': datetime.datetime(2019, 1, 24, 11, 0),
                    'magic_date': None,
                },
            },
        ),
        (
            'pg_no_fix_date',
            {
                'id_1_ok': {
                    'created_at': datetime.datetime(2019, 1, 24, 8, 0),
                    'updated_at': datetime.datetime(2019, 1, 24, 11, 0),
                    'magic_date': datetime.datetime(2019, 1, 24),
                    'magic_ts': None,
                },
                'id_5_null': {
                    'created_at': datetime.datetime(2019, 1, 24, 8, 0),
                    'updated_at': datetime.datetime(2019, 1, 24, 11, 0),
                    'magic_date': None,
                    'magic_ts': None,
                },
            },
        ),
    ],
)
async def test_pg_replication_date(run_replication, rule_name, expected):
    targets_data = await run_replication(rule_name, source_type='postgres')
    queue_docs = targets_data.queue_data_by_id(drop_confirmations=True)
    queue_docs = {
        doc_id: {
            'created_at': doc['data']['created_at'],
            'updated_at': doc['data']['updated_at'],
            'magic_ts': (
                doc['data']['magic_ts'] if 'magic_ts' in doc['data'] else None
            ),
            'magic_date': doc['data']['magic_date'],
        }
        for doc_id, doc in queue_docs.items()
    }
    assert queue_docs == expected


@pytest.mark.pgsql('conditioned', files=['conditioned.sql'])
async def test_pg_replication_date_without_fix(run_replication):
    with pytest.raises(OverflowError) as error:
        targets_data = await run_replication(
            'pg_no_fix_date_err', source_type='postgres',
        )
        targets_data.queue_data_by_id(drop_confirmations=True)
    assert 'date value out of range' in str(error.value)


@pytest.mark.parametrize(
    ('task_name', 'broken_date_default'),
    [('pg_fix_date', '2020-03-22'), ('pg_no_fix_date', None)],
)
async def test_fix_date_default_flag(
        replication_tasks_getter, task_name: str, broken_date_default: bool,
):
    tasks = await replication_tasks_getter(
        postgres.SOURCE_TYPE_POSTGRES, task_name,
    )
    assert len(tasks) == 1
    assert tasks[0].source.meta.broken_date_default == broken_date_default
