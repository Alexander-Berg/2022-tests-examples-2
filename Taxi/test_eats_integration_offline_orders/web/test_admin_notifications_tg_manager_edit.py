import http

import pytest


DEFAULT_PARAMS = {'manager_uuid': 'manager_uuid_1'}
BASE_FIELDS = {'telegram_login_id': 'new_personal_telegram_login_id'}


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code'),
    (
        pytest.param(
            {'manager_uuid': 'manager_uuid_1'},
            BASE_FIELDS,
            http.HTTPStatus.OK,
            id='OK',
        ),
        pytest.param(
            {'manager_uuid': 'manager_uuid_2'},
            BASE_FIELDS,
            http.HTTPStatus.NOT_FOUND,
            id='deleted-manager',
        ),
        pytest.param(
            {'manager_uuid': 'not-existing-uuid'},
            BASE_FIELDS,
            http.HTTPStatus.NOT_FOUND,
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'telegram_managers.sql'],
)
async def test_admin_notifications_tg_manager_edit(
        web_app_client, params, request_body, expected_code,
):
    response = await web_app_client.put(
        '/admin/v1/notifications/tg/managers',
        json=request_body,
        params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    if response.status != http.HTTPStatus.OK:
        return
    _base_contact = {'uuid': params['manager_uuid'], 'place_id': 'place_id__1'}
    expected = request_body.copy()
    expected.update(**_base_contact)
    assert body == expected
