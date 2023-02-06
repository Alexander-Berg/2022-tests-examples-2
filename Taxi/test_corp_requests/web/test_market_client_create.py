import copy
import datetime
import typing

import pytest


BASE_REQUEST: typing.Dict[str, typing.Any] = {
    'city': 'Москва',
    'company_name': 'ООО Ромашка',
    'contact_name': 'Василий',
    'contact_phone': '+79991112233',
    'contact_email': 'example@yandex.ru',
    'enterprise_name_full': 'ООО «Ромашка»',
    'enterprise_name_short': 'Ромашка',
    'legal_form': 'ООО «РОМАШКА»',
    'legal_address_info': {
        'street': 'Ботаническая',
        'house': '3',
        'city': 'Москва',
        'post_index': '111',
    },
    'mailing_address_info': {
        'street': 'Ботаническая',
        'house': '3',
        'city': 'Москва',
        'post_index': '111',
    },
    'company_tin': '9664576408',
    'company_cio': '966401000',
    'signer_position': 'Директор',
    'signer_name': 'Вася',
    'signer_gender': 'male',
    'market_passport_login': 'market_login',
}

UTM_MARKS = {
    'utm_medium': 'cpc',
    'utm_source': 'yadirect',
    'utm_campaign': '[YT]DT_BB-goal_RU-MOW-MSK_CorpMarket_1business',
    'utm_term': 'корпоративный маркет',
    'utm_content': '3296395919_6308959046',
    'ya_source': 'businessmarket',
}

FULL_REQUEST = dict(
    BASE_REQUEST,
    enterprise_name='Ромашка',
    company_ogrn='1187746005072',
    company_registration_date='2021-02-28T12:30:00+03:00',
    bank_bic='1234',
    bank_account_number='1234',
    bank_name='банк',
    autofilled_fields=['legal_address_info', 'mailing_address_info'],
    edo_operator='diadoc',
    utm=UTM_MARKS,
    disable_go_communications=True,
)

DB_CLIENT_REQUEST_TEMPLATE = {
    'bank_account_number': '',
    'bank_bic': '',
    'bank_name': '',
    'city': 'Москва',
    'client_id': 'market_client_1',
    'company_cio': '966401000',
    'company_name': 'ООО Ромашка',
    'company_tin': '9664576408',
    'company_tin_id': '139d4cb653499c80def2c8139bbe433d',
    'contact_emails': ['example@yandex.ru'],
    'contact_emails_ids': ['7385287bf0079ffaa7ffe95ac293c63d'],
    'contact_name': 'Василий',
    'contact_phone': '+79991112233',
    'contact_phone_id': '75188e7dc667bb5fece36b9bc7980dc4',
    'contract_by_proxy': False,
    'contract_type': 'multi_market',
    'country': 'rus',
    'enterprise_name': '',
    'enterprise_name_full': 'ООО «Ромашка»',
    'enterprise_name_short': 'Ромашка',
    'legal_address': 'Москва;111;Ботаническая;3',
    'legal_address_info': {
        'city': 'Москва',
        'house': '3',
        'post_index': '111',
        'street': 'Ботаническая',
    },
    'legal_form': 'ООО «РОМАШКА»',
    'mailing_address': 'Москва;111;Ботаническая;3',
    'mailing_address_info': {
        'city': 'Москва',
        'house': '3',
        'post_index': '111',
        'street': 'Ботаническая',
    },
    'offer_agreement': True,
    'processing_agreement': True,
    'services': ['taxi', 'drive', 'eats2', 'market'],
    'signer_gender': 'male',
    'signer_name': 'Вася',
    'signer_position': 'Директор',
    'status': 'pending',
    'yandex_login': 'yandex_login',
    'yandex_login_id': '6033a0d9faf483a3c0fa3b2791744091',
    'is_active': True,
    'references': {},
    'disable_go_communications': False,
    'additional_login': 'market_login',
}


@pytest.mark.parametrize(
    ['created_client_id', 'request_data', 'expected_client_request_template'],
    [
        pytest.param(
            'market_client_1',
            BASE_REQUEST,
            copy.deepcopy(DB_CLIENT_REQUEST_TEMPLATE),
            id='min-fields-path',
        ),
        pytest.param(
            'market_client_1',
            FULL_REQUEST,
            {
                **DB_CLIENT_REQUEST_TEMPLATE,
                'enterprise_name': 'Ромашка',
                'company_ogrn': '1187746005072',
                'company_registration_date': datetime.datetime(
                    2021, 2, 28, 9, 30,
                ),
                'bank_bic': '1234',
                'bank_account_number': '1234',
                'bank_name': 'банк',
                'autofilled_fields': [
                    'legal_address_info',
                    'mailing_address_info',
                ],
                'references': UTM_MARKS,
                'edo': {'operator': 'diadoc', 'organization': 'market'},
                'disable_go_communications': True,
            },
            id='full-fields-path',
        ),
        pytest.param(
            'market_client_1',
            {**BASE_REQUEST, 'edo_operator': 'diadoc'},
            {
                **DB_CLIENT_REQUEST_TEMPLATE,
                **{'edo': {'operator': 'diadoc', 'organization': 'market'}},
            },
            marks=pytest.mark.config(
                CORP_EDO_TESTING_CLIENTS_MAPPING={
                    'enabled': True,
                    'clients': {'market_login': {'diadoc': {'inn': '123'}}},
                },
            ),
            id='use-inn-mapping-config',
        ),
    ],
)
@pytest.mark.config(CORP_CLIENT_REQUESTS_AUTO_ACCEPT=True)
async def test_market_offer_create_success(
        web_app_client,
        blackbox_mock,
        mock_corp_clients,
        mock_passport_internal,
        mockserver,
        db,
        stq,
        patch,
        created_client_id,
        request_data,
        expected_client_request_template,
):
    @patch('corp_requests.api.common.passport_registration.create_login')
    async def _create_login(*args, **kwargs):
        return 'yandex_login'

    @mockserver.json_handler('/corp-managers/v1/managers/create')
    def create_manager(request):
        return {'id': 'role_id'}

    mock_corp_clients.data.create_client_response = {'id': created_client_id}

    response = await web_app_client.post(
        '/v1/market-client/create',
        json=request_data,
        headers={'X-Remote-IP': 'remote_ip'},
    )

    # check handler response
    response_data = await response.json()
    assert response.status == 200, response_data
    assert response_data == {'client_id': created_client_id}

    # check client request draft in db
    client_request_draft = await db.corp_client_request_drafts.find_one(
        {'client_id': created_client_id},
        projection={'_id': False, 'created': False, 'updated': False},
    )
    assert client_request_draft == {
        **expected_client_request_template,
        **{'draft_status': 'validated', 'flow': 'register_trial'},
    }

    # check client request in db
    client_request = await db.corp_client_requests.find_one(
        {'client_id': created_client_id},
        projection={
            '_id': False,
            'created': False,
            'updated': False,
            'locked': False,
            'task_id': False,
        },
    )
    assert client_request == expected_client_request_template

    # check create trial client request
    assert mock_corp_clients.create_client.next_call()['request'].json == {
        'city': 'Москва',
        'country': 'rus',
        'email': 'example@yandex.ru',
        'is_trial': True,
        'name': 'ООО Ромашка',
        'phone': '+79991112233',
        'yandex_login': 'yandex_login',
    }

    # check client role creation
    assert create_manager.next_call()['request'].json == {
        'client_id': 'market_client_1',
        'role': 'client',
        'yandex_login': 'market_login',
    }

    # check auto accept stq kwargs
    accept_request_stq_call = stq.corp_accept_client_request.next_call()[
        'kwargs'
    ]
    assert accept_request_stq_call['status'] == 'accepted'
    assert accept_request_stq_call['client_request']['country_id'] == 225


@pytest.mark.parametrize(
    ['request_data', 'expected_code', 'expected_response'],
    [
        pytest.param(
            {**BASE_REQUEST, **{'market_passport_login': None}},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': 'market_passport_login is required property',
                },
                'message': 'Some parameters are invalid',
            },
            id='validation_error',
        ),
        pytest.param(
            {**BASE_REQUEST, 'edo_operator': 'diadoc'},
            400,
            {
                'code': 'client_not_in_mapping',
                'details': {},
                'message': (
                    'add client to CORP_EDO_TESTING_CLIENTS_MAPPING config'
                ),
            },
            marks=pytest.mark.config(
                CORP_EDO_TESTING_CLIENTS_MAPPING={
                    'enabled': True,
                    'clients': {},
                },
            ),
            id='client_not_in_mapping',
        ),
        pytest.param(
            {**BASE_REQUEST, **{'company_tin': '7727563778'}},
            400,
            {
                'code': 'client-request-duplicate-error',
                'details': {},
                'message': 'client request with this company_tin is pending',
            },
            id='company_tin_duplicate',
        ),
    ],
)
async def test_market_offer_create_fail(
        web_app_client, request_data, expected_code, expected_response,
):
    response = await web_app_client.post(
        '/v1/market-client/create',
        json=request_data,
        headers={'X-Remote-IP': 'remote_ip'},
    )

    response_data = await response.json()
    assert response.status == expected_code, response_data
    assert response_data == expected_response
