import http

import pytest

from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'file_id,tags,collection_id,categories,status_code',
    (
        # ok case
        (
            const.FILE_UUID_1,
            ['new_tag'],
            const.COLLECTION_UUID_1,
            {},
            http.HTTPStatus.OK,
        ),
        (
            const.FILE_UUID_1,
            ['new_tag', 'new_tag_2'],
            const.COLLECTION_UUID_1,
            {},
            http.HTTPStatus.OK,
        ),
        # tag already exists
        (
            const.FILE_UUID_1,
            ['happy'],
            const.COLLECTION_UUID_1,
            {},
            http.HTTPStatus.OK,
        ),
        (
            const.FILE_UUID_1,
            ['happy', 'new_tag'],
            const.COLLECTION_UUID_1,
            {},
            http.HTTPStatus.OK,
        ),
        # check categories
        (
            const.FILE_UUID_1,
            ['new_tag'],
            const.COLLECTION_UUID_2,
            const.CATEGORIES_OK_1,
            http.HTTPStatus.OK,
        ),
        (
            const.FILE_UUID_1,
            ['new_tag'],
            const.COLLECTION_UUID_2,
            const.CATEGORIES_OK_2,
            http.HTTPStatus.OK,
        ),
        (
            const.FILE_UUID_1,
            ['new_tag'],
            const.COLLECTION_UUID_2,
            const.CATEGORIES_OK_3,
            http.HTTPStatus.OK,
        ),
        (
            const.FILE_UUID_1,
            ['new_tag'],
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_1,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_1,
            ['new_tag'],
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_2,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_1,
            ['new_tag'],
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_3,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_1,
            ['new_tag'],
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_4,
            http.HTTPStatus.BAD_REQUEST,
        ),
        # check file not belong to any collection
        (const.FILE_UUID_4, ['new_tag'], '', {}, http.HTTPStatus.OK),
        (
            const.FILE_UUID_4,
            ['new_tag'],
            const.COLLECTION_UUID_1,
            {},
            http.HTTPStatus.BAD_REQUEST,
        ),
        # check bad format
        (
            const.UUID_BAD_FMT,
            ['happy'],
            const.COLLECTION_UUID_1,
            {},
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_1,
            ['happy'],
            const.UUID_BAD_FMT,
            {},
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.FILE_UUID_NOT_EXIST,
            ['happy'],
            const.COLLECTION_UUID_1,
            {},
            http.HTTPStatus.NOT_FOUND,
        ),
    ),
)
async def test_file_add_tag(
        taxi_chatterbox_admin_web,
        pgsql,
        file_id,
        tags,
        collection_id,
        categories,
        status_code,
):
    response = await taxi_chatterbox_admin_web.post(
        '/v1/attachments/files/tags',
        params={'file_id': file_id, 'collection_id': collection_id},
        json={'categories': categories, 'tags': tags},
    )
    assert response.status == status_code
    if status_code == 200:
        cursor = pgsql['chatterbox_admin'].cursor()
        cursor.execute(
            """
            SELECT array_agg(tag_name)
            FROM chatterbox_admin.attachments_file_tags
            WHERE file_id = %s
            """,
            (file_id,),
        )
        row = cursor.fetchone()
        assert row
        for tag in tags:
            assert tag in row[0]
            assert row[0].count(tag) == 1
