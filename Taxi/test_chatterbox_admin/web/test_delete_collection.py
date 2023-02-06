import http

import pytest

from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'collection_id,categories,status_code',
    (
        # ok case
        (const.COLLECTION_UUID_1, {}, http.HTTPStatus.OK),
        # check categories
        (const.COLLECTION_UUID_2, const.CATEGORIES_OK_1, http.HTTPStatus.OK),
        (const.COLLECTION_UUID_2, const.CATEGORIES_OK_2, http.HTTPStatus.OK),
        (const.COLLECTION_UUID_2, const.CATEGORIES_OK_3, http.HTTPStatus.OK),
        (
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_1,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_2,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_3,
            http.HTTPStatus.BAD_REQUEST,
        ),
        (
            const.COLLECTION_UUID_2,
            const.CATEGORIES_FAIL_4,
            http.HTTPStatus.BAD_REQUEST,
        ),
        # check wrong request
        (const.COLLECTION_UUID_NOT_EXIST, {}, http.HTTPStatus.NOT_FOUND),
        (const.UUID_BAD_FMT, {}, http.HTTPStatus.BAD_REQUEST),
    ),
)
async def test_delete_collection(
        taxi_chatterbox_admin_web,
        pgsql,
        collection_id,
        categories,
        status_code,
):
    response = await taxi_chatterbox_admin_web.delete(
        '/v1/attachments/collections',
        params={'collection_id': collection_id},
        json={'categories': categories},
    )
    assert response.status == status_code
    if status_code == http.HTTPStatus.OK:
        cursor = pgsql['chatterbox_admin'].cursor()
        cursor.execute(
            """
            SELECT id
            FROM chatterbox_admin.attachments_collections
            WHERE id = %s
            """,
            (collection_id,),
        )
        assert cursor.fetchone() is None
