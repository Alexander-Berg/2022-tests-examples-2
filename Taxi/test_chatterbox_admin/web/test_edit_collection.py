import copy
import http

import pytest

from test_chatterbox_admin import constants as const


REQUEST_BODY = {
    'name': 'new name',
    'description': 'description',
    'active': False,
}

RESPONSE_BODY = ('new name', 'description', False)


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'collection_id,request_json,status_code',
    (
        # check ok case
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
        # check wrong parameters
        (const.COLLECTION_UUID_NOT_EXIST, {}, http.HTTPStatus.NOT_FOUND),
        (const.UUID_BAD_FMT, {}, http.HTTPStatus.BAD_REQUEST),
    ),
)
async def test_edit_collection(
        taxi_chatterbox_admin_web,
        pgsql,
        collection_id,
        request_json,
        status_code,
):
    request_body = copy.deepcopy(REQUEST_BODY)
    request_body.update(**{'categories': request_json})
    response = await taxi_chatterbox_admin_web.put(
        '/v1/attachments/collections',
        params={'collection_id': collection_id},
        json=request_body,
    )
    assert response.status == status_code
    if status_code == 200:
        cursor = pgsql['chatterbox_admin'].cursor()
        cursor.execute(
            """
            SELECT id, name, description, active
            FROM chatterbox_admin.attachments_collections
            WHERE id = %s
            """,
            (collection_id,),
        )
        assert cursor.fetchone() == (collection_id, *RESPONSE_BODY)
