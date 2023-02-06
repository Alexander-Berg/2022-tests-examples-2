import aiohttp
import pytest

from supportai_lib.tasks import constants


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
@pytest.mark.parametrize('internal', [False, True])
async def test_upload_download_file(web_app_client, internal):

    file_name = 'test.xlsx'
    file_data = b'test_data'

    form = aiohttp.FormData()
    form.add_field(
        name='file',
        value=file_data,
        filename=file_name,
        content_type=constants.XLSX_CONTENT_TYPE,
    )

    if internal:
        form.add_field(name='filename', value=file_name)

        form.add_field(name='content_type', value=constants.XLSX_CONTENT_TYPE)

    prefix = '/supportai-tasks' if internal else ''

    response = await web_app_client.post(
        f'{prefix}/v1/files?user_id=34&project_id=1', data=form,
    )

    assert response.status == 200

    response_json = await response.json()
    file = response_json['file'] if not internal else response_json

    file_id = file['id']

    assert file_id is not None
    assert file['filename'] == file_name
    assert file['content_type'] == constants.XLSX_CONTENT_TYPE

    response = await web_app_client.get(
        f'{prefix}/v1/files/{file_id}?user_id=34&project_id=1',
    )

    assert response.status == 200
    assert (await response.content.read()) == file_data
    assert file_name in response.headers['Content-Disposition']


@pytest.mark.pgsql(
    'supportai_tasks', files=['sample_projects.sql', 'files.sql'],
)
async def test_internal_update_file(web_app_client):

    file_name = 'test.xlsx'
    file_data = b'test_data'

    form = aiohttp.FormData()
    form.add_field(
        name='file',
        value=file_data,
        filename=file_name,
        content_type=constants.XLSX_CONTENT_TYPE,
    )

    response = await web_app_client.put(
        f'/supportai-tasks/v1/files/1', data=form,
    )

    assert response.status == 200

    response_json = await response.json()
    file = response_json

    file_id = file['id']

    assert file_id is not None
    assert file['filename'] == file_name

    response = await web_app_client.get(f'supportai-tasks/v1/files/{file_id}')

    assert response.status == 200
    assert (await response.content.read()) == file_data
    assert file_name in response.headers['Content-Disposition']


@pytest.mark.pgsql(
    'supportai_tasks', files=['sample_projects.sql', 'files.sql'],
)
async def test_get_files_list(web_app_client):
    response = await web_app_client.get(
        f'/v1/files?project_id=1&user_id=007&'
        f'task_type=outgoing_calls_init&limit=10&offset=0',
    )

    assert response.status == 200

    response_json = await response.json()
    assert response_json['total'] == 1
    assert len(response_json['files']) == 1
    assert response_json['files'][0]['filename'] == 'test.xlsx'
    assert response_json['files'][0]['id'] == '1'
