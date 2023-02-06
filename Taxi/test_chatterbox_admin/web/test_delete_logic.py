import http

import pytest

from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize('logic_id', (const.LOGIC_UUID_1, const.LOGIC_UUID_2))
async def test_delete_logic(taxi_chatterbox_admin_web, pgsql, logic_id: str):
    response = await taxi_chatterbox_admin_web.delete(
        '/v1/logics', params={'logic_id': logic_id},
    )
    assert response.status == http.HTTPStatus.OK
    cursor = pgsql['chatterbox_admin'].cursor()
    cursor.execute(
        """
        SELECT id
        FROM chatterbox_admin.logics
        WHERE id = %s
    """,
        (logic_id,),
    )
    assert cursor.fetchone() is None
    cursor.execute(
        """
        SELECT 1
        FROM chatterbox_admin.themes_logics
        WHERE logic_id = %s
    """,
        (logic_id,),
    )
    assert cursor.fetchone() is None


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'logic_id,status_code',
    (
        (const.LOGIC_UUID_NOT_EXIST, http.HTTPStatus.NOT_FOUND),
        (const.UUID_BAD_FMT, http.HTTPStatus.BAD_REQUEST),
    ),
)
async def test_delete_logic_error(
        taxi_chatterbox_admin_web, pgsql, logic_id: str, status_code: int,
):
    response = await taxi_chatterbox_admin_web.delete(
        '/v1/logics', params={'logic_id': logic_id},
    )
    assert response.status == status_code
