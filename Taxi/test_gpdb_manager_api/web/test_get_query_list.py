import pytest


@pytest.mark.pgsql('gpbm', files=['query_list_active.sql'])
async def test_get_query_list_active(
        web_app_client, gpdb_manager_api_auth_mock, load_json,
):
    response = await web_app_client.get(
        '/internal/gpdb-manager-api/v1/query/list',
        params={'status': 'active', 'database_name': 'ritchie'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == load_json('query_list_active.json')


@pytest.mark.pgsql('gpbm', files=['query_list_idle.sql'])
async def test_get_query_list_idle(
        web_app_client, gpdb_manager_api_auth_mock, load_json,
):
    response = await web_app_client.get(
        '/internal/gpdb-manager-api/v1/query/list',
        params={'status': 'idle', 'database_name': 'ritchie'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == load_json('query_list_idle.json')


@pytest.mark.pgsql('gpbm', files=['query_list_active.sql'])
async def test_get_query(
        web_app_client, gpdb_manager_api_auth_mock, load_json,
):
    response = await web_app_client.get(
        '/internal/gpdb-manager-api/v1/query/355836',
        params={'database_name': 'ritchie'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == load_json('single_query.json')


@pytest.mark.pgsql('gpbm', files=['query_list_active.sql'])
async def test_query_not_found(
        web_app_client, gpdb_manager_api_auth_mock, load_json,
):
    response = await web_app_client.get(
        '/internal/gpdb-manager-api/v1/query/1111111',
        params={'database_name': 'ritchie'},
    )
    assert response.status == 404
