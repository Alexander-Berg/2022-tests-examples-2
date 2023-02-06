# pylint: disable=super-init-not-called
# pylint: disable=super-init-not-called
import datetime

from aiohttp import test_utils
import pytest

from taxi_protocol.handlers import urgenthelp

APIKEY_SECDIST = 'zendesk_urgent_help_backend_apikey'


@pytest.mark.config(
    ZENDESK_FEEDBACK_CUSTOM_FIELDS_SPLITTED={
        'yataxi': {'order_id': 38647729, 'urgenthelp_source': 123},
        'yutaxi': {'order_id': 38647729, 'urgenthelp_source': 123},
    },
)
@pytest.mark.parametrize(
    'phone,data,expected_result',
    [
        (
            '+79000000000',
            {'locale': 'ru', 'orderId': '1'},
            {
                'ticket': {
                    'comment': (
                        'Перезвонить пользовате' 'лю по номеру +79000000000'
                    ),
                    'requester': {
                        'email': '79000000000@taxi.' 'yandex.ru',
                        'name': 'devnull',
                        'phone': '+79000000000',
                    },
                    'subject': 'Нужна срочная помощь',
                    'custom_fields': [{'id': 38647729, 'value': '1'}],
                },
            },
        ),
        (
            '+79000000000',
            {'locale': 'en', 'orderId': '2'},
            {
                'ticket': {
                    'comment': (
                        'Перезвонить пользователю' ' по номеру +79000000000'
                    ),
                    'requester': {
                        'email': '79000000000@taxi.' 'yandex.ru',
                        'name': 'devnull',
                        'phone': '+79000000000',
                    },
                    'subject': 'Yandex.Taxi Need urgent help',
                    'custom_fields': [{'id': 38647729, 'value': '2'}],
                },
            },
        ),
        (
            '+79000000000',
            {'locale': 'en', 'orderId': '2', 'source': 'safety_center'},
            {
                'ticket': {
                    'comment': (
                        'Перезвонить пользователю' ' по номеру +79000000000'
                    ),
                    'requester': {
                        'email': '79000000000@taxi.' 'yandex.ru',
                        'name': 'devnull',
                        'phone': '+79000000000',
                    },
                    'subject': 'Yandex.Taxi Need urgent help',
                    'custom_fields': [
                        {'id': 123, 'value': 'safety_center'},
                        {'id': 38647729, 'value': '2'},
                    ],
                },
            },
        ),
    ],
)
async def test_create_ticket_data(
        monkeypatch,
        protocol_client,
        protocol_app,
        phone,
        data,
        expected_result,
):
    request = test_utils.make_mocked_request('POST', '/')
    request['data'] = data
    request.app.config = protocol_app.config
    # pylint: disable=protected-access
    assert (
        urgenthelp._create_ticket_data(
            request, phone, protocol_app.zendesk_client,
        )
        == expected_result
    )


@pytest.mark.parametrize('apikey', ['API_KEY', APIKEY_SECDIST])
@pytest.mark.config(ZENDESK_URGENT_HELP_BACKEND_APIKEY='API_KEY')
@pytest.mark.parametrize(
    'request_data',
    [
        (
            {
                'phone': '+79000000000',
                'locale': 'ru',
                'orderId': '1',
                'idempotency_key': '123',
            }
        ),
    ],
)
async def test_idempotency(patch, protocol_client, db, request_data, apikey):
    @patch('taxi.clients.territories.TerritoriesApiClient.get_all_countries')
    async def _get_all_countries(*args, **kwargs):
        return await db.countries.find().to_list(None)

    headers = {'YaTaxi-Api-Key': apikey}

    response = await protocol_client.post(
        '/1.0/urgenthelp/', json=request_data, headers=headers,
    )
    assert response.status == 200

    response = await protocol_client.post(
        '/1.0/urgenthelp/', json=request_data, headers=headers,
    )
    assert response.status == 200


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(ZENDESK_URGENT_HELP_BACKEND_APIKEY='API_KEY')
@pytest.mark.parametrize(
    'request_data',
    [
        (
            {
                'phone': '+79000000000',
                'locale': 'ru',
                'orderId': '1',
                'idempotency_key': '123',
            }
        ),
    ],
)
async def test_urgenthelp_tvm_auth(
        monkeypatch, patch, protocol_client, db, protocol_app, request_data,
):
    @patch('taxi.clients.territories.TerritoriesApiClient.get_all_countries')
    async def _get_all_countries(*args, **kwargs):
        return await db.countries.find().to_list(None)

    @patch('taxi_protocol.handlers.base_handler._check_auth')
    async def _check_auth(*args, **kwargs):
        return object()

    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def _get_allowed_service_name(*args, **kwargs):
        return 'protocol-py3'

    headers = {'X-Ya-Service-Ticket': 'service-ticket'}

    response = await protocol_client.post(
        '/1.0/urgenthelp/', json=request_data, headers=headers,
    )

    assert response.status == 200


@pytest.mark.translations(
    zendesk_forms={
        'urgenthelp_ticket.subject': {
            'en': 'Need urgent help',
            'ru': 'Надо ургентхелп',
        },
        'urgenthelp_ticket.body': {
            'en': 'Please call {phone!s}',
            'ru': 'Надо позвонить на {phone!s}',
        },
    },
)
@pytest.mark.parametrize(
    'data,headers,expected_response,expected_stq_put',
    [
        (
            {'source': 'app', 'locale': 'en'},
            {'X-YaTaxi-UserId': 'some_user_id'},
            {},
            {
                'queue': 'support_info_urgenthelp_ticket',
                'id': '2104653bdac343e39ac57869d0bd738d_urgenthelp',
                'args': ['2104653bdac343e39ac57869d0bd738d_urgenthelp'],
                'eta': datetime.datetime(1970, 1, 1, 0, 0),
                'kwargs': {
                    'owner_id': '5d84f4a63934cf8f37562ffe',
                    'phone': '+79000000000',
                    'metadata': {'source': 'app', 'locale': 'en'},
                },
            },
        ),
        (
            {
                'idempotency_key': '123',
                'source': 'app',
                'phone': '+79000000000',
                'locale': 'ru',
                'orderId': '1',
                'driver_id': 'some_driver_id',
                'driver_uuid': 'some_driver_uuid',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_db_id',
                'user_platform': 'iphone',
            },
            {'X-YaTaxi-UserId': 'some_user_id'},
            {},
            {
                'queue': 'support_info_urgenthelp_ticket',
                'id': '123_urgenthelp',
                'args': ['123_urgenthelp'],
                'eta': datetime.datetime(1970, 1, 1, 0, 0),
                'kwargs': {
                    'owner_id': '5d84f4a63934cf8f37562ffe',
                    'phone': '+79000000000',
                    'metadata': {
                        'source': 'app',
                        'phone': '+79000000000',
                        'locale': 'ru',
                        'orderId': '1',
                        'driver_id': 'some_driver_id',
                        'driver_uuid': 'some_driver_uuid',
                        'order_alias_id': 'some_alias_id',
                        'park_db_id': 'some_db_id',
                        'user_platform': 'iphone',
                    },
                },
            },
        ),
        (
            {
                'idempotency_key': '123',
                'source': 'app',
                'phone': '+79000000001',
                'locale': 'fr',
                'orderId': '1',
                'driver_id': 'some_driver_id',
                'driver_uuid': 'some_driver_uuid',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_db_id',
                'user_platform': 'iphone',
            },
            {'X-YaTaxi-UserId': 'another_user_id'},
            {},
            {
                'queue': 'support_info_urgenthelp_ticket',
                'id': '123_urgenthelp',
                'args': ['123_urgenthelp'],
                'eta': datetime.datetime(1970, 1, 1, 0, 0),
                'kwargs': {
                    'owner_id': None,
                    'phone': '+79000000001',
                    'metadata': {
                        'source': 'app',
                        'phone': '+79000000001',
                        'locale': 'fr',
                        'orderId': '1',
                        'driver_id': 'some_driver_id',
                        'driver_uuid': 'some_driver_uuid',
                        'order_alias_id': 'some_alias_id',
                        'park_db_id': 'some_db_id',
                        'user_platform': 'iphone',
                    },
                },
            },
        ),
    ],
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
async def test_urgenthelp4(
        mockserver,
        stq,
        mock_uuid_fixture,
        mock_get_all_countries,
        mock_get_users,
        protocol_client,
        protocol_app,
        data,
        headers,
        expected_response,
        expected_stq_put,
):
    @mockserver.json_handler('/user-api/user_phones/get')
    def _mock_get_user_phones(request):
        if request.json['id'] == '5d84f4a63934cf8f37562ffe':
            return {
                'id': '5d84f4a63934cf8f37562ffe',
                'phone': '+79000000000',
                'type': 'yandex',
                'stat': {},
                'is_loyal': False,
                'is_yandex_staff': False,
                'is_taxi_staff': False,
            }
        return mockserver.make_response(status=404)

    response = await protocol_client.post(
        '/4.0/urgenthelp/', json=data, headers=headers,
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data == expected_response

    stq_put_call = stq.support_info_urgenthelp_ticket.next_call()
    del stq_put_call['kwargs']['log_extra']
    assert stq_put_call == expected_stq_put


@pytest.mark.translations(
    zendesk_forms={
        'urgenthelp_ticket.subject': {'en': 'Need urgent help'},
        'urgenthelp_ticket.body': {'en': 'Please call {phone!s}'},
    },
)
@pytest.mark.config(ZENDESK_URGENT_HELP_BACKEND_APIKEY='API_KEY')
@pytest.mark.parametrize(
    'data,headers,expected_response,expected_stq_put,'
    'expected_zendesk_create_ticket',
    [
        (
            {
                'source': 'app',
                'phone': '+79000000001',
                'locale': 'en',
                'orderId': '1',
                'driver_id': 'some_driver_id',
                'driver_uuid': 'some_driver_uuid',
                'order_alias_id': 'some_alias_id',
                'park_db_id': 'some_db_id',
                'user_platform': 'iphone',
                'idempotency_key': '123',
            },
            {'YaTaxi-Api-Key': 'API_KEY'},
            {},
            {
                'queue': 'support_info_urgenthelp_ticket',
                'id': '123_urgenthelp',
                'args': ['123_urgenthelp'],
                'eta': datetime.datetime(1970, 1, 1, 0, 0),
                'kwargs': {
                    'owner_id': None,
                    'phone': '+79000000001',
                    'metadata': {
                        'source': 'app',
                        'phone': '+79000000001',
                        'locale': 'en',
                        'orderId': '1',
                        'driver_id': 'some_driver_id',
                        'driver_uuid': 'some_driver_uuid',
                        'order_alias_id': 'some_alias_id',
                        'park_db_id': 'some_db_id',
                        'user_platform': 'iphone',
                    },
                },
            },
            None,
        ),
    ],
)
async def test_urgenthelp1(
        stq,
        mock_get_all_countries,
        mock_zendesk_ticket_create,
        mock_uuid_fixture,
        mock_zendesk_get_by_external_id,
        protocol_client,
        protocol_app,
        data,
        headers,
        expected_response,
        expected_stq_put,
        expected_zendesk_create_ticket,
):
    response = await protocol_client.post(
        '/1.0/urgenthelp/', json=data, headers=headers,
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data == expected_response

    stq_put_call = stq.support_info_urgenthelp_ticket.next_call()
    del stq_put_call['kwargs']['log_extra']
    assert stq_put_call == expected_stq_put
