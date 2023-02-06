import http

import pytest


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize('name,url', (('logic name', 'logic url'),))
async def test_create_logic(
        taxi_chatterbox_admin_web, pgsql, name: str, url: str,
):
    request_body = {'name': name, 'url': url}
    response = await taxi_chatterbox_admin_web.post(
        '/v1/logics', json=request_body,
    )
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    logic_id = content.get('id')
    assert logic_id
    cursor = pgsql['chatterbox_admin'].cursor()
    cursor.execute(
        """
        SELECT id, name, url
        FROM chatterbox_admin.logics
        WHERE id = %s
    """,
        (logic_id,),
    )
    row = cursor.fetchone()
    assert row
    assert (row[0], row[1], row[2]) == (logic_id, name, url)


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'name,url,status_code',
    (
        ('awesome name', 'logic url', http.HTTPStatus.CONFLICT),
        ('logic name', 'awesome url', http.HTTPStatus.CONFLICT),
    ),
)
async def test_create_logic_error(
        taxi_chatterbox_admin_web,
        pgsql,
        name: str,
        url: str,
        status_code: int,
):
    request_body = {'name': name, 'url': url}
    response = await taxi_chatterbox_admin_web.post(
        '/v1/logics', json=request_body,
    )
    assert response.status == status_code
