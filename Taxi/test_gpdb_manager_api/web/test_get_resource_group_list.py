import pytest


@pytest.mark.pgsql('gpbm', files=['resource_group.sql'])
async def test_get_resource_group_list(
        web_app_client, gpdb_manager_api_auth_mock, load_json,
):
    response = await web_app_client.get(
        '/internal/gpdb-manager-api/v1/resource-group/list',
        params={'database_name': 'ritchie'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == load_json('resource_group.json')
