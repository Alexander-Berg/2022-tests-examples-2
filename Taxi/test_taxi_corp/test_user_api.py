import uuid

import bson
import pytest

CORP_USER_PHONES_SUPPORTED_79 = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+79'],
        'matches': ['^79'],
    },
]


@pytest.mark.parametrize(
    'corp_user_auth_client_data',
    [
        {
            'fullname': 'Boe',
            'phone': '+79291112206',
            'role': {'role_id': 'role1'},
            'email': 'boe@mail.com',
            'is_active': True,
            'department_id': 'd1',
        },
    ],
)
@pytest.mark.translations(
    corp={
        'role.others_name': {'ru': 'role.others_name'},
        'sms.create_user': {'ru': 'Привет!'},
    },
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_79)
@pytest.mark.config(USER_API_USE_USER_PHONES_CREATION_PY3=True)
async def test_general_post_personal(
        taxi_corp_auth_client,
        db,
        patch,
        response_mock,
        corp_user_auth_client_data,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_user_phone_bulk(phone_ids, *args, **kwargs):
        def hex_to_phone(hex_phone):
            phone = hex_phone.strip('a')
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        return [
            {'id': phone_id, 'phone': hex_to_phone(phone_id)}
            for phone_id in phone_ids
        ]

    @patch(
        'taxi.clients.ucommunications.UcommunicationsClient.send_sms_to_user',
    )
    async def _send_message(personal_phone_id, text, intent):
        assert personal_phone_id == 'pd_id'
        assert text == 'Привет!'
        assert intent == 'taxi_corp_taxi_account_created'

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch('taxi.clients.user_api.UserApiClient._request')
    async def mock_request(location, json, timeout, retries, log_extra=None):
        identifier = bson.ObjectId()

        return {
            'id': str(identifier),
            'phone': json['phone'],
            'type': json['type'],
            'personal_phone_id': str(uuid.uuid4()).replace('-', ''),
            'created': '2019-02-01T13:00:00+0000',
            'updated': '2019-02-01T13:00:00+0000',
            'stat': {
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
            },
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
        }

    response = await taxi_corp_auth_client.post(
        '/1.0/client/client1/user', json=corp_user_auth_client_data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_request.calls

    corp_user = await db.corp_users.find_one({'_id': response_json['_id']})
    for key, value in corp_user_auth_client_data.items():
        assert corp_user[key] == value
