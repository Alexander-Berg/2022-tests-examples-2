import http

import pytest

from test_eats_integration_offline_orders import conftest


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code'),
    (
        pytest.param(
            {'place_id': 'place_id__1'},
            {'telegram_login_id': 'personal_telegram_login_id'},
            http.HTTPStatus.OK,
            id='OK',
        ),
        pytest.param(
            {'place_id': 'not-existing-place-id'},
            {'telegram_login_id': 'personal_telegram_login_id'},
            http.HTTPStatus.NOT_FOUND,
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'telegram_managers.sql'],
)
async def test_admin_notifications_tg_manager_add(
        web_app_client,
        mock_generate_uuid,
        params,
        request_body,
        expected_code,
):
    response = await web_app_client.post(
        '/admin/v1/notifications/tg/managers',
        json=request_body,
        params=params,
    )
    assert response.status == expected_code
    if response.status != http.HTTPStatus.OK:
        return
    body = await response.json()
    expected = request_body.copy()
    expected.update(
        {'uuid': conftest.MOCK_UUID, 'place_id': params['place_id']},
    )
    assert body == expected
