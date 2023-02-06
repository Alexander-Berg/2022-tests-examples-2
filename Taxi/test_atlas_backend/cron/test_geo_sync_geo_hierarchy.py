import contextlib
import json

from atlas_backend.generated.cron import run_cron


async def check_result(web_context, expected):
    async with web_context.pg.master_pool.acquire() as conn:
        stored_data = [
            dict(row)
            for row in await conn.fetch(
                """
        select * from taxi_db_postgres_atlas_backend.full_geo_hierarchy
        """,
            )
        ]
        assert stored_data == expected


async def test_geo_sync_geo_hierarchy(
        open_file, web_context, atlas_blackbox_mock, patch,
):
    with open_file('data.json') as fin:
        test_data = json.load(fin)
    async with contextlib.AsyncExitStack() as stack:
        pool = await stack.enter_async_context(
            web_context.greenplum.get_pool(),
        )
        greenplum_conn = await stack.enter_async_context(pool.acquire())
        columns = '\n, '.join(
            [f'{col[0]} {col[1]}' for col in test_data['columns']],
        )
        await greenplum_conn.execute(
            f"""
        CREATE SCHEMA IF NOT EXISTS core_cdm_geo;""",
        )
        create_query = f"""
        CREATE TABLE  IF NOT EXISTS
        core_cdm_geo.v_dim_full_geo_hierarchy({columns});
        """
        await greenplum_conn.execute(create_query)
        await greenplum_conn.copy_records_to_table(
            table_name='v_dim_full_geo_hierarchy',
            schema_name='core_cdm_geo',
            records=test_data['data'],
            columns=[col[0] for col in test_data['columns']],
        )

    await run_cron.main(
        ['atlas_backend.crontasks.geo.sync_geo_hierarchy', '-t', '0'],
    )

    await check_result(web_context, test_data['expected'])
    # check truncate works
    await run_cron.main(
        ['atlas_backend.crontasks.geo.sync_geo_hierarchy', '-t', '0'],
    )

    await check_result(web_context, test_data['expected'])
