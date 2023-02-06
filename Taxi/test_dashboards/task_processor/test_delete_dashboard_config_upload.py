import pytest

from dashboards.internal.models import configs_upload


@pytest.fixture(name='configs_upload_manager')
def _configs_upload_manager(web_context):
    return configs_upload.ConfigsUploadManager(web_context)


@pytest.fixture(name='init_test_data')
async def _init_test_data(configs_upload_manager):
    db_manager = configs_upload_manager
    await db_manager.add(
        vendor=configs_upload.ConfigUploadVendor.GITHUB,
        content='content1',
        filepath='filepath1',
    )
    await db_manager.add(
        vendor=configs_upload.ConfigUploadVendor.ARCADIA,
        content='content1',
        filepath='filepath1',
    )
    await db_manager.add(
        vendor=configs_upload.ConfigUploadVendor.GITHUB,
        content='content2',
        filepath='filepath2',
    )
    await db_manager.add(
        vendor=configs_upload.ConfigUploadVendor.ARCADIA,
        content='content2',
        filepath='filepath2',
    )
    await db_manager.set_status(
        [1, 2, 3, 4], configs_upload.ConfigUploadStatus.APPLIED,
    )


@pytest.mark.usefixtures('init_test_data')
async def test_delete_config_upload(call_cube, configs_upload_manager):
    response = await call_cube(
        'DeleteDashboardConfigUpload', {'config_upload_ids': [1, 2]},
    )
    assert response['status'] == 'success'
    all_records = await configs_upload_manager.fetch()
    assert {record.id for record in all_records} == {3, 4}
