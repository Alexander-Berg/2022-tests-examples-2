import pytest

from dashboards.internal.models import configs_upload


@pytest.fixture(name='init_test_data')
async def _init_test_data(web_context):
    db_manager = configs_upload.ConfigsUploadManager(web_context)
    await db_manager.add(
        vendor=configs_upload.ConfigUploadVendor.GITHUB,
        content='content',
        filepath='filepath',
    )
    await db_manager.add(
        vendor=configs_upload.ConfigUploadVendor.ARCADIA,
        content='content',
        filepath='filepath',
    )


@pytest.fixture(name='update_test_data')
async def _update_test_data(web_context):
    db_manager = configs_upload.ConfigsUploadManager(web_context)
    await db_manager.set_status(
        [1, 2], configs_upload.ConfigUploadStatus.APPLIED,
    )


@pytest.fixture(name='call_wait_cube')
def _call_wait_cube(call_cube):
    async def _wrapper():
        response = await call_cube(
            'WaitDashboardConfigUpload', {'config_upload_ids': [1, 2]},
        )
        return response

    return _wrapper


@pytest.mark.usefixtures('init_test_data')
async def test_wait_in_progress(call_wait_cube):
    response = await call_wait_cube()
    assert response['status'] == 'in_progress'


@pytest.mark.usefixtures('init_test_data', 'update_test_data')
async def test_wait_success(call_wait_cube):
    response = await call_wait_cube()
    assert response['status'] == 'success'
