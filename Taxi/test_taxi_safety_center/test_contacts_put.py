import json

import pytest

from taxi_safety_center import exceptions
from taxi_safety_center.logic import contacts as contact_handler
from test_taxi_safety_center import data_generators

CLIENT_MESSAGES = {
    'exceptions.safety_center.authorization_error': {
        'ru': 'Ошибка авторизации',
        'en': 'authorization_error',
    },
    'exceptions.safety_center.invalid_phone_number': {
        'ru': 'Неверный формат номера',
        'en': 'invalid_phone_number',
    },
    'exceptions.safety_center.invalid_contact_name': {
        'ru': 'Слишком длинное имя контакта',
        'en': 'invalid_contact_name',
    },
    'exceptions.safety_center.phone_number_duplicate': {
        'ru': 'Ошибка: дублирующиеся номера контактов',
        'en': 'phone_number_duplicate',
    },
    'exceptions.safety_center.unknown_server_error': {
        'ru': 'Внутренняя ошибка сервера',
        'en': 'unknown_server_error',
    },
    'exceptions.safety_center.contacts_limit_error': {
        'ru': 'Слишком много контактов',
        'en': 'Too many contacts',
    },
}

DEFAULT_HEADER = {
    'X-Yandex-UID': '9876',
    'Accept-Language': 'ru',
    'X-YaTaxi-UserId': '9876',
}

MAX_CONTACTS = 5


@pytest.mark.config(
    SAFETY_CENTER_MAX_CONTACTS=MAX_CONTACTS,
    SAFETY_CENTER_MAX_CONTACT_NAME_LENGTH=50,
)
@pytest.mark.pgsql('safety_center')
@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.parametrize(
    ','.join(
        [
            'request_headers',
            'request_body',
            'response_status',
            'response_body',
        ],
    ),
    [
        (
            DEFAULT_HEADER,
            {
                'contacts': [
                    data_generators.significant_contact(i)
                    for i in range(MAX_CONTACTS + 1)
                ],
            },
            exceptions.ContactsLimitError.status_code,
            {
                'code': exceptions.ContactsLimitError.error_code,
                'message': CLIENT_MESSAGES[
                    'exceptions.safety_center.contacts_limit_error'
                ]['ru'],
                'details': {'max_contacts': MAX_CONTACTS},
            },
            # TODO formatted (and pluralized!) translated exceptions
        ),
        (
            DEFAULT_HEADER,
            {
                'contacts': [
                    data_generators.significant_contact(1),
                    data_generators.significant_contact(1),
                ],
            },
            exceptions.PhoneNumberDuplicateError.status_code,
            {
                'code': exceptions.PhoneNumberDuplicateError.error_code,
                'message': CLIENT_MESSAGES[
                    'exceptions.safety_center.phone_number_duplicate'
                ]['ru'],
            },
        ),
        (
            DEFAULT_HEADER,
            {
                'contacts': [
                    {
                        'phone_number': '8' * (
                            contact_handler.MAX_PHONE_NUMBER_LEN + 1
                        ),
                        'name': 'Significant contact',
                    },
                ],
            },
            exceptions.InvalidPhoneNumberError.status_code,
            {
                'code': exceptions.InvalidPhoneNumberError.error_code,
                'message': CLIENT_MESSAGES[
                    'exceptions.safety_center.invalid_phone_number'
                ]['ru'],
            },
        ),
        (
            DEFAULT_HEADER,
            {
                'contacts': [
                    {
                        'phone_number': 'a' * (
                            contact_handler.MAX_RAW_PHONE_NUMBER_LEN + 1
                        ),
                        'name': 'Significant contact',
                    },
                ],
            },
            exceptions.InvalidPhoneNumberError.status_code,
            {
                'code': exceptions.InvalidPhoneNumberError.error_code,
                'message': CLIENT_MESSAGES[
                    'exceptions.safety_center.invalid_phone_number'
                ]['ru'],
            },
        ),
        (
            DEFAULT_HEADER,
            {
                'contacts': [
                    {
                        'phone_number': '+798765643210',
                        'name': 'a' * (
                            contact_handler.MAX_CONTACT_NAME_LEN + 1
                        ),
                    },
                ],
            },
            exceptions.InvalidContactNameError.status_code,
            {
                'code': exceptions.InvalidContactNameError.error_code,
                'message': CLIENT_MESSAGES[
                    'exceptions.safety_center.invalid_contact_name'
                ]['ru'],
            },
        ),
    ],
)
async def test_put_contacts_errors(
        web_app_client,
        request_headers,
        request_body,
        response_status,
        response_body,
        mock_personal_response,
        path='/4.0/safety_center/v1/contacts',
):
    mock_personal_response(
        contact['phone_number'] for contact in request_body['contacts']
    )
    response = await web_app_client.put(
        path, data=json.dumps(request_body), headers=request_headers,
    )
    assert response.status == response_status
    assert response_body == await response.json()


@pytest.mark.config(
    SAFETY_CENTER_MAX_CONTACTS=5, SAFETY_CENTER_MAX_CONTACT_NAME_LENGTH=50,
)
@pytest.mark.pgsql('safety_center')
@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
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
async def test_put_contacts_200(
        pgsql,
        web_app_client,
        contacts_rows,
        mock_personal_response,
        path='/4.0/safety_center/v1/contacts',
):
    for contacts_row in contacts_rows:
        mock_personal_response(
            contact['phone_number'] for contact in contacts_row
        )
        request_body = {'contacts': contacts_row}
        put_response = await web_app_client.put(
            path, data=json.dumps(request_body), headers=DEFAULT_HEADER,
        )
        assert put_response.status == 200
        assert await put_response.json() == {}
        cursor = pgsql['safety_center'].cursor()
        cursor.execute(
            'SELECT (unnest(contacts.contacts)).* from safety_center.contacts'
            ' WHERE yandex_uid = {}::text'.format(
                DEFAULT_HEADER['X-Yandex-UID'],
            ),
        )
        result = [row for row in cursor]
        assert len(result) == len(contacts_row)
        for i, contact in enumerate(contacts_row):
            assert result[i] == (
                contact['name'],
                contact['phone_number'] + '_id',
            )
