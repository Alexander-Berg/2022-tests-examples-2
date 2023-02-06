# TODO: activate it after testsuite resolve yt_apply problems
import pytest

from crm_admin.generated.cron import run_cron


@pytest.mark.yt(static_table_data=['yt_v_dim_full_geo_hierarchy.yaml'])
async def test_geo_hierarchy_update(yt_apply, yt_client, web_context):
    await run_cron.main(['crm_admin.crontasks.geo_hierarchy', '-t', '0'])

    pool = web_context.pg.master_pool
    async with pool.acquire() as conn:
        c_rows = await conn.fetch(
            'select * from crm_admin.geo_hierarchy_countries order '
            'by node_id',
        )
        z_rows = await conn.fetch(
            'select * from crm_admin.geo_hierarchy_zones order by node_id',
        )

    from_db = list(map(dict, c_rows))

    assert len(from_db) == 4
    assert from_db == [
        {'node_id': 'br_azerbaijan', 'name_ru': 'Азербайджан'},
        {'node_id': 'br_belarus', 'name_ru': 'Белоруссия'},
        {'name_ru': 'Кот-д\'Ивуар', 'node_id': 'br_cote_divoire'},
        {'node_id': 'br_russia', 'name_ru': 'Россия'},
    ]

    from_db = list(map(dict, z_rows))

    assert len(from_db) == 6
    assert from_db == [
        {
            'node_id': 'br_baku',
            'name_ru': 'Баку',
            'tz_country_node_id': 'br_azerbaijan',
            'node_type': 'agglomeration',
        },
        {
            'node_id': 'br_blagoveshchensk',
            'name_ru': 'Благовещенск',
            'tz_country_node_id': 'br_russia',
            'node_type': 'agglomeration',
        },
        {
            'node_id': 'br_bobruisk',
            'name_ru': 'Бобруйск',
            'tz_country_node_id': 'br_belarus',
            'node_type': 'agglomeration',
        },
        {
            'node_id': 'br_brest',
            'name_ru': 'Брест',
            'tz_country_node_id': 'br_belarus',
            'node_type': 'agglomeration',
        },
        {
            'node_id': 'br_brjanskaja_obl',
            'name_ru': 'Брянская область',
            'tz_country_node_id': 'br_belarus',
            'node_type': 'node',
        },
        {
            'node_id': 'br_cherepovets',
            'name_ru': 'Череповец',
            'tz_country_node_id': 'br_russia',
            'node_type': 'agglomeration',
        },
    ]
