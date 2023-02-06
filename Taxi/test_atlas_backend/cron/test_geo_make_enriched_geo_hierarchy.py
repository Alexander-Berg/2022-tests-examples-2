import json

import pytest

from atlas_backend.generated.cron import run_cron


async def check_result(web_context, expected):
    async with web_context.pg.master_pool.acquire() as conn:
        stored_data = [
            dict(row)
            for row in await conn.fetch(
                """
        select * from taxi_db_postgres_atlas_backend.geo_node_info
        """,
            )
        ]
        assert stored_data == expected


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
async def test_geo_make_enriched_hierarchy(open_file, web_context):
    with open_file('data.json') as fin:
        test_data = json.load(fin)
    await run_cron.main(
        ['atlas_backend.crontasks.geo.make_enriched_geo_hierarchy', '-t', '0'],
    )
    await check_result(web_context, test_data['expected'])

    # Check no duplicates on second update
    await run_cron.main(
        ['atlas_backend.crontasks.geo.make_enriched_geo_hierarchy', '-t', '0'],
    )
    await check_result(web_context, test_data['expected'])
