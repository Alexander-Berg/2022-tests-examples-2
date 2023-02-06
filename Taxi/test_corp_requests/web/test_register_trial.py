# flake8: noqa
# pylint: disable=W0621,E0102,R1705

import dataclasses
import re

import pytest

REQUEST_PHONE_CLEANED = '+79011111111'


@pytest.fixture
def mock_corp_clients_dupplies(mockserver):
    class MockCorpClients:
        @dataclasses.dataclass
        class CorpClientsData:
            clients_list: dict
            clients_list_empty: dict

        data = CorpClientsData(
            clients_list={
                'clients': [
                    {
                        'active_users_count': 0,
                        'billing_id': 'billing_id_2',
                        'contracts': [],
                        'country': 'rus',
                        'city': 'Msc',
                        'email': 'qwerty@gmail.com',
                        'features': [],
                        'id': 'client_id_2',
                        'is_trial': True,
                        'name': 'ABC',
                        'yandex_login': 'yandex_login_2',
                        'phone': '+79011111111',
                        'updated_at': '1234.56',
                        'services': {
                            'cargo': {'is_active': False},
                            'drive': {'is_active': False},
                            'eats': {'is_active': False},
                            'eats2': {'is_active': False},
                            'taxi': {'is_active': False},
                        },
                        'without_vat_contract': False,
                    },
                ],
                'skip': 0,
                'limit': 50,
                'amount': 1,
                'sort_field': 'name',
                'sort_direction': 1,
                'search': 'corp_client_2',
            },
            clients_list_empty={
                'clients': [],
                'skip': 0,
                'limit': 50,
                'amount': 0,
                'sort_field': 'name',
                'sort_direction': 1,
                'search': 'corp_client_2',
            },
        )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/clients/list/accurate')
        async def clients_list(request):
            if request.method == 'GET':
                skip = int(request.query.get('skip'))
                if skip == 0:
                    return mockserver.make_response(
                        json=MockCorpClients.data.clients_list, status=200,
                    )
                return mockserver.make_response(
                    json=MockCorpClients.data.clients_list_empty, status=200,
                )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/clients/attendance')
        async def clients_attendance(request):
            return mockserver.make_response(
                json={'attendances': []}, status=200,
            )

    return MockCorpClients()


@pytest.fixture
def mock_corp_clients_400(mockserver):
    class MockCorpClients:
        @dataclasses.dataclass
        class CorpClientsData:
            clients_list: dict

        data = CorpClientsData(
            clients_list={
                'clients': [],
                'skip': 0,
                'limit': 50,
                'amount': 0,
                'sort_field': 'name',
                'sort_direction': 1,
                'search': 'corp_client_2',
            },
        )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/clients/create')
        async def create_client(request):
            if request.method == 'POST':
                return mockserver.make_response(
                    json={
                        'code': '400',
                        'message': 'corp clients custom error',
                    },
                    status=400,
                )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/clients/list/accurate')
        async def clients_list(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.clients_list, status=200,
                )

    return MockCorpClients()


@pytest.mark.parametrize(
    ['request_phone'],
    [
        pytest.param(REQUEST_PHONE_CLEANED),
        pytest.param(REQUEST_PHONE_CLEANED[1:]),
    ],
)
@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-requests'},
        {'dst': 'stq-agent', 'src': 'corp-requests'},
        {'dst': 'corp-clients', 'src': 'corp-requests'},
    ],
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 12,
            'prefixes': ['+79', '+78'],
            'matches': ['^79', '^78'],
        },
    ],
)
@pytest.mark.parametrize(
    ('request_params',),
    [
        pytest.param(
            {
                'path': '/v1/register-trial',
                'headers': {'X-Remote-IP': 'remote_ip'},
            },
            id='non-mobile',
        ),
        pytest.param(
            {
                'path': '/4.0/corp-requests/v1/register-trial',
                'headers': {
                    'X-Remote-IP': 'remote_ip',
                    'X-YaTaxi-UserId': 'user_id_1',
                },
            },
            id='mobile',
        ),
    ],
)
@pytest.mark.parametrize(
    ('contract_type',), [pytest.param('cargo'), pytest.param('taxi')],
)
async def test_register_trial(
        mock_mds,
        mock_personal_random_gen_login,
        taxi_corp_requests_web,
        blackbox_mock,
        mock_passport_internal,
        mock_corp_clients,
        mock_captcha,
        db,
        stq,
        request_phone,
        web_context,
        request_params,
        contract_type,
):
    json = {
        'phone': request_phone,
        'utm': {
            'utm_medium': 'cpc',
            'utm_source': 'yadirect',
            'utm_campaign': '[YT]DT_BB-goal_RU-MOW-MSK_CorpTaxi_1business',
            'utm_term': 'корпоративное такси яндекс',
            'utm_content': '3296395919_6308959046',
            'ya_source': 'businesstaxi',
            'ya_vat_nocheck': True,
        },
        'email': 'qwerty@gmail.com',
        'city': 'Msc',
        'company': 'ABC',
        'name': 'Ivan',
        'contract_type': contract_type,
    }
    if request_params['path'] == '/v1/register-trial':
        json['captcha_key'] = 'captcha_key'
        json['captcha_answer'] = 'captcha_value'

    response = await taxi_corp_requests_web.post(**request_params, json=json)

    assert response.status == 200

    response_json = await response.json()

    call = stq.corp_notices_process_event.next_call()

    assert call['kwargs']['event_name'] == 'NewTrialClient'

    web_context.corp_crypto.decrypt(
        call['kwargs']['data'].pop('encrypted_password'),
    )
    re.match(
        r'corp-abc\d{5}', call['kwargs']['data'].pop('yandex_login'),
    ).group(0)
    assert call['kwargs']['data'] == {
        'client_id': 'client_id',
        'contract_type': contract_type,
        'flow': 'register_trial',
    }

    create_call = mock_corp_clients.create_client.next_call()
    create_call_req = create_call['request'].json

    assert create_call_req['phone'] == REQUEST_PHONE_CLEANED

    request_draft = await db.corp_client_request_drafts.find(
        {'client_id': response_json['client_id']},
    ).to_list(None)

    assert len(request_draft) == 1
    assert request_draft[0]['references'] == json['utm']
    assert request_draft[0]['flow'] == 'register_trial'
    assert 'updated' in request_draft[0] and 'created' in request_draft[0]
    assert request_draft[0]['references']['ya_vat_nocheck']

    service_handlers = {
        'taxi': mock_corp_clients.service_taxi,
        'cargo': mock_corp_clients.service_cargo,
    }

    if contract_type == 'cargo':
        assert service_handlers[contract_type].next_call()['request'].json == {
            'is_active': True,
            'is_visible': True,
        }

    assert not mock_corp_clients.service_taxi.has_calls
    assert not mock_corp_clients.service_cargo.has_calls


@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-requests'},
        {'dst': 'stq-agent', 'src': 'corp-requests'},
    ],
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 12,
            'prefixes': ['+79', '+78'],
            'matches': ['^79', '^78'],
        },
    ],
    CORP_CLIENT_REQUESTS_DENY_DUPLIES=True,
    CORP_PASSPORT_REGISTRATION_EXTERNAL_LIMIT=0,
    CORP_PASSPORT_REGISTRATION_EXTERNAL_MOBILE_LIMIT=3,
)
@pytest.mark.parametrize(
    ('request_params', 'incorrect_values', 'expected_json'),
    [
        pytest.param(
            {
                'path': '/v1/register-trial',
                'headers': {'X-Remote-IP': 'remote_ip'},
            },
            {'phone': 'aaa', 'email': 'a@gmail.com'},
            {
                'code': 'validation error',
                'details': {},
                'message': (
                    '{\'phone\': [\'phone length with plus sign should '
                    'be greater than 4 symbols\']}'
                ),
            },
            id='non-mobile',
        ),
        pytest.param(
            {
                'path': '/4.0/corp-requests/v1/register-trial',
                'headers': {
                    'X-Remote-IP': 'remote_ip',
                    'X-YaTaxi-UserId': 'user_id_1',
                },
            },
            {'phone': 'aaa', 'email': 'a@gmail.com'},
            {
                'code': 'VALIDATION_ERROR',
                'details': {
                    'reason': 'validation error',
                    'fields': [
                        {
                            'field': 'phone',
                            'messages': ['error.phone_validation_error'],
                        },
                    ],
                },
                'message': '',
            },
            id='mobile',
        ),
        pytest.param(
            {
                'path': '/4.0/corp-requests/v1/register-trial',
                'headers': {
                    'X-Remote-IP': 'remote_ip',
                    'X-YaTaxi-UserId': 'user_id_1',
                },
            },
            {'phone': 'aaa', 'email': 'mail.com'},
            {
                'code': 'VALIDATION_ERROR',
                'details': {
                    'reason': 'validation error',
                    'fields': [
                        {
                            'field': 'phone',
                            'messages': ['error.phone_validation_error'],
                        },
                        {
                            'field': 'email',
                            'messages': ['error.email_validation_error'],
                        },
                    ],
                },
                'message': '',
            },
            id='mobile (two fields)',
        ),
        pytest.param(
            {
                'path': '/4.0/corp-requests/v1/register-trial',
                'headers': {
                    'X-Remote-IP': 'remote_ip',
                    'X-YaTaxi-UserId': 'user_id_1',
                },
            },
            {'phone': REQUEST_PHONE_CLEANED, 'email': 'ммммм@gmail.com'},
            {
                'code': 'VALIDATION_ERROR',
                'details': {
                    'reason': 'validation error',
                    'fields': [
                        {
                            'field': 'email',
                            'messages': ['error.email_validation_error'],
                        },
                    ],
                },
                'message': '',
            },
            id='email error',
        ),
    ],
)
async def test_register_trial_validation_error(
        mock_mds,
        mock_personal_random_gen_login,
        mock_captcha,
        web_app_client,
        blackbox_mock,
        mock_passport_internal,
        mock_corp_clients,
        request_params,
        incorrect_values,
        expected_json,
):
    json = {
        'city': 'MSK',
        'company': 'OOO Company 1',
        'name': 'Ivan',
        'contract_type': 'taxi',
    }
    json.update(incorrect_values)
    if request_params['path'] == '/v1/register-trial':
        json['captcha_key'] = 'captcha_key'
        json['captcha_answer'] = 'captcha_value'

    response = await web_app_client.post(**request_params, json=json)

    assert response.status == 400
    response_json = await response.json()
    assert expected_json == response_json


@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-requests'},
        {'dst': 'stq-agent', 'src': 'corp-requests'},
        {'dst': 'corp-clients', 'src': 'corp-requests'},
    ],
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 12,
            'prefixes': ['+79', '+78'],
            'matches': ['^79', '^78'],
        },
    ],
    CORP_PASSPORT_REGISTRATION_EXTERNAL_LIMIT=0,
    CORP_PASSPORT_REGISTRATION_EXTERNAL_MOBILE_LIMIT=3,
)
@pytest.mark.parametrize(
    ('request_params',),
    [
        pytest.param(
            {
                'path': '/v1/register-trial',
                'headers': {'X-Remote-IP': 'remote_ip'},
            },
            id='non-mobile',
        ),
        pytest.param(
            {
                'path': '/4.0/corp-requests/v1/register-trial',
                'headers': {
                    'X-Remote-IP': 'remote_ip',
                    'X-YaTaxi-UserId': 'user_id_1',
                },
            },
            id='mobile',
        ),
    ],
)
async def test_register_trial_400(
        mock_mds,
        mock_personal_random_gen_login,
        mock_captcha,
        taxi_corp_requests_web,
        blackbox_mock,
        mock_passport_internal,
        mock_corp_clients_400,
        db,
        request_params,
):
    json = {
        'phone': REQUEST_PHONE_CLEANED,
        'utm': {
            'utm_medium': 'cpc',
            'utm_source': 'yadirect',
            'utm_campaign': '[YT]DT_BB-goal_RU-MOW-MSK_CorpTaxi_1business',
            'utm_term': 'корпоративное такси яндекс',
            'utm_content': '3296395919_6308959046',
            'ya_source': 'businesstaxi',
        },
        'email': 'qwerty@gmail.com',
        'city': 'Msc',
        'company': 'ABC',
        'name': 'Ivan',
        'contract_type': 'taxi',
    }
    if request_params['path'] == '/v1/register-trial':
        json['captcha_key'] = 'captcha_key'
        json['captcha_answer'] = 'captcha_value'

    response = await taxi_corp_requests_web.post(**request_params, json=json)

    assert response.status == 400
    response_json = await response.json()
    assert response_json['message'] == 'corp clients custom error'


@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-requests'},
        {'dst': 'stq-agent', 'src': 'corp-requests'},
        {'dst': 'corp-clients', 'src': 'corp-requests'},
    ],
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 12,
            'prefixes': ['+79', '+78'],
            'matches': ['^79', '^78'],
        },
    ],
    CORP_PASSPORT_REGISTRATION_EXTERNAL_LIMIT=0,
    CORP_PASSPORT_REGISTRATION_EXTERNAL_MOBILE_LIMIT=3,
)
@pytest.mark.parametrize(
    ('request_params',),
    [
        pytest.param(
            {
                'path': '/v1/register-trial',
                'headers': {'X-Remote-IP': 'remote_ip'},
            },
            id='non-mobile',
        ),
        pytest.param(
            {
                'path': '/4.0/corp-requests/v1/register-trial',
                'headers': {
                    'X-Remote-IP': 'remote_ip',
                    'X-YaTaxi-UserId': 'user_id_1',
                },
            },
            id='mobile',
        ),
    ],
)
async def test_register_trial_dupplies(
        mock_mds,
        mock_personal_random_gen_login,
        mock_captcha,
        taxi_corp_requests_web,
        blackbox_mock,
        mock_passport_internal,
        mock_corp_clients_dupplies,
        db,
        stq,
        request_params,
):
    json = {
        'phone': REQUEST_PHONE_CLEANED,
        'utm': {
            'utm_medium': 'cpc',
            'utm_source': 'yadirect',
            'utm_campaign': '[YT]DT_BB-goal_RU-MOW-MSK_CorpTaxi_1business',
            'utm_term': 'корпоративное такси яндекс',
            'utm_content': '3296395919_6308959046',
            'ya_source': 'businesstaxi',
        },
        'email': 'qwerty@gmail.com',
        'city': 'Msc',
        'company': 'ABC',
        'name': 'Ivan',
        'contract_type': 'taxi',
    }
    if request_params['path'] == '/v1/register-trial':
        json['captcha_key'] = 'captcha_key'
        json['captcha_answer'] = 'captcha_value'

    response = await taxi_corp_requests_web.post(**request_params, json=json)

    call = stq.corp_notices_process_event.next_call()
    assert call['kwargs']['event_name'] == 'DuplicateTrialClient'
    assert call['kwargs']['data'] == {
        'client_id': 'client_id_2',
        'yandex_login': 'yandex_login_2',
        'contract_type': 'taxi',
    }

    response_json = await response.json()
    assert response.status == 409, response_json


@pytest.mark.now('2020-04-21T00:00:00+03:00')
@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-requests'},
        {'dst': 'stq-agent', 'src': 'corp-requests'},
        {'dst': 'corp-clients', 'src': 'corp-requests'},
    ],
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 12,
            'prefixes': ['+79', '+78'],
            'matches': ['^79', '^78'],
        },
    ],
    CORP_PASSPORT_REGISTRATION_EXTERNAL_LIMIT=0,
    CORP_PASSPORT_REGISTRATION_EXTERNAL_MOBILE_LIMIT=0,
)
@pytest.mark.parametrize(
    ('request_params', 'expected_json'),
    [
        pytest.param(
            {
                'path': '/v1/register-trial',
                'headers': {'X-Remote-IP': 'remote_ip'},
            },
            {
                'code': 'GENERAL',
                'details': {},
                'message': 'passport registration limit exceeded',
            },
            id='non-mobile',
        ),
        pytest.param(
            {
                'path': '/4.0/corp-requests/v1/register-trial',
                'headers': {
                    'X-Remote-IP': 'remote_ip',
                    'X-YaTaxi-UserId': 'mobile_user_id',
                },
            },
            {
                'code': 'GENERAL',
                'details': {},
                'message': 'error.register_request_limit_exceeded',
            },
            id='mobile',
        ),
    ],
)
async def test_register_trial_429(
        mock_mds,
        mock_personal_random_gen_login,
        mock_captcha,
        web_app_client,
        blackbox_mock,
        mock_passport_internal,
        mock_corp_clients,
        db,
        request_params,
        expected_json,
):
    json = {
        'phone': REQUEST_PHONE_CLEANED,
        'utm': {
            'utm_medium': 'cpc',
            'utm_source': 'yadirect',
            'utm_campaign': '[YT]DT_BB-goal_RU-MOW-MSK_CorpTaxi_1business',
            'utm_term': 'корпоративное такси яндекс',
            'utm_content': '3296395919_6308959046',
            'ya_source': 'businesstaxi',
        },
        'email': 'qwerty@gmail.com',
        'city': 'Msc',
        'company': 'ABC',
        'name': 'Ivan',
        'contract_type': 'taxi',
    }

    if request_params['path'] == '/v1/register-trial':
        json['captcha_key'] = 'captcha_key'
        json['captcha_answer'] = 'captcha_value'

    response = await web_app_client.post(**request_params, json=json)

    response_json = await response.json()
    assert response.status == 429
    assert expected_json == response_json


@pytest.mark.config(CORP_PASSPORT_REGISTRATION_EXTERNAL_LIMIT=0)
async def test_bad_captcha(taxi_corp_requests_web, mock_captcha):
    json = {
        'phone': REQUEST_PHONE_CLEANED,
        'email': 'qwerty@gmail.com',
        'city': 'Msc',
        'company': 'ABC',
        'name': 'Ivan',
        'contract_type': 'taxi',
        'captcha_key': 'captcha_key',
        'captcha_answer': 'bad_captcha',
    }

    response = await taxi_corp_requests_web.post(
        '/v1/register-trial', json=json, headers={'X-Remote-IP': 'remote_ip'},
    )

    assert response.status == 403
