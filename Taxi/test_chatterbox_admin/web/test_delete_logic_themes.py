import http

import pytest

from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'logic_id,theme',
    (
        (const.LOGIC_UUID_1, 'awesome theme'),
        (const.LOGIC_UUID_2, 'awesome theme'),
    ),
)
async def test_delete_logic_themes(
        taxi_chatterbox_admin_web, pgsql, logic_id: str, theme: str,
):
    response = await taxi_chatterbox_admin_web.delete(
        f'/v1/logics/themes', params={'logic_id': logic_id, 'theme': theme},
    )
    assert response.status == http.HTTPStatus.OK
    cursor = pgsql['chatterbox_admin'].cursor()
    cursor.execute(
        """
        SELECT 1
        FROM chatterbox_admin.themes_logics
        WHERE logic_id = %s and theme = %s
    """,
        (logic_id, theme),
    )
    assert cursor.fetchone() is None


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'logic_id,theme,status_code',
    (
        (
            const.LOGIC_UUID_NOT_EXIST,
            'awesome theme',
            http.HTTPStatus.NOT_FOUND,
        ),
        (const.UUID_BAD_FMT, 'awesome theme', http.HTTPStatus.BAD_REQUEST),
    ),
)
async def test_delete_logic_themes_error(
        taxi_chatterbox_admin_web,
        pgsql,
        logic_id: str,
        theme: str,
        status_code: int,
):
    response = await taxi_chatterbox_admin_web.delete(
        f'/v1/logics/themes', params={'logic_id': logic_id, 'theme': theme},
    )
    assert response.status == status_code
