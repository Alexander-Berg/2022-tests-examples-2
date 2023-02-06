import http

import pytest

from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'logic_id,name,url',
    (
        (const.LOGIC_UUID_1, 'random name', 'random url'),
        (const.LOGIC_UUID_2, 'new name', 'new url'),
    ),
)
async def test_edit_logic(
        taxi_chatterbox_admin_web, pgsql, logic_id: str, name: str, url: str,
):
    request_body = {'name': name, 'url': url}
    response = await taxi_chatterbox_admin_web.put(
        '/v1/logics', params={'logic_id': logic_id}, json=request_body,
    )
    assert response.status == http.HTTPStatus.OK
    cursor = pgsql['chatterbox_admin'].cursor()
    cursor.execute(
        """
        SELECT
            id,
            name,
            url
        FROM chatterbox_admin.logics
        WHERE id=%s
    """,
        (logic_id,),
    )
    result = cursor.fetchone()
    assert result == (
        logic_id,
        request_body.get('name', result[1]),
        request_body.get('url', result[2]),
    )


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'logic_id,name,url,status_code',
    (
        (const.LOGIC_UUID_1, 'random name', None, http.HTTPStatus.BAD_REQUEST),
        (const.LOGIC_UUID_1, None, 'random url', http.HTTPStatus.BAD_REQUEST),
        (const.LOGIC_UUID_1, None, None, http.HTTPStatus.BAD_REQUEST),
        (
            const.LOGIC_UUID_2,
            'random name',
            'awesome url',
            http.HTTPStatus.CONFLICT,
        ),
        (
            const.LOGIC_UUID_2,
            'awesome name',
            'random url',
            http.HTTPStatus.CONFLICT,
        ),
        (const.LOGIC_UUID_NOT_EXIST, '', '', http.HTTPStatus.NOT_FOUND),
        (const.UUID_BAD_FMT, '', '', http.HTTPStatus.BAD_REQUEST),
    ),
)
async def test_edit_logic_error(
        taxi_chatterbox_admin_web,
        pgsql,
        logic_id: str,
        name: str,
        url: str,
        status_code: int,
):
    request_body = {'name': name, 'url': url}
    response = await taxi_chatterbox_admin_web.put(
        '/v1/logics', params={'logic_id': logic_id}, json=request_body,
    )
    assert response.status == status_code
