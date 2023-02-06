import http

import pytest

from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'logic_id,themes',
    (
        (const.LOGIC_UUID_1, ['random theme']),
        (const.LOGIC_UUID_2, ['random theme', 'awesome theme']),
        (const.LOGIC_UUID_1, ['awesome theme']),
    ),
)
async def test_create_logic_themes(
        taxi_chatterbox_admin_web, pgsql, logic_id: str, themes: str,
):
    response = await taxi_chatterbox_admin_web.post(
        f'/v1/logics/themes',
        params={'logic_id': logic_id},
        json={'themes': themes},
    )
    assert response.status == http.HTTPStatus.OK
    cursor = pgsql['chatterbox_admin'].cursor()
    themes_sql = ', '.join([f'\'{theme}\'' for theme in themes])
    cursor.execute(
        f"""
        SELECT logic_id, theme
        FROM chatterbox_admin.themes_logics
        WHERE logic_id = %s and theme in ({themes_sql})
    """,
        (logic_id,),
    )
    results = cursor.fetchall()
    assert len(results) == len(themes)


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'logic_id,themes,status_code',
    (
        (const.LOGIC_UUID_NOT_EXIST, ['theme'], http.HTTPStatus.NOT_FOUND),
        (const.UUID_BAD_FMT, ['theme'], http.HTTPStatus.BAD_REQUEST),
    ),
)
async def test_create_logic_themes_error(
        taxi_chatterbox_admin_web,
        pgsql,
        logic_id: str,
        themes: str,
        status_code: int,
):
    response = await taxi_chatterbox_admin_web.post(
        f'/v1/logics/themes',
        params={'logic_id': logic_id},
        json={'themes': themes},
    )
    assert response.status == status_code
