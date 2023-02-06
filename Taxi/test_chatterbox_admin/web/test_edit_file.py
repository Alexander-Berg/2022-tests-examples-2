import copy
import http

import pytest

from test_chatterbox_admin import constants as const


REQUEST_BODY = {'name': 'new_name.jpeg', 'description': 'awesome file!'}


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'file_id,collection_id,categories,status_code',
    (
        # ok case
        (const.FILE_UUID_1, const.COLLECTION_UUID_1, {}, http.HTTPStatus.OK),
        # check categories
        (
            const.FILE_UUID_1,
            const.COLLECTION_UUID_2,
            const.CATEGORIES_OK_1,
            http.HTTPStatus.OK,
        ),
        (
            const.FILE_UUID_1,
            const.COLLECTION_UUID_2,
            const.CATEGORIES_OK_2,
            http.HTTPStatus.OK,
        ),
        (
            const.FILE_UUID_1,
            const.COLLECTION_UUID_2,
            const.CATEGORIES_OK_3,
            http.HTTPStatus.OK,
        ),
        (
            const.FILE_UUID_1,
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_1,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_1,
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_2,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_1,
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_3,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_1,
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_4,
            http.HTTPStatus.BAD_REQUEST,
        ),
        # check file not belong to any collection
        (const.FILE_UUID_4, '', {}, http.HTTPStatus.OK),
        (
            const.FILE_UUID_4,
            const.COLLECTION_UUID_1,
            {},
            http.HTTPStatus.BAD_REQUEST,
        ),
        # check not found
        (
            const.FILE_UUID_NOT_EXIST,
            const.COLLECTION_UUID_1,
            {},
            http.HTTPStatus.NOT_FOUND,
        ),
        # check bad fmt
        (
            const.UUID_BAD_FMT,
            const.COLLECTION_UUID_1,
            {},
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_1,
            const.UUID_BAD_FMT,
            {},
            http.HTTPStatus.BAD_REQUEST,
        ),
    ),
)
async def test_edit_file(
        taxi_chatterbox_admin_web,
        pgsql,
        file_id,
        collection_id,
        categories,
        status_code,
):
    request_body = copy.deepcopy(REQUEST_BODY)
    request_body['categories'] = categories
    response = await taxi_chatterbox_admin_web.patch(
        '/v1/attachments/files',
        params={'file_id': file_id, 'collection_id': collection_id},
        json=request_body,
    )
    assert response.status == status_code
    if status_code == http.HTTPStatus.OK:
        cursor = pgsql['chatterbox_admin'].cursor()
        cursor.execute(
            """
            SELECT id, name, description
            FROM chatterbox_admin.attachments_files
            WHERE id = %s
            """,
            (file_id,),
        )
        row = cursor.fetchone()
        assert row
        assert row[0] == file_id
        assert row[1] == REQUEST_BODY['name']
        assert row[2] == REQUEST_BODY['description']
