import pytest


@pytest.mark.pgsql('gpbm', files=['uptime.sql'])
async def test_get_uptime(
        web_app_client, gpdb_manager_api_auth_mock, load_json, web_context,
):
    response = await web_app_client.get(
        '/internal/gpdb-manager-api/v1/uptime',
        params={'database_name': 'ritchie'},
    )
    assert response.status == 200
    content = await response.json()
    expected = load_json('uptime.json')
    async with web_context.pg.slave_pool.acquire() as conn:
        current_date = await conn.fetchval(
            'SELECT current_date - interval \'1 day\'',
        )
    expected['points'][0]['day'] = str(current_date.date())
    assert content == expected
