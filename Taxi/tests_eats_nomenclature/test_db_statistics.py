import pytest

PERIODIC_NAME = 'eats_nomenclature-collect_metrics-db'
METRICS_NAME = 'db-metrics'


@pytest.mark.suspend_periodic_tasks('db-metrics')
async def test_dead_tuples_metric(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor,
):
    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    dead_tuples_metric_name = 'dead_tuples'
    assert dead_tuples_metric_name in metrics[METRICS_NAME]
    assert metrics[METRICS_NAME][dead_tuples_metric_name] in {0, 1}


@pytest.mark.suspend_periodic_tasks('db-metrics')
async def test_picture_processing_errors(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, pgsql,
):
    sql_fill_pictures(pgsql)
    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    metric_name = 'picture_processing_errors'
    assert metrics[METRICS_NAME][metric_name] == 3


@pytest.mark.suspend_periodic_tasks('db-metrics')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_statistics.sql'],
)
async def test_tables_and_indexes_statistics(
        taxi_eats_nomenclature, taxi_eats_nomenclature_monitor, pgsql,
):
    await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)

    metrics = await taxi_eats_nomenclature_monitor.get_metrics()
    metric_values = metrics[METRICS_NAME]
    assert metric_values['total_tables_size'] == sql_get_total_tables_size(
        pgsql,
    )
    assert metric_values['total_indexes_size'] == sql_get_total_indexes_size(
        pgsql,
    )
    assert metric_values['total_dead_tuples'] == sql_get_total_dead_tuples(
        pgsql,
    )
    assert metric_values[
        'total_temp_files_size'
    ] == sql_get_total_temp_files_size(pgsql)

    assert metric_values['size_per_table']['$meta'] == {
        'solomon_children_labels': 'entity_name',
    }
    assert dict_without_key(
        metric_values['size_per_table'], '$meta',
    ) == sql_get_size_per_table(pgsql)

    assert metric_values['size_per_index']['$meta'] == {
        'solomon_children_labels': 'entity_name',
    }
    assert dict_without_key(
        metric_values['size_per_index'], '$meta',
    ) == sql_get_size_per_index(pgsql)

    assert metric_values['dead_tuples_per_table']['$meta'] == {
        'solomon_children_labels': 'entity_name',
    }
    assert dict_without_key(
        metric_values['dead_tuples_per_table'], '$meta',
    ) == sql_get_dead_tuples_per_table(pgsql)


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=False)


def sql_fill_pictures(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.pictures(
            id, url, processing_error
        )
        values (1, 'url1', 'error1'),
               (2, 'url2', 'error2'),
               (3, 'url3', 'error3'),
               (4, 'url4', null),
               (5, 'url5', null)
        """,
    )


def sql_get_total_tables_size(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            select
                coalesce(sum(pg_relation_size('"' || table_schema ||
                    '"."' || table_name || '"')), 0)::bigint as size
            from information_schema.tables
        """,
    )
    return cursor.fetchone()[0]


def sql_get_total_indexes_size(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            select
                coalesce(sum(pg_relation_size('"' || schemaname || '"."'
                    || indexname || '"')), 0)::bigint as size
            from pg_indexes
        """,
    )
    return cursor.fetchone()[0]


def sql_get_total_dead_tuples(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            select coalesce(sum(n_dead_tup), 0)::bigint
            from pg_stat_user_tables
        """,
    )
    return cursor.fetchone()[0]


def sql_get_total_temp_files_size(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            select coalesce(sum(temp_bytes), 0)::bigint as size
            from pg_stat_database
        """,
    )
    return cursor.fetchone()[0]


def sql_get_size_per_table(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            select
                table_schema || '.' || table_name as table_name,
                pg_relation_size('"' || table_schema ||
                    '"."' || table_name || '"') as size
            from information_schema.tables
            order by size desc
        """,
    )
    return {row[0]: row[1] for row in cursor.fetchall()}


def sql_get_size_per_index(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            select
                schemaname || '.' || indexname as index_name,
                pg_relation_size('"' || schemaname ||
                    '"."' || indexname || '"') as size
            from pg_indexes
            order by size desc
        """,
    )
    return {row[0]: row[1] for row in cursor.fetchall()}


def sql_get_dead_tuples_per_table(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            select
                schemaname || '.' || relname as table_name,
                coalesce(n_dead_tup, 0)::bigint as dead_count
            from pg_stat_user_tables
            where relname is not null
            order by dead_count desc
        """,
    )
    return {row[0]: row[1] for row in cursor.fetchall()}


def dict_without_key(obj, key):
    return {x: obj[x] for x in obj if x != key}
