import http

import pytest


DEFAULT_PARAMS = {'contact_uuid': 'contact_uuid_1'}
BASE_FIELDS = {'fullname_id': 'personal_fullname_id_1', 'title': 'ЛПР'}


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code'),
    (
        pytest.param(
            DEFAULT_PARAMS,
            {
                'phone_id': 'new_personal_phone_id',
                'email_id': 'new_personal_email_id',
                'fullname_id': 'new_personal_fullname_id',
                'telegram_login_id': 'new_personal_telegram_login_id',
                'title': 'Бухгалтер',
                'comment': 'коммент',
            },
            http.HTTPStatus.OK,
            id='OK',
        ),
        pytest.param(
            DEFAULT_PARAMS, BASE_FIELDS, http.HTTPStatus.OK, id='set-null',
        ),
        pytest.param(
            {'contact_uuid': 'contact_uuid_2'},
            BASE_FIELDS,
            http.HTTPStatus.NOT_FOUND,
            id='deleted-contact',
        ),
        pytest.param(
            {'contact_uuid': 'not-existing-uuid'},
            BASE_FIELDS,
            http.HTTPStatus.NOT_FOUND,
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'restaurants_contacts.sql'],
)
async def test_admin_place_contacts_edit(
        web_app_client, params, request_body, expected_code,
):
    response = await web_app_client.put(
        '/admin/v1/contacts', json=request_body, params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    if response.status != http.HTTPStatus.OK:
        return
    _base_contact = {'uuid': params['contact_uuid'], 'place_id': 'place_id__1'}
    expected = request_body.copy()
    expected.update(**_base_contact)
    assert body == expected
