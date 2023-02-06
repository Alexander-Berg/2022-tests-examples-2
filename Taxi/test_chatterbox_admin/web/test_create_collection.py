import copy
import http

import pytest


REQUEST_BODY = {'active': True, 'description': 'description'}


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'collection_name,category,status_code',
    (
        ('collection name', 'taxi', http.HTTPStatus.OK),
        ('collection name', '', http.HTTPStatus.OK),
        ('awesome collection', '', http.HTTPStatus.CONFLICT),
    ),
)
async def test_create_collection(
        taxi_chatterbox_admin_web,
        pgsql,
        collection_name,
        category,
        status_code,
):
    request_body = copy.deepcopy(REQUEST_BODY)
    request_body.update(name=collection_name, category=category)
    response = await taxi_chatterbox_admin_web.post(
        '/v1/attachments/collections', json=request_body,
    )
    assert response.status == status_code
    if status_code == http.HTTPStatus.OK:
        content = await response.json()
        collection_id = content.get('id')
        assert collection_id
        cursor = pgsql['chatterbox_admin'].cursor()
        cursor.execute(
            """
            SELECT id, categories
            FROM chatterbox_admin.attachments_collections
            WHERE id = %s
            """,
            (collection_id,),
        )
        row = cursor.fetchone()
        assert row
        assert row[0] == collection_id
        if category:
            assert row[1] == [category]
        else:
            assert not row[1]
