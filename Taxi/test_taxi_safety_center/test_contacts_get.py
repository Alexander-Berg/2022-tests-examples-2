import pytest

DEFAULT_HEADER = {
    'X-Yandex-UID': '9876',
    'Accept-Language': 'ru',
    'X-YaTaxi-UserId': '9876',
}
MAX_CONTACTS = 5


@pytest.mark.config(SAFETY_CENTER_MAX_CONTACTS=MAX_CONTACTS)
@pytest.mark.pgsql(
    'safety_center',
    queries=[
        (
            'INSERT INTO safety_center.contacts '
            '(yandex_uid, contacts, created_at, updated_at)'
            ' VALUES (' + DEFAULT_HEADER['X-Yandex-UID'] + '::text,'
            'array[(\'contact_name\',\'+7987654321_id\')]::contact[],'
            ' NOW(), NOW())'
        ),
    ],
)
@pytest.mark.parametrize(
    'contacts_row',
    [[{'phone_number': '+7987654321', 'name': 'contact_name'}]],
)
async def test_get_contacts_200(
        web_app_client,
        contacts_row,
        mock_personal_response,
        path='/4.0/safety_center/v1/contacts',
):
    mock_personal_response(contact['phone_number'] for contact in contacts_row)
    get_response = await web_app_client.get(
        path, data='{}', headers=DEFAULT_HEADER,
    )
    assert get_response.status == 200
    awaited_response = {'contacts': contacts_row, 'max_contacts': MAX_CONTACTS}
    assert await get_response.json() == awaited_response
