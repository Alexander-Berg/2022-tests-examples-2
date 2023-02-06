import http

import pytest

from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'file_id,collection_id,categories,status_code',
    (
        # ok case
        (
            const.FILE_UUID_6,
            const.COLLECTION_UUID_3,
            const.CATEGORIES_OK_1,
            http.HTTPStatus.OK,
        ),
        # file already deleted
        (
            const.FILE_UUID_2,
            const.COLLECTION_UUID_2,
            const.CATEGORIES_OK_1,
            http.HTTPStatus.NOT_FOUND,
        ),
        # check categories
        (
            const.FILE_UUID_6,
            const.COLLECTION_UUID_3,
            const.CATEGORIES_OK_3,
            http.HTTPStatus.OK,
        ),
        (
            const.FILE_UUID_6,
            const.COLLECTION_UUID_3,
            const.CATEGORIES_OK_2,
            http.HTTPStatus.OK,
        ),
        (
            const.FILE_UUID_6,
            const.COLLECTION_UUID_3,
            const.CATEGORIES_OK_3,
            http.HTTPStatus.OK,
        ),
        (
            const.FILE_UUID_6,
            const.COLLECTION_UUID_3,
            const.CATEGORIES_FAIL_1,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_6,
            const.COLLECTION_UUID_3,
            const.CATEGORIES_FAIL_2,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_6,
            const.COLLECTION_UUID_3,
            const.CATEGORIES_FAIL_3,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_6,
            const.COLLECTION_UUID_3,
            const.CATEGORIES_FAIL_4,
            http.HTTPStatus.BAD_REQUEST,
        ),
        # check file not belong to any collection
        #
        (const.FILE_UUID_4, '', {}, http.HTTPStatus.OK),
        (const.FILE_UUID_1, '', {}, http.HTTPStatus.BAD_REQUEST),
        #
        (
            const.FILE_UUID_4,
            const.COLLECTION_UUID_2,
            const.CATEGORIES_OK_1,
            http.HTTPStatus.BAD_REQUEST,
        ),
        # check bad format
        (const.FILE_UUID_NOT_EXIST, '', {}, http.HTTPStatus.NOT_FOUND),
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
async def test_delete_file(
        taxi_chatterbox_admin_web,
        pgsql,
        file_id,
        collection_id,
        categories,
        status_code,
):
    response = await taxi_chatterbox_admin_web.delete(
        '/v1/attachments/files',
        params={'file_id': file_id, 'collection_id': collection_id},
        json={'categories': categories},
    )
    assert response.status == status_code
    if status_code == http.HTTPStatus.OK:
        cursor = pgsql['chatterbox_admin'].cursor()
        cursor.execute(
            """
            SELECT id, deleted
            FROM chatterbox_admin.attachments_files
            WHERE id = %s
            """,
            (file_id,),
        )
        row = cursor.fetchone()
        assert row
        assert row[0] == file_id
        assert row[1]
