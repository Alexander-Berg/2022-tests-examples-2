import http

import pytest

from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'collection_id,categories,status_code',
    (
        (const.COLLECTION_UUID_1, ['lavka'], http.HTTPStatus.OK),
        (const.COLLECTION_UUID_1, ['lavka', 'lavka'], http.HTTPStatus.OK),
        (const.COLLECTION_UUID_2, ['taxi', 'eda'], http.HTTPStatus.OK),
        (const.COLLECTION_UUID_2, ['taxi', 'eda', 'taxi'], http.HTTPStatus.OK),
        (
            const.COLLECTION_UUID_NOT_EXIST,
            ['lavka'],
            http.HTTPStatus.NOT_FOUND,
        ),
        (const.UUID_BAD_FMT, ['lavka'], http.HTTPStatus.BAD_REQUEST),
    ),
)
async def test_collection_add_category(
        taxi_chatterbox_admin_web,
        pgsql,
        collection_id,
        categories,
        status_code,
):
    response = await taxi_chatterbox_admin_web.post(
        '/v1/attachments/collections/categories',
        params={'collection_id': collection_id},
        json={'categories': categories},
    )
    assert response.status == status_code
    if status_code == http.HTTPStatus.OK:
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
        assert sorted(set(categories)) == sorted(set(row[1]))
