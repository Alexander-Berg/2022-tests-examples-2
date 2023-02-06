import pytest


@pytest.mark.pgsql('gpbm', files=['restore.sql'])
async def test_get_restore_status(
        web_app_client, gpdb_manager_api_auth_mock, load_json,
):
    queue_name = 'restore'
    process_uuid = '68369174-60d2-b0d9-a87c-b9973aea1570'
    response = await web_app_client.get(
        f'/internal/gpdb-manager-api/v1/process/{queue_name}/{process_uuid}',
    )

    assert response.status == 200
    content = await response.json()
    assert content == load_json('restore.json')


@pytest.mark.pgsql('gpbm', files=['backup.sql'])
async def test_get_backup_status(
        web_app_client, gpdb_manager_api_auth_mock, load_json,
):
    queue_name = 'backup'
    backup_uuid = '007df841-63d5-b905-d027-d6303c532f24'
    response = await web_app_client.get(
        f'/internal/gpdb-manager-api/v1/process/{queue_name}/{backup_uuid}',
    )

    assert response.status == 200
    content = await response.json()
    assert content == load_json('backup.json')


@pytest.mark.pgsql('gpbm', files=['restore.sql'])
async def test_process_not_found(
        web_app_client, gpdb_manager_api_auth_mock, load_json,
):
    queue_name = 'restore'
    process_uuid = '68369174-60d2-b0d9-a87c-b9973aea1571'
    response = await web_app_client.get(
        f'/internal/gpdb-manager-api/v1/process/{queue_name}/{process_uuid}',
    )

    assert response.status == 404
