import pytest


@pytest.mark.pgsql('gpbm', files=['queue_stat.sql'])
async def test_get_queue_stat(
        web_app_client, gpdb_manager_api_auth_mock, load_json,
):
    response = await web_app_client.get(
        '/internal/gpdb-manager-api/v1/queue/restore',
    )
    assert response.status == 200
    content = await response.json()
    assert content == load_json('queue_stat.json')


@pytest.mark.pgsql('gpbm', files=['queue_stat.sql'])
async def test_get_restore_detail(
        web_app_client, gpdb_manager_api_auth_mock, load_json,
):
    response = await web_app_client.get(
        '/internal/gpdb-manager-api/v1/queue/restore/detail',
    )
    assert response.status == 200
    content = await response.json()
    assert content == load_json('restore_detail.json')
