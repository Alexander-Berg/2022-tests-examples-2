import http

import pytest


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'status_code,expected_result', ((http.HTTPStatus.OK, ['taxi', 'eda']),),
)
async def test_get_categories(
        taxi_chatterbox_admin_web, status_code, expected_result,
):
    response = await taxi_chatterbox_admin_web.get(
        '/v1/attachments/collections/categories/get_all',
    )
    assert response.status == status_code
    if status_code == http.HTTPStatus.OK:
        content = await response.json()
        content = set(content)
        expected_result = set(expected_result)
        assert content == expected_result
