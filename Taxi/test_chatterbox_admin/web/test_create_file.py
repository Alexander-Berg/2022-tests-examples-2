import http

import aiohttp
import pytest

from taxi.clients import mds_s3

from chatterbox_admin.common import utils


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'content,file_name,error,generate_preview,status_code',
    (
        (b'abc', 'test_name.jpeg', False, False, http.HTTPStatus.OK),
        (b'abc', 'test_name.jpeg', True, False, http.HTTPStatus.BAD_REQUEST),
        (b'abc', 'test_name.jpeg', False, True, http.HTTPStatus.OK),
        (
            b'test-content',
            'test_name.jpeg',
            False,
            False,
            http.HTTPStatus.CONFLICT,
        ),
        (
            b'test-content',
            'test_name.jpeg',
            False,
            True,
            http.HTTPStatus.CONFLICT,
        ),
    ),
)
async def test_create_file(
        web_app_client,
        pgsql,
        patch,
        content,
        file_name,
        error,
        generate_preview,
        status_code,
):
    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_s3_mock(*args, **kwargs):
        if error:
            raise ValueError()
        return mds_s3.S3Object(Key='key', ETag=None)

    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def _put_task(queue, eta=None, task_id=None, args=None, kwargs=None):
        return {}

    @patch('chatterbox_admin.common.utils.check_content_is_image')
    def _check_preview(*args, **kwargs):
        return generate_preview

    form = aiohttp.FormData()
    form.add_field(name='content', value=content, filename=file_name)
    response = await web_app_client.post(
        '/v1/attachments/files', data=form, headers={'X-File-Name': file_name},
    )
    assert response.status == status_code
    if response.status == http.HTTPStatus.OK:
        content = await response.json()
        file_id = content.get('id')
        assert file_id
        cursor = pgsql['chatterbox_admin'].cursor()
        cursor.execute(
            """
            SELECT id, name, hash
            FROM chatterbox_admin.attachments_files
            WHERE id = %s
            """,
            (file_id,),
        )
        row = cursor.fetchone()
        assert row
        assert row[0] == file_id
        assert row[1] == file_name
        assert row[2]
        assert _mds_s3_mock
        if generate_preview:
            assert len(_put_task.calls) == 1
        else:
            assert not _put_task.calls
    else:
        assert not _put_task.calls
        if response.status != http.HTTPStatus.CONFLICT:
            cursor = pgsql['chatterbox_admin'].cursor()
            file_hash = utils.calculate_file_hash(content)
            cursor.execute(
                """
                SELECT id
                FROM chatterbox_admin.attachments_files
                WHERE hash = %s
                """,
                (file_hash,),
            )
            row = cursor.fetchone()
            assert not row
