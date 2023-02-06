# pylint: disable=redefined-outer-name
from aiohttp import web
import pytest

import sf_data_load.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['sf_data_load.generated.service.pytest_plugins']

SF_DATA_LOAD_SF_RULES = [
    {
        'load_period': 1,
        'lookup_alias': 'b2b-cc-sf-cti',
        'sf_api_name': 'DstNumber__c',
        'source': 'B2BCallsFromSfCti',
        'source_field': 'external_phone',
    },
    {
        'load_period': 1,
        'lookup_alias': 'b2b-cc-sf-cti',
        'sf_api_name': 'SrcNumber__c',
        'source': 'B2BCallsFromSfCti',
        'source_field': 'manager_number',
    },
    {
        'load_period': 1,
        'lookup_alias': 'b2b-cc-sf-cti',
        'sf_api_name': 'ExternalId__c',
        'source': 'B2BCallsFromSfCti',
        'source_field': 'cc_sf_cti_call_id',
    },
    {
        'load_period': 1,
        'lookup_alias': 'concat_id_contact_and_task',
        'sf_api_name': 'WhoId',
        'source': 'sf|b2b|Contact',
        'source_field': 'Id',
    },
    {
        'load_period': 1,
        'lookup_alias': 'concat_id_manager_and_task',
        'sf_api_name': 'OwnerId',
        'source': 'sf|b2b|User',
        'source_field': 'Id',
    },
    {
        'load_period': 1,
        'lookup_alias': 'concat_id_contact_and_task_mobile',
        'sf_api_name': 'WhoId',
        'source': 'sf|b2b|Contact',
        'source_field': 'Id',
    },
]
SF_DATA_LOAD_LOOKUPS = {
    'b2b-cc-sf-cti': {
        'create': True,
        'required_fields': ['WhoId', 'OwnerId'],
        'sf_key': 'ExternalId__c',
        'sf_object': 'Task',
        'sf_org': 'b2b',
        'source_key': 'cc_sf_cti_call_id',
        'record_load_by_bulk': 0,
    },
    'concat_id_contact_and_task': {
        'sf_key': 'DstNumber__c',
        'sf_object': 'Task',
        'sf_org': 'b2b',
        'source_key': 'Phone',
        'update': True,
        'record_load_by_bulk': 0,
    },
    'concat_id_contact_and_task_mobile': {
        'sf_key': 'DstNumber__c',
        'sf_object': 'Task',
        'sf_org': 'b2b',
        'source_key': 'MobilePhone',
        'update': True,
        'record_load_by_bulk': 0,
    },
    'concat_id_manager_and_task': {
        'sf_key': 'SrcNumber__c',
        'sf_object': 'Task',
        'sf_org': 'b2b',
        'source_key': 'Extension',
        'update': True,
        'record_load_by_bulk': 0,
    },
}
MANAGER_REQUESTS = [
    {
        'id': 'request_accepted',
        'readonly_fields': [
            'signer_duly_authorized',
            'readonly_fields',
            'created',
            'attachments',
            'billing_external_id',
            'id',
            'client_login',
            'final_status_manager_login',
            'activation_email_sent',
            'manager_login',
            'final_status_date',
            'client_id',
            'last_error',
            'client_tmp_password',
            'status',
            'country',
        ],
        'status': 'accepted',
        'created': '2000-01-01T03:00:00+03:00',
        'updated': '2000-01-01T03:00:00+03:00',
        'manager_login': 'r1_manager_login',
        'signer_duly_authorized': 'authority_agreement',
        'service': 'taxi',
        'contract_type': 'postpaid',
        'company_tin': '500100732259',
        'enterprise_name_short': 'r1_enterprise_name_short',
        'enterprise_name_full': 'r1_enterprise_name_full',
        'legal_address': '7;r1_legal_address',
        'mailing_address': '7;r1_mailing_address',
        'contacts': [
            {
                'name': 'r1_name',
                'email': 'example@yandex.ru',
                'phone': '+79011111111',
            },
        ],
        'bank_bic': 'r1_bank_bic',
        'signer_name': 'r1_signer_name',
        'signer_position': 'r1_signer_position',
        'crm_link': 'r1_crm_link',
        'client_id': 'r1_client_id',
        'client_login': 'small_yandex_login',
        'client_tmp_password': 'some_aes_string',
        'final_status_date': '2000-01-01T03:00:00+03:00',
        'final_status_manager_login': 'r1_final_status_manager_login',
        'billing_client_id': 73170692,
        'last_error': 'error',
        'error_reason': 'some error reason',
        'activation_email_sent': True,
        'attachments': [
            {
                'filename': 'r1_filename1',
                'url': '$mockserver/mds/get-taxi/r1_file_key1',
            },
            {
                'filename': 'r1_filename2',
                'url': '$mockserver/mds/get-taxi/r1_file_key2',
            },
        ],
        'company_cio': 'r1_company_cio',
        'bank_account_number': 'r1_bank_account_number',
        'signer_gender': 'male',
        'power_of_attorney_limit': '100',
        'st_link': 'r1_st_link',
        'desired_button_name': 'r1_desired_button_name',
        'additional_information': 'r1_additional_information',
        'reason': 'r1_reason',
    },
    {
        'id': 'request_pending',
        'readonly_fields': [
            'signer_duly_authorized',
            'readonly_fields',
            'created',
            'attachments',
            'billing_external_id',
            'id',
            'client_login',
            'final_status_manager_login',
            'activation_email_sent',
            'manager_login',
            'final_status_date',
            'client_id',
            'last_error',
            'client_tmp_password',
            'status',
            'country',
        ],
        'status': 'pending',
        'created': '2000-01-02T03:00:00+03:00',
        'updated': '2000-01-03T03:00:00+03:00',
        'manager_login': 'r2_1',
        'signer_duly_authorized': 'charter',
        'service': 'cargo',
        'contract_type': 'prepaid',
        'company_tin': '1503009020',
        'enterprise_name_short': 'r2_4',
        'enterprise_name_full': 'r2_5',
        'legal_address': '6;r2_6',
        'mailing_address': '7;r2_7',
        'contacts': [
            {
                'name': 'r2_8',
                'email': 'lol@yandex.ru',
                'phone': '+79263452243',
            },
            {
                'name': 'r2_18',
                'email': 'lol@yandex.ru',
                'phone': '+79263452243',
            },
        ],
        'bank_bic': 'r2_11',
        'signer_name': 'r2_13',
        'signer_position': 'r2_signer_position',
        'crm_link': 'r2_14',
        'country': 'rus',
        'bank_account_number': 'r2_12',
        'signer_gender': 'female',
        'st_link': 'r2_15',
        'desired_button_name': 'r2_16',
        'additional_information': 'r2_17',
        'kbe': '1',
        'city': 'Москва',
    },
    {
        'id': 'request_accepting',
        'readonly_fields': [
            'signer_duly_authorized',
            'readonly_fields',
            'created',
            'attachments',
            'billing_external_id',
            'id',
            'client_login',
            'final_status_manager_login',
            'activation_email_sent',
            'manager_login',
            'final_status_date',
            'client_id',
            'last_error',
            'client_tmp_password',
            'status',
            'country',
        ],
        'status': 'accepting',
        'created': '2000-01-03T03:00:00+03:00',
        'updated': '2000-01-04T03:00:00+03:00',
        'manager_login': 'r3_1',
        'signer_duly_authorized': 'charter',
        'service': 'taxi',
        'contract_type': 'prepaid',
        'company_tin': '102500351',
        'enterprise_name_short': 'r3_4',
        'enterprise_name_full': 'r3_5',
        'legal_address': 'r3_6',
        'mailing_address': 'r3_7',
        'contacts': [
            {
                'name': 'r3_8',
                'email': 'pochta3_9@yandex.ru',
                'phone': '+31000000',
            },
            {
                'name': 'r3_18',
                'email': 'pochta3_19@yandex.ru',
                'phone': '+32000000',
            },
        ],
        'bank_bic': 'r3_11',
        'signer_name': 'r3_13',
        'signer_position': 'r3_signer_position',
        'crm_link': 'r3_14',
        'bank_account_number': 'r3_12',
        'signer_gender': 'female',
        'st_link': 'r3_15',
        'desired_button_name': 'r3_16',
        'additional_information': 'r3_17',
    },
    {
        'id': 'bad_request',
        'readonly_fields': [
            'signer_duly_authorized',
            'readonly_fields',
            'created',
            'attachments',
            'billing_external_id',
            'id',
            'client_login',
            'final_status_manager_login',
            'activation_email_sent',
            'manager_login',
            'final_status_date',
            'client_id',
            'last_error',
            'client_tmp_password',
            'status',
            'country',
        ],
        'status': 'failed',
        'created': '2000-01-04T03:00:00+03:00',
        'updated': '2000-01-05T03:00:00+03:00',
        'manager_login': 'r4_1',
        'signer_duly_authorized': 'charter',
        'service': 'drive',
        'contract_type': 'prepaid',
        'company_tin': '102500352',
        'enterprise_name_short': 'r4_4',
        'enterprise_name_full': 'r4_5',
        'legal_address': '6,r4_6',
        'mailing_address': '7,r4_7',
        'contacts': [
            {
                'name': 'r4_8',
                'email': 'pochta4_9@yandex.ru',
                'phone': '+41000000',
            },
            {
                'name': 'r4_18',
                'email': 'pochta4_19@yandex.ru',
                'phone': '+42000000',
            },
        ],
        'bank_bic': 'r4_11',
        'signer_name': 'r4_13',
        'signer_position': 'r4_signer_position',
        'crm_link': 'r4_14',
        'bank_account_number': 'r4_12',
        'signer_gender': 'female',
        'st_link': 'r4_15',
        'desired_button_name': 'r4_16',
        'additional_information': 'r4_17',
    },
]
CORP_CLIENTS = [
    {
        'billing_id': '100001',
        'country': 'rus',
        'created': '2021-07-01T13:00:00+03:00',
        'email': 'email@ya.ru',
        'features': [],
        'id': 'client_id_1',
        'is_trial': False,
        'name': 'corp_client_1',
        'billing_name': 'OOO Client1',
        'yandex_login': 'yandex_login_1',
        'tz': 'Europe/Moscow',
        'yandex_id': 'yandex_uid_1',
        'description': 'corp_client_1 description',
        'without_vat_contract': False,
        'services': {
            'taxi': {'is_active': True, 'is_visible': True},
            'eats': {'is_active': True, 'is_visible': True},
            'eats2': {'is_active': True, 'is_visible': True},
        },
        'updated_at': '31525201.0',
    },
]
CORP_DRAFTS = [
    {
        'client_id': 'triad',
        'contract_type': 'taxi',
        'created': '2018-04-11T15:20:09.160000+03:00',
        'updated': '2018-04-12T15:20:09.160000+03:00',
        'yandex_login': 'sraft_login',
        'country': 'rus',
        'company_name': 'name',
        'contact_name': 'mr.Anderson Jr.',
        'contact_phone': '+79263452243',
        'contact_emails': ['example@yandex.ru'],
        'references': {'promo_id': 'click ID', 'utm': 'utm_val'},
        'services': ['taxi', 'eats2', 'drive', 'tanker'],
        'city': 'Москва',
        'enterprise_name_full': 'example',
        'enterprise_name_short': 'example',
        'legal_address': 'Москва;115222;Москворечье;2к2',
        'legal_address_info': {
            'city': 'Москва',
            'street': 'Москворечье',
            'house': '2к2',
            'post_index': '115222',
        },
        'mailing_address': 'Москва;115222;Москворечье;2к2',
        'mailing_address_info': {
            'city': 'Москва',
            'street': 'Москворечье',
            'house': '2к2',
            'post_index': '115222',
        },
        'company_tin': '500100732259',
        'bank_bic': '044525225',
        'bank_account_number': '40702810638050013199',
        'offer_agreement': True,
        'company_cio': '770501001',
        'enterprise_name': 'ООО "ЯНДЕКС.ТАКСИ"',
        'company_ogrn': '1027717009275',
        'company_registration_date': '2010-01-01T15:20:09.160000+03:00',
        'signer_gender': 'male',
        'contract_by_proxy': False,
        'bank_name': 'Банк',
        'processing_agreement': True,
        'signer_position': 'ГЕНЕРАЛЬНЫЙ ДИРЕКТОР',
        'signer_name': 'Шулейко Даниил Владимирович',
        'proxy_scan': 'http://mds.yandex.net/get-taxi/group/key?sign=sign',
        'autofilled_fields': [
            'legal_address',
            'signer_name',
            'signer_position',
            'company_tin',
            'company_cio',
            'company_ogrn',
            'legal_form',
            'company_registration_date',
            'enterprise_name',
        ],
        'legal_form': 'Общество с ограниченной ответственностью',
        'promo_id': '',
        'without_vat_contract': False,
    },
]


@pytest.fixture
def mock_salesforce_auth(mock_multi_salesforce):
    @mock_multi_salesforce('/services/oauth2/token')
    async def _handler(request):
        return web.json_response(
            {
                'access_token': 'TOKEN',
                'instance_url': 'URL',
                'id': 'ID',
                'token_type': 'TYPE',
                'issued_at': '2019-01-01',
                'signature': 'SIGN',
            },
            status=400,
        )

    return _handler


@pytest.fixture
async def salesforce(mockserver):
    @mockserver.json_handler('/salesforce/services/oauth2/token')
    def auth(request):  # pylint: disable=W0612
        data = {
            'access_token': 'b2b_access_token',
            'instance_url': '$mockserver/salesforce',
            'id': 'b2b_id',
            'token_type': 'b2b_token_type',
            'issued_at': 'b2b_issued_at',
            'signature': 'b2b_signature',
        }
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler(
        r'/salesforce/services/data/v46.0'
        r'/sobjects/(?P<sobject_type>\w+)/(?P<sobject_id>\w+)',
        regex=True,
    )  # pylint: disable=W0612
    def get_user(request, sobject_type, sobject_id):
        if request.method == 'PATCH':
            return mockserver.make_response(json={}, status=204)
        if request.headers['Authorization'] == 'Bearer b2b_access_token':
            data = {
                'Type': 'b2b',
                'City__c': 'Москва',
                'IBAN__c': 'account',
                'SWIFT__c': 'bik',
            }
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler(
        r'/salesforce/services/data/v46.0/sobjects/(?P<sobject_type>\w+)',
        regex=True,
    )  # pylint: disable=W0612
    def create_object(request, sobject_type):
        if sobject_type == 'Account':
            if request.headers['Authorization'] == 'Bearer b2b_access_token':
                data = {
                    'RecordTypeId': 'RecordTypeAccount',
                    'AccountId': 'b2b',
                    'Status': 'In Progress',
                    'Origin': 'API',
                    'IBAN__c': '1',
                    'SWIFT__c': '1',
                    'Subject': 'Self-Employed Change Payment Details',
                }
        return mockserver.make_response(json=data, status=201)

    @mockserver.json_handler(
        '/salesforce/services/data/v46.0/queryAll',
    )  # pylint: disable=W0612
    def get_query_all(request):
        if request.query['q'].find('test') == -1:
            return mockserver.make_response(json={'totalSize': 0}, status=200)
        return mockserver.make_response(
            json={
                'totalSize': 1,
                'nextRecordsUrl': (
                    '/salesforce/services/data/v46.0'
                    '/sobject/Account/001D000000IomazIAB-1'
                ),
                'records': [
                    {
                        'attributes': {
                            'type': 'Case',
                            'url': (
                                '/services/data/v46.0/sobjects'
                                '/Case/5007S000002T4dBQAS'
                            ),
                        },
                        'SystemModstamp': '2022-02-26T08:52:38.000+0000',
                        'Id': 1,
                        'BIN__c': 'bin_value',
                        'INN__c': 'inn_value',
                        'startdata__c': 'data_value',
                        'Id_temp': '1234',
                        'tmp': 'tmp_value',
                    },
                ],
            },
            status=200,
        )

    @mockserver.json_handler(
        r'/salesforce/services/data/v46.0'
        r'/query/(?P<query_id>\w+)-(?P<start_index>\w+)',
        regex=True,
    )  # pylint: disable=W0612
    def next_query(request, query_id, start_index):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        r'/salesforce/services/data/v46.0/sobjects/(?P<sobject_type>\w+)',
        regex=True,
    )  # pylint: disable=W0612
    def create(request, sobject_type):
        return mockserver.make_response(json={'id': '1'}, status=201)


@pytest.fixture
async def mock_salesforce_timeout(mockserver):
    @mockserver.json_handler('/salesforce/services/oauth2/token')
    def auth(request):  # pylint: disable=W0612
        data = {
            'access_token': 'b2b_access_token',
            'instance_url': '$mockserver/salesforce',
            'id': 'b2b_id',
            'token_type': 'b2b_token_type',
            'issued_at': 'b2b_issued_at',
            'signature': 'b2b_signature',
        }
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler(
        r'/salesforce/services/data/v46.0' r'/sobjects/(?P<sobject_type>\w+)',
        regex=True,
    )  # pylint: disable=W0612
    def create(request, sobject_type):
        return mockserver.make_response(status=500)

    @mockserver.json_handler(
        r'/salesforce/services/data/v46.0'
        r'/sobjects/(?P<sobject_type>\w+)/(?P<sobject_id>\w+)',
        regex=True,
    )  # pylint: disable=W0612
    def update(request, sobject_type, sobject_id):
        return mockserver.make_response(status=500)


@pytest.fixture
async def mock_salesforce_failed(mockserver):
    @mockserver.json_handler('/salesforce/services/oauth2/token')
    def auth(request):  # pylint: disable=W0612
        data = {
            'access_token': 'b2b_access_token',
            'instance_url': '$mockserver/salesforce',
            'id': 'b2b_id',
            'token_type': 'b2b_token_type',
            'issued_at': 'b2b_issued_at',
            'signature': 'b2b_signature',
        }
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler(
        r'/salesforce/services/data/v46.0' r'/sobjects/(?P<sobject_type>\w+)',
        regex=True,
    )  # pylint: disable=W0612
    def create(request, sobject_type):
        return mockserver.make_response(
            json=[{'message': 'cannot create'}], status=400,
        )

    @mockserver.json_handler(
        r'/salesforce/services/data/v46.0'
        r'/sobjects/(?P<sobject_type>\w+)/(?P<sobject_id>\w+)',
        regex=True,
    )  # pylint: disable=W0612
    def update(request, sobject_type, sobject_id):
        return mockserver.make_response(
            json=[{'message': 'cannot create'}], status=400,
        )


@pytest.fixture
def mock_manager_request(mockserver):
    @mockserver.json_handler(
        'corp-requests/v1/manager-request/list/updated-since',
    )
    async def _handler(request):
        return mockserver.make_response(
            json={'manager_requests': MANAGER_REQUESTS}, status=200,
        )


@pytest.fixture
def mock_corp_drafts(mockserver):
    @mockserver.json_handler(
        'corp-requests/v1/client-request-drafts/list/updated-since',
    )
    async def _handler(request):
        return mockserver.make_response(
            json={'client_request_drafts': CORP_DRAFTS}, status=200,
        )


@pytest.fixture
def mock_corp_clients(mockserver):
    @mockserver.json_handler('corp-clients/v1/clients/list/updated-since')
    async def _handler(request):
        return mockserver.make_response(
            json={'clients': CORP_CLIENTS}, status=200,
        )
