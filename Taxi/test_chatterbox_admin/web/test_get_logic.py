import http

import pytest

from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'logic_id,expected_result',
    (
        (
            const.LOGIC_UUID_1,
            {
                'id': const.LOGIC_UUID_1,
                'name': 'awesome name',
                'url': 'awesome url',
            },
        ),
        (
            const.LOGIC_UUID_2,
            {
                'id': const.LOGIC_UUID_2,
                'name': 'not my name',
                'url': 'not my url',
            },
        ),
    ),
)
async def test_get_logic(
        taxi_chatterbox_admin_web, logic_id: str, expected_result: dict,
):
    response = await taxi_chatterbox_admin_web.get(
        '/v1/logics', params={'logic_id': logic_id},
    )
    assert response.status == http.HTTPStatus.OK
    content = await response.json()
    assert content == expected_result


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'logic_id,status_code',
    (
        (const.LOGIC_UUID_NOT_EXIST, http.HTTPStatus.NOT_FOUND),
        (const.UUID_BAD_FMT, http.HTTPStatus.BAD_REQUEST),
    ),
)
async def test_get_logic_error(
        taxi_chatterbox_admin_web, logic_id: str, status_code: int,
):
    response = await taxi_chatterbox_admin_web.get(
        '/v1/logics', params={'logic_id': logic_id},
    )
    assert response.status == status_code
