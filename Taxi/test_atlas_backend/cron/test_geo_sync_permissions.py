import contextlib
import datetime

from atlas_backend.generated.cron import run_cron

TEST_TZ_PERMISSIONS = [['test_user1', 'moscow'], ['test_user2', 'omsk']]

TEST_GEO_PERMISSIONS = [
    [6, 'br_reutov', 'Реутов', 'node', 'fi_root', 'test_user1', '0001'],
    [
        4,
        'br_novgorod_region',
        'Новгородский регион',
        'agglomeration',
        'fi_root',
        'test_user2',
        '0002',
    ],
]


async def _prepare_tz_perm_table(greenplum_conn):
    create_query = f"""
            CREATE TABLE  IF NOT EXISTS
            taxi_cdm_geo.dim_tariff_zone_permission(
            _etl_processed_dttm TIMESTAMP,
            yandex_passport_login VARCHAR,
            tariff_geo_zone_name VARCHAR
            );
            """
    etl_time = datetime.datetime.now()

    await greenplum_conn.execute(create_query)
    await greenplum_conn.copy_records_to_table(
        table_name='dim_tariff_zone_permission',
        schema_name='taxi_cdm_geo',
        records=[[etl_time] + perm for perm in TEST_TZ_PERMISSIONS],
        columns=[
            '_etl_processed_dttm',
            'yandex_passport_login',
            'tariff_geo_zone_name',
        ],
    )
    return etl_time


async def _prepare_geo_perm_table(greenplum_conn):
    create_query = """
        CREATE TABLE IF NOT EXISTS taxi_cdm_geo.dim_geo_node_permission
        (
            _etl_processed_dttm TIMESTAMP,
            geo_node_depth INTEGER,
            geo_node_id VARCHAR,
            geo_node_name_ru VARCHAR,
            geo_node_type VARCHAR,
            geo_root_node_id VARCHAR,
            yandex_passport_login VARCHAR,
            staff_uid VARCHAR
        )"""
    etl_time = datetime.datetime.now()

    await greenplum_conn.execute(create_query)
    await greenplum_conn.copy_records_to_table(
        table_name='dim_geo_node_permission',
        schema_name='taxi_cdm_geo',
        records=[[etl_time] + perm for perm in TEST_GEO_PERMISSIONS],
        columns=[
            '_etl_processed_dttm',
            'geo_node_depth',
            'geo_node_id',
            'geo_node_name_ru',
            'geo_node_type',
            'geo_root_node_id',
            'yandex_passport_login',
            'staff_uid',
        ],
    )
    return etl_time


async def _prepare_gp_tables(web_context):
    async with contextlib.AsyncExitStack() as stack:
        pool = await stack.enter_async_context(
            web_context.greenplum.get_pool(),
        )
        greenplum_conn = await stack.enter_async_context(pool.acquire())
        await greenplum_conn.execute(
            'CREATE SCHEMA IF NOT EXISTS taxi_cdm_geo;',
        )

        tz_etl = await _prepare_tz_perm_table(greenplum_conn)
        geo_etl = await _prepare_geo_perm_table(greenplum_conn)

    return tz_etl, geo_etl


async def _check_tz_data(web_context, tz_etl):
    async with web_context.pg.master_pool.acquire() as conn:
        stored_data = [
            [row['yandex_passport_login'], row['tariff_geo_zone_name']]
            for row in await conn.fetch(
                """
                SELECT * FROM
                    taxi_db_postgres_atlas_backend.tariff_zone_permission
                """,
            )
        ]
        assert sorted(stored_data) == sorted(TEST_TZ_PERMISSIONS)

        cached = await conn.fetch(
            """
            SELECT * FROM taxi_db_postgres_atlas_backend.cache_info
            WHERE cache_name = 'dim_tariff_zone_permission'
            """,
        )
        assert len(cached) == 1
        assert dict(cached[0]) == {
            'cache_name': 'dim_tariff_zone_permission',
            'source': 'dim_tariff_zone_permission',
            'modification_time': tz_etl.isoformat(),
        }


async def _check_geo_data(web_context, geo_etl):
    columns = ['root_node_id', 'node_id', 'yandex_passport_login']
    async with web_context.pg.master_pool.acquire() as conn:
        stored_data = [
            [row[column] for column in columns]
            for row in await conn.fetch(
                """
                SELECT * FROM
                    taxi_db_postgres_atlas_backend.geo_node_permission
                """,
            )
        ]
        test_data = [
            [
                row[4],  # geo_root_node_id
                row[1],  # geo_node_id
                row[5],  # yandex_passport_login
            ]
            for row in TEST_GEO_PERMISSIONS
        ]
        assert sorted(stored_data) == sorted(test_data)

        cached = await conn.fetch(
            """
            SELECT * FROM taxi_db_postgres_atlas_backend.cache_info
            WHERE cache_name = 'dim_geo_node_permission'
            """,
        )
        assert len(cached) == 1
        assert dict(cached[0]) == {
            'cache_name': 'dim_geo_node_permission',
            'source': 'dim_geo_node_permission',
            'modification_time': geo_etl.isoformat(),
        }


async def test_geo_sync_geo_hierarchy(
        open_file, web_context, atlas_blackbox_mock, patch, caplog,
):
    tz_etl, geo_etl = await _prepare_gp_tables(web_context)
    await run_cron.main(
        ['atlas_backend.crontasks.geo.sync_geo_permissions', '-t', '0'],
    )

    await _check_tz_data(web_context, tz_etl)
    await _check_geo_data(web_context, geo_etl)

    await run_cron.main(
        ['atlas_backend.crontasks.geo.sync_geo_permissions', '-t', '1'],
    )
    nothing_todo = [
        rec
        for rec in caplog.records
        if rec.name == 'atlas_backend.internal.crontasks.geo_permissions'
        and (
            'No new updates for dim_tariff_zone_permission.' in rec.message
            or 'No new updates for dim_geo_node_permission.' in rec.message
        )
    ]

    assert len(nothing_todo) == 2
