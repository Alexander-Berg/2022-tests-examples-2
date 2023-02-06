import http

import pytest

from test_eats_integration_offline_orders import conftest


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code'),
    (
        pytest.param(
            {'place_id': 'place_id__1'},
            {'title': 'ЛПР', 'fullname_id': 'personal_fullname_id'},
            http.HTTPStatus.OK,
            id='OK',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {
                'title': 'ЛПР',
                'fullname_id': 'personal_fullname_id',
                'phone_id': 'personal_phone_id',
                'email_id': 'personal_email_id',
                'telegram_login_id': 'personal_telegram_login_id',
                'comment': 'звонить после 12',
            },
            http.HTTPStatus.OK,
            id='OK-all-fields',
        ),
        pytest.param(
            {'place_id': 'not-existing-place-id'},
            {'title': 'ЛПР', 'fullname_id': 'personal_fullname_id'},
            http.HTTPStatus.NOT_FOUND,
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'restaurants_contacts.sql'],
)
async def test_admin_place_contacts_create(
        web_app_client,
        mock_generate_uuid,
        patch,
        params,
        request_body,
        expected_code,
):
    response = await web_app_client.post(
        '/admin/v1/contacts', json=request_body, params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    if response.status != http.HTTPStatus.OK:
        return
    expected = request_body.copy()
    expected.update(
        {'uuid': conftest.MOCK_UUID, 'place_id': params['place_id']},
    )
    assert body == expected
