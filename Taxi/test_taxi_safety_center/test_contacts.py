import json

import pytest

from test_taxi_safety_center import data_generators

DEFAULT_HEADER = {
    'X-Yandex-UID': '9876',
    'Accept-Language': 'ru',
    'X-YaTaxi-UserId': '9876',
}
MAX_CONTACTS = 5


@pytest.mark.config(
    SAFETY_CENTER_MAX_CONTACTS=MAX_CONTACTS,
    SAFETY_CENTER_MAX_CONTACT_NAME_LENGTH=50,
    TVM_RULES=[{'src': 'safety-center', 'dst': 'personal'}],
)
@pytest.mark.pgsql('safety_center')
@pytest.mark.parametrize(
    'contacts_rows',
    [
        [[], [data_generators.significant_contact(1)], []],
        [
            [data_generators.significant_contact(1)],
            [data_generators.significant_contact(2)],
        ],
        [
            [
                data_generators.significant_contact(1),
                data_generators.significant_contact(2),
                data_generators.significant_contact(3),
            ],
            [],
        ],
        [[{'phone_number': '+79876543210', 'name': ''}]],
    ],
)
async def test_put_and_get_contacts_200(
        web_app,
        web_app_client,
        contacts_rows,
        mock_personal_response,
        web_context,
        path='/4.0/safety_center/v1/contacts',
):
    for contacts_row in contacts_rows:
        mock_personal_response(
            [contact['phone_number'] for contact in contacts_row],
        )

        request_body = {'contacts': contacts_row}
        put_response = await web_app_client.put(
            path, data=json.dumps(request_body), headers=DEFAULT_HEADER,
        )
        assert put_response.status == 200
        assert await put_response.json() == {}

        get_response = await web_app_client.get(
            path, data='{}', headers=DEFAULT_HEADER,
        )
        assert get_response.status == 200
        awaited_response = {
            'contacts': contacts_row,
            'max_contacts': MAX_CONTACTS,
        }
        assert await get_response.json() == awaited_response
