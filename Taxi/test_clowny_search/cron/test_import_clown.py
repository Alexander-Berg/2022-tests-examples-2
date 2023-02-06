import pytest

from clowny_search.generated.cron import run_cron


@pytest.mark.pgsql('clowny_search', files=['add_test_data.sql'])
async def test_cron_import_clown(mock_stats, mock_clown, web_context):
    await run_cron.main(['clowny_search.crontasks.import_clown', '-t', '0'])
    async with web_context.pg.primary.acquire() as conn:
        rows = await conn.fetch(
            'SELECT * FROM clowny_search.imported_services',
        )
        assert len(rows) == 4
        assert rows[0]['clownductor_project'] == '1'
        assert rows[0]['cluster_name'] == 'alpha'
        assert rows[0]['service_id'] == 10
        assert rows[0]['abc_slug'] == 'taxiuserviceslug10'

        project_rows = await conn.fetch(
            'SELECT * FROM clowny_search.imported_projects',
        )
        assert len(project_rows) == 2
        assert project_rows[0]['id'] == 1
        assert project_rows[0]['name'] == 'proj_1'
        assert project_rows[1]['id'] == 2
        assert project_rows[1]['name'] == 'proj_2'
