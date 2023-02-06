import datetime

import pytest

from replication.sources.mysql.core import source

NOW = datetime.datetime(2019, 11, 5, 12, 0)


@pytest.mark.parametrize(
    'rule_name,'
    'mysql_docs_by_bounds_file,'
    'mysql_unindexed_docs_file,'
    'mysql_min_ts_file,'
    'mysql_utc_now_file,'
    'mysql_next_ts_file,'
    'expected_queue',
    [
        (
            'mysql_test_rule_raw',
            'docs_by_bounds.json',
            'unindexed_docs.json',
            'min_ts.json',
            'utc_now.json',
            'next_ts.json',
            'expected_staging_data_raw.json',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_mysql_replication(
        replication_ctx,
        mock_mysql_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
        rule_name,
        mysql_docs_by_bounds_file,
        mysql_unindexed_docs_file,
        mysql_min_ts_file,
        mysql_utc_now_file,
        mysql_next_ts_file,
        expected_queue,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name=rule_name, source_types=[source.SOURCE_TYPE_MYSQL],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    mock_mysql_source.apply(
        meta,
        mysql_docs_by_bounds_file,
        mysql_unindexed_docs_file,
        mysql_min_ts_file,
        mysql_utc_now_file,
        mysql_next_ts_file,
    )
    targets_data = await replication_runner.run(
        rule_name, source_type=source.SOURCE_TYPE_MYSQL,
    )
    staging_docs = targets_data.queue_data_by_id(drop_targets_updated=False)
    expected_staging_docs = load_py_json(expected_queue)
    assert (
        staging_docs == expected_staging_docs
    ), 'MySQL replication to queue failed'
    assert mock_mysql_source.queries_history == [
        ('select min(updated_at) as updated_at from dummy', None),
        ('select * from dummy where dummy.updated_at is null', None),
        ('select UTC_TIMESTAMP() as utc_now', None),
        (
            'select * from dummy '
            'where dummy.updated_at >= %s and dummy.updated_at <= %s',
            (
                datetime.datetime(2019, 11, 5, 5, 59),
                datetime.datetime(2019, 11, 5, 6, 4),
            ),
        ),
        (
            'select * from dummy '
            'where dummy.updated_at >= %s and dummy.updated_at <= %s',
            (
                datetime.datetime(2019, 11, 5, 6, 1),
                datetime.datetime(2019, 11, 5, 6, 6),
            ),
        ),
        (
            'select * from dummy '
            'where dummy.updated_at >= %s and dummy.updated_at <= %s',
            (
                datetime.datetime(2019, 11, 5, 6, 6),
                datetime.datetime(2019, 11, 5, 6, 11),
            ),
        ),
        (
            'select min(updated_at) as updated_at from dummy '
            'where dummy.updated_at > %(updated_at)s',
            {'updated_at': datetime.datetime(2019, 11, 5, 6, 6)},
        ),
    ], 'MySQL queries check failed'


@pytest.mark.parametrize(
    'rule_name,'
    'mysql_docs_by_bounds_file,'
    'mysql_unindexed_docs_file,'
    'mysql_min_ts_file,'
    'mysql_max_ts_file,'
    'expected_queue',
    [
        (
            'mysql_test_rule_sequence',
            'docs_by_bounds.json',
            'unindexed_docs.json',
            'min_ts.json',
            'max_ts.json',
            'expected_staging_data_sequence.json',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_mysql_replication_sequence(
        replication_ctx,
        mock_mysql_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
        rule_name,
        mysql_docs_by_bounds_file,
        mysql_unindexed_docs_file,
        mysql_min_ts_file,
        mysql_max_ts_file,
        expected_queue,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name=rule_name, source_types=[source.SOURCE_TYPE_MYSQL],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    mock_mysql_source.apply(
        meta,
        mysql_docs_by_bounds_file,
        mysql_unindexed_docs_file,
        mysql_min_ts_file,
        max_ts_file=mysql_max_ts_file,
        utc_now_file=None,
        next_ts_file=None,
    )
    targets_data = await replication_runner.run(
        rule_name, source_type=source.SOURCE_TYPE_MYSQL,
    )
    staging_docs = targets_data.queue_data_by_id(drop_targets_updated=False)
    expected_staging_docs = load_py_json(expected_queue)
    assert (
        staging_docs == expected_staging_docs
    ), 'MySQL replication to queue failed'
    assert mock_mysql_source.queries_history == [
        ('select min(updated_at) as updated_at from dummy', None),
        ('select * from dummy where dummy.updated_at is null', None),
        ('select max(updated_at) as updated_at from dummy', None),
        ('select min(updated_at) as updated_at from dummy', None),
        (
            'select * from dummy where dummy.updated_at is NULL '
            'or dummy.updated_at <= %s',
            (datetime.datetime(2019, 11, 5, 6, 0),),
        ),
        (
            'select * from dummy where dummy.updated_at >= %s '
            'and dummy.updated_at <= %s '
            'order by dummy.updated_at asc limit 10000',
            (
                datetime.datetime(2019, 11, 5, 6, 0),
                datetime.datetime(2019, 11, 5, 6, 6),
            ),
        ),
    ], 'MySQL queries check failed'


@pytest.mark.parametrize(
    'rule_name,'
    'mysql_docs_by_bounds_file,'
    'mysql_unindexed_docs_file,'
    'mysql_min_ts_file,'
    'mysql_utc_now_file,'
    'mysql_next_ts_file,'
    'mysql_max_ts_file,'
    'expected_queue',
    [
        (
            'mysql_test_rule_two_dates',
            'docs_by_bounds_two_dates.json',
            'unindexed_docs.json',
            'min_ts_two_dates.json',
            'utc_now.json',
            'next_ts_two_dates.json',
            'max_ts_two_dates.json',
            'expected_staging_data_two_dates.json',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_mysql_replication_two_dates(
        replication_ctx,
        mock_mysql_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
        rule_name,
        mysql_docs_by_bounds_file,
        mysql_unindexed_docs_file,
        mysql_min_ts_file,
        mysql_utc_now_file,
        mysql_next_ts_file,
        mysql_max_ts_file,
        expected_queue,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name=rule_name, source_types=[source.SOURCE_TYPE_MYSQL],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    mock_mysql_source.apply(
        meta,
        mysql_docs_by_bounds_file,
        mysql_unindexed_docs_file,
        mysql_min_ts_file,
        mysql_utc_now_file,
        mysql_next_ts_file,
        max_ts_file=mysql_max_ts_file,
    )
    targets_data = await replication_runner.run(
        rule_name, source_type=source.SOURCE_TYPE_MYSQL,
    )
    staging_docs = targets_data.queue_data_by_id(drop_targets_updated=False)
    expected_staging_docs = load_py_json(expected_queue)
    assert (
        staging_docs == expected_staging_docs
    ), 'MySQL replication to queue failed'
    assert mock_mysql_source.queries_history == [
        # source.get_reader queries:
        (
            'select '
            'min(updated_at) as updated_at, '
            'min(created_at) as created_at '
            'from dummy',
            None,
        ),
        (
            'select * from dummy '
            'where dummy.updated_at is null '
            'and dummy.created_at is null',
            None,
        ),
        (
            'select max(updated_at) as updated_at, '
            'max(created_at) as created_at from dummy',
            None,
        ),
        (
            'select * from dummy '
            'where (dummy.updated_at between %s and %s) '
            'or (dummy.created_at between %s and %s)',
            (
                datetime.datetime(2019, 11, 5, 6, 0),
                datetime.datetime(2019, 11, 5, 6, 5),
                datetime.datetime(2019, 11, 5, 6, 0),
                datetime.datetime(2019, 11, 5, 6, 5),
            ),
        ),
        (
            'select * from dummy '
            'where (dummy.updated_at between %s and %s) '
            'or (dummy.created_at between %s and %s)',
            (
                datetime.datetime(2019, 11, 5, 6, 3, 20),
                datetime.datetime(2019, 11, 5, 6, 8, 20),
                datetime.datetime(2019, 11, 5, 6, 3, 20),
                datetime.datetime(2019, 11, 5, 6, 8, 20),
            ),
        ),
        (
            'select '
            'min(updated_at) as updated_at, '
            'min(created_at) as created_at '
            'from dummy '
            'where (dummy.updated_at > %(updated_at)s'
            ' and dummy.created_at > %(created_at)s'
            ') or ('
            'dummy.created_at > %(created_at)s'
            ' and dummy.updated_at is null'
            ') or ('
            'dummy.updated_at > %(updated_at)s'
            ' and dummy.created_at is null'
            ')',
            {
                'created_at': datetime.datetime(2019, 11, 5, 6, 3, 20),
                'updated_at': datetime.datetime(2019, 11, 5, 6, 3, 20),
            },
        ),
        (
            'select * from dummy '
            'where (dummy.updated_at between %s and %s) '
            'or (dummy.created_at between %s and %s)',
            (
                datetime.datetime(2019, 11, 5, 6, 20, 20),
                datetime.datetime(2019, 11, 5, 6, 25, 20),
                datetime.datetime(2019, 11, 5, 6, 20, 20),
                datetime.datetime(2019, 11, 5, 6, 25, 20),
            ),
        ),
    ], 'MySQL queries check failed'


@pytest.mark.parametrize(
    'rule_name,' 'mysql_snapshot_docs,' 'expected_queue',
    [
        (
            'mysql_snapshot_test_rule',
            'snapshot_docs.json',
            'snapshot_expected_staging_data.json',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_mysql_snapshot_replication(
        replication_ctx,
        mock_mysql_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
        rule_name,
        mysql_snapshot_docs,
        expected_queue,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name=rule_name, source_types=[source.SOURCE_TYPE_MYSQL],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    mock_mysql_source.apply(
        meta,
        docs_by_bounds_file=None,
        unindexed_docs_file=None,
        min_ts_file=None,
        utc_now_file=None,
        next_ts_file=None,
        snapshot_docs_file=mysql_snapshot_docs,
    )
    targets_data = await replication_runner.run(
        rule_name, source_type=source.SOURCE_TYPE_MYSQL,
    )
    staging_docs = targets_data.queue_data_by_id(drop_targets_updated=False)
    expected_staging_docs = load_py_json(expected_queue)
    assert (
        staging_docs == expected_staging_docs
    ), 'MySQL replication to queue failed'
    assert mock_mysql_source.queries_history == [
        ('select * from dummy_snapshot', None),
    ], 'MySQL queries check failed'


@pytest.mark.parametrize(
    'rule_name,' 'mysql_snapshot_docs,' 'expected_queue',
    [
        (
            'mysql_iterative_snapshot_test_rule',
            'snapshot_docs.json',
            'snapshot_expected_staging_data.json',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_mysql_iterative_snapshot_replication(
        replication_ctx,
        mock_mysql_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
        rule_name,
        mysql_snapshot_docs,
        expected_queue,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name=rule_name, source_types=[source.SOURCE_TYPE_MYSQL],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    mock_mysql_source.apply(
        meta,
        docs_by_bounds_file=None,
        unindexed_docs_file=None,
        min_ts_file=None,
        utc_now_file=None,
        next_ts_file=None,
        snapshot_docs_file=mysql_snapshot_docs,
        snapshot_page_size=3,
    )
    targets_data = await replication_runner.run(
        rule_name, source_type=source.SOURCE_TYPE_MYSQL,
    )
    staging_docs = targets_data.queue_data_by_id(drop_targets_updated=False)
    expected_staging_docs = load_py_json(expected_queue)
    assert (
        staging_docs == expected_staging_docs
    ), 'MySQL replication to queue failed'
    assert mock_mysql_source.queries_history == [
        ('select * from dummy_snapshot order by id_1, id_2 limit 3', None),
        (
            'select * from dummy_snapshot where id_1 > %(id_1)s or '
            'id_2 > %(id_2)s and id_1 = %(id_1)s order by id_1, id_2 limit 3',
            {'id_1': 1, 'id_2': 3},
        ),
        (
            'select * from dummy_snapshot where id_1 > %(id_1)s or '
            'id_2 > %(id_2)s and id_1 = %(id_1)s order by id_1, id_2 limit 3',
            {'id_1': 1, 'id_2': 6},
        ),
        (
            'select * from dummy_snapshot where id_1 > %(id_1)s or '
            'id_2 > %(id_2)s and id_1 = %(id_1)s order by id_1, id_2 limit 3',
            {'id_1': 1, 'id_2': 9},
        ),
        (
            'select * from dummy_snapshot where id_1 > %(id_1)s or '
            'id_2 > %(id_2)s and id_1 = %(id_1)s order by id_1, id_2 limit 3',
            {'id_1': 2, 'id_2': 2},
        ),
        (
            'select * from dummy_snapshot where id_1 > %(id_1)s or '
            'id_2 > %(id_2)s and id_1 = %(id_1)s order by id_1, id_2 limit 3',
            {'id_1': 2, 'id_2': 5},
        ),
    ], 'MySQL queries check failed'


@pytest.mark.parametrize(
    'rule_name,'
    'mysql_docs_by_bounds_file,'
    'mysql_unindexed_docs_file,'
    'mysql_min_ts_file,'
    'mysql_max_ts_file,'
    'expected_queue',
    [
        (
            'mysql_test_rule_sequence',
            'empty_docs.json',
            'empty_docs.json',
            'empty_ts.json',
            'empty_ts.json',
            'expected_staging_empty_data.json',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_replicate_empty_table(
        replication_ctx,
        mock_mysql_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
        rule_name,
        mysql_docs_by_bounds_file,
        mysql_unindexed_docs_file,
        mysql_min_ts_file,
        mysql_max_ts_file,
        expected_queue,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name=rule_name, source_types=[source.SOURCE_TYPE_MYSQL],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    mock_mysql_source.apply(
        meta,
        mysql_docs_by_bounds_file,
        mysql_unindexed_docs_file,
        mysql_min_ts_file,
        max_ts_file=mysql_max_ts_file,
        utc_now_file=None,
        next_ts_file=None,
    )
    targets_data = await replication_runner.run(
        rule_name, source_type=source.SOURCE_TYPE_MYSQL,
    )
    staging_docs = targets_data.queue_data_by_id(drop_targets_updated=False)
    expected_staging_docs = load_py_json(expected_queue)
    assert (
        staging_docs == expected_staging_docs
    ), 'MySQL replication to queue failed'
    assert mock_mysql_source.queries_history == [
        ('select min(updated_at) as updated_at from dummy', None),
    ], 'MySQL queries check failed'
