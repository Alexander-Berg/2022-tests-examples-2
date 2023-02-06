import asyncio
import io

import aiohttp
from aiohttp import web
import pytest
import xlsxwriter

from taxi.clients import mds_s3

from supportai_calls.utils import constants
from supportai_calls.utils import external_phone_id_helpers


async def test_upload_download_file(web_app_client):
    file_name = 'test.xlsx'
    file_data = b'test_data'

    form = aiohttp.FormData()
    form.add_field(
        name='file',
        value=file_data,
        filename=file_name,
        content_type=constants.XLSX_CONTENT_TYPE,
    )

    response = await web_app_client.post(
        '/v1/files?user_id=34&project_slug=test', data=form,
    )

    assert response.status == 200

    response_json = await response.json()
    file = response_json['file']

    file_id = file['id']

    assert file_id is not None
    assert file['filename'] == file_name
    assert file['content_type'] == constants.XLSX_CONTENT_TYPE

    response = await web_app_client.get(
        f'/v1/files/{file_id}?user_id=34&project_slug=test',
    )

    assert response.status == 200
    assert (await response.content.read()) == file_data
    assert file_name in response.headers['Content-Disposition']


@pytest.mark.pgsql('supportai_calls', files=['upload_files.sql'])
async def test_upload_calls_audio_file(web_app_client, load_binary, patch):
    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _upload_content(*args, **kwargs):
        return mds_s3.S3Object(Key='mds-id', ETag=None)

    try:
        proc = await asyncio.create_subprocess_exec('ffmpeg', '-version')

        await proc.communicate()

        ffmpeg_exists = proc.returncode == 0
    except FileNotFoundError:
        ffmpeg_exists = False

    file_name = 'test.m4a'
    file_data = load_binary(file_name)

    form = aiohttp.FormData()
    form.add_field(
        name='file',
        value=file_data,
        filename=file_name,
        content_type='audio/m4a',
    )

    response = await web_app_client.post(
        '/v1/files/audio?user_id=34&project_slug=test', data=form,
    )

    assert response.status == (200 if ffmpeg_exists else 400)


@pytest.mark.pgsql('supportai_calls', files=['outgoing_calls.sql'])
async def test_download_call_record_file_ivr(web_app_client, mockserver):
    file_data_ivr_framework = b'test_data_ivr_framework'

    @mockserver.json_handler(
        '/ivr-dispatcher/v1/ivr-framework/get-call-record',
    )
    async def _(request):
        assert (
            request.query['call_record_id'] == 'call_record_id_ivr_framework'
        )
        assert request.query['ivr_flow_id'] == 'test_ivr_framework'
        return web.Response(
            body=file_data_ivr_framework, content_type='audio/wav',
        )

    response = await web_app_client.get(
        f'/v1/files/calls/1/record?user_id=34&project_slug=test_ivr_framework',
    )
    assert response.status == 200
    assert (await response.content.read()) == file_data_ivr_framework
    assert 'chat_id.wav' in response.headers['Content-Disposition']
    assert response.headers['X-File-Name'] == 'chat_id.wav'


@pytest.mark.pgsql('supportai_calls', files=['outgoing_calls.sql'])
async def test_download_call_record_file_voximplant(
        web_app_client, mockserver, patch, response_mock,
):
    call_record_content = b'voximplant call record content'

    @patch('aiohttp.request')
    def _(**kwargs):
        url = kwargs.get('url')
        assert url == 'http://voximplant_record_storage/call_record.mp3'

        class RequestContextManager:
            class MockResponse:
                def __init__(self, body):
                    self.status = 200
                    self.body = body

                async def read(self):
                    return self.body

            async def __aenter__(self):
                return self.MockResponse(call_record_content)

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        return RequestContextManager()

    response_voximplant = await web_app_client.get(
        f'/v1/files/calls/2/record?user_id=34&project_slug=test_voximplant',
    )
    assert response_voximplant.status == 200
    assert (await response_voximplant.content.read()) == call_record_content
    assert 'chat_id.mp3' in response_voximplant.headers['Content-Disposition']
    assert response_voximplant.headers['X-File-Name'] == 'chat_id.mp3'


async def test_upload_different_xlsm(web_app_client):
    content_types = {
        'application/vnd.ms-excel.sheet.macroEnabled.12': True,
        'application/vnd.ms-excel.sheet.macroenabled.12': True,
        'appLication/Vnd.MS-excEl.shEEt.macroenabled.12': True,
        'application/vnd-ms-excel.sheet.macroenabled.13': False,
    }

    for content_type, is_allowed in content_types.items():
        form_data = aiohttp.FormData()
        form_data.add_field(
            name='file',
            value=b'',
            content_type=content_type,
            filename='some filename',
        )
        response = await web_app_client.post(
            '/v1/files?user_id=34&project_slug=test', data=form_data,
        )
        if is_allowed:
            assert response.status == 200
        else:
            assert response.status == 400


async def test_store_external_phone_ids(web_app_client, web_context):
    def convert_items_to_file_data(items):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('some_sheet')
        workbook.add_worksheet('another sheet')
        worksheet.write(0, 0, 'phone')
        worksheet.write(0, 1, 'external_phone_id')

        for idx, item in enumerate(items):
            worksheet.write(idx + 1, 0, item['phone'])
            worksheet.write(idx + 1, 1, item['external_phone_id'])
        workbook.close()
        output.seek(0)

        return output.read()

    items = [
        {'phone': '1', 'external_phone_id': 'id_1'},
        {'phone': '2', 'external_phone_id': 'id_2'},
    ]
    file_data = convert_items_to_file_data(items)
    project_slug = 'test_store_external_ids'

    form_data = aiohttp.FormData()
    form_data.add_field(
        name='file',
        value=file_data,
        content_type=constants.XLSX_CONTENT_TYPE,
        filename='some filename',
    )

    response = await web_app_client.post(
        f'/v1/files/external_phone_ids?project_slug={project_slug}&user_id=34',
        data=form_data,
    )
    assert response.status == 200

    external_id_to_phone = await external_phone_id_helpers.get_id_to_phone_map(
        web_context, {}, project_slug,
    )
    assert set(external_id_to_phone.items()) == {('id_1', '1'), ('id_2', '2')}

    new_items = [
        {'phone': 'new_1', 'external_phone_id': 'id_1'},
        {'phone': '3', 'external_phone_id': 'id_3'},
    ]
    file_data = convert_items_to_file_data(new_items)
    form_data = aiohttp.FormData()
    form_data.add_field(
        name='file',
        value=file_data,
        content_type=constants.XLSX_CONTENT_TYPE,
        filename='some new filename',
    )
    response = await web_app_client.post(
        f'/v1/files/external_phone_ids?project_slug={project_slug}&user_id=34',
        data=form_data,
    )
    assert response.status == 200

    external_id_to_phone = await external_phone_id_helpers.get_id_to_phone_map(
        web_context, {}, project_slug,
    )
    assert set(external_id_to_phone.items()) == {
        ('id_1', 'new_1'),
        ('id_2', '2'),
        ('id_3', '3'),
    }
