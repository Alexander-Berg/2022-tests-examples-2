# pylint: disable=unused-argument,unused-variable,redefined-outer-name

import aiohttp
import pytest

from crm_admin.entity import error


@pytest.mark.parametrize('campaign_id,status', [(1, 200), (2, 400)])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_upload_csv(web_app_client, patch, pgsql, campaign_id, status):
    attachment_id = 1

    @patch('crm_admin.utils.upload_data_manager.Manager._upload_to_yt')
    async def upload_to_yt(chunks):
        async for chunk in chunks:
            yield chunk

    @patch('crm_admin.utils.upload_data_manager.Manager._upload_to_s3')
    async def upload_to_s3(chunks):
        async for chunk in chunks:
            pass

    content = (
        'db_id,driver_uuid\n'
        '001,0001\n'
        '002,0003\n'
        '004,0005\n'
        '005,0007\n'
        '007,0016\n'
    )

    form_data = aiohttp.FormData()
    form_data.add_field(
        name='file',
        value=content,
        filename='filename',
        content_type='text/plain; charset=utf-8',
    )

    response = await web_app_client.post(
        '/v1/process/upload_csv',
        data=form_data,
        params={'campaign_id': campaign_id},
    )
    assert response.status == status

    if status == 200:
        value = await response.json()
        assert value['data'].endswith('.csv')

        cursor = pgsql['crm_admin'].cursor()
        cursor.execute(
            'select id from crm_admin.uploaded_csv where campaign_id = %s',
            (campaign_id,),
        )
        assert cursor.fetchone() == (attachment_id,)

    else:
        value = await response.json()
        assert 'Not implemented' in value['message']


@pytest.mark.parametrize(
    'case_name,status',
    [
        ('valid_csv', 200),
        ('wrong_delimiter', 400),
        ('missing_db_id', 400),
        ('missing_driver_uuid', 400),
        ('non_ascii_column_names', 400),
        ('duplicate_columns', 400),
        ('empty', 400),
        ('spaces_in_header', 400),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_validate_csv(
        web_app_client, patch, load_json, case_name, status,
):
    campaign_id = 1

    @patch('crm_admin.utils.upload_data_manager.Manager._upload_to_yt')
    async def upload_to_yt(chunks):
        async for chunk in chunks:
            yield chunk

    @patch('crm_admin.utils.upload_data_manager.Manager._upload_to_s3')
    async def upload_to_s3(chunks):
        async for chunk in chunks:
            pass

    @patch('crm_admin.utils.upload_data_manager.Manager.remove_all')
    async def remove_all():
        pass

    cases = load_json('csv-samples.json')

    form_data = aiohttp.FormData()
    form_data.add_field(
        name='file',
        value=cases[case_name],
        filename='filename',
        content_type='text/plain; charset=utf-8',
    )

    response = await web_app_client.post(
        '/v1/process/upload_csv',
        data=form_data,
        params={'campaign_id': campaign_id},
    )
    assert response.status == status


@pytest.mark.pgsql('crm_admin', files=['init.sql', 'init-attachments.sql'])
async def test_upload_error(web_app_client, patch, pgsql):
    campaign_id = 1

    @patch('crm_admin.utils.upload_data_manager.Manager._upload_to_yt')
    async def upload_to_yt(chunks):
        async for chunk in chunks:
            yield chunk

    @patch('crm_admin.utils.upload_data_manager.Manager._upload_to_s3')
    async def upload_to_s3(chunks):
        raise error.UploadError('some error')

    @patch('crm_admin.utils.upload_data_manager.Manager.remove_all')
    async def remove_all():
        pass

    content = (
        'db_id,driver_uuid\n'
        '001,0001\n'
        '002,0003\n'
        '004,0005\n'
        '005,0007\n'
        '007,0016\n'
    )

    form_data = aiohttp.FormData()
    form_data.add_field(
        name='file',
        value=content,
        filename='filename',
        content_type='text/plain; charset=utf-8',
    )

    response = await web_app_client.post(
        '/v1/process/upload_csv',
        data=form_data,
        params={'campaign_id': campaign_id},
    )
    assert response.status == 400

    cursor = pgsql['crm_admin'].cursor()
    cursor.execute(
        'select * from crm_admin.uploaded_csv where campaign_id = %s',
        (campaign_id,),
    )
    assert cursor.fetchone() is None
