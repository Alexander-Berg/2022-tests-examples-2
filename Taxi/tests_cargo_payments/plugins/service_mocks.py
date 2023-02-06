"""
    Describe here mocks for other service calls.
"""
import base64
import collections
import dataclasses
import json

import pytest


_DEFAULT_IBOX_ID = 11111


@pytest.fixture(autouse=True)
def personal_data_request(mockserver):
    def _store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    def _bulk_store(request):
        result = {'items': []}
        for i in request.json['items']:
            result['items'].append(
                {'id': i['value'] + '_id', 'value': i['value']},
            )
        return result

    def _retrieve(request):
        if request.json['id'][-3:] != '_id':
            return mockserver.make_response(
                status=404,
                json={
                    'code': '404',
                    'message': 'Not found ' + request.json['id'],
                },
            )
        return {'id': request.json['id'], 'value': request.json['id'][:-3]}

    def _bulk_retrieve(request):
        result = {'items': []}
        for i in request.json['items']:
            result['items'].append({'id': i['id'], 'value': i['id'][:-3]})
        return result

    @mockserver.json_handler('/personal/v1/phones/store')
    def _phones_store(request):
        return _store(request)

    @mockserver.json_handler('/personal/v1/emails/store')
    def _emails_store(request):
        return _store(request)

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones_bulk_store(request):
        return _bulk_store(request)

    @mockserver.json_handler('/personal/v1/emails/bulk_store')
    def _emails_bulk_store(request):
        return _bulk_store(request)

    @mockserver.json_handler('/personal/v1/tins/bulk_store')
    def _tins_bulk_store(request):
        return _bulk_store(request)

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return _retrieve(request)

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _emails_retrieve(request):
        assert request.json['id'] != ''
        return _retrieve(request)

    @mockserver.json_handler('/personal/v1/tins/retrieve')
    def _tins_retrieve(request):
        return _retrieve(request)

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        return _bulk_retrieve(request)

    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def _emails_bulk_retrieve(request):
        for email_id in request.json['items']:
            assert email_id['id'] != ''
        return _bulk_retrieve(request)

    @mockserver.json_handler('/personal/v1/identifications/retrieve')
    def _identifications_retrieve(request):
        return _retrieve(request)


def check_hardcode_post_fields(request):
    assert request.json['Ip'] == '5.255.255.77'
    assert request.json['Lang'] == 'RU'
    assert request.json['AppFramework'] == 1
    assert request.json['Location'] == {'Latitude': 55, 'Longitude': 37}
    assert request.json['Country'] == 'Russia'
    assert request.json['CountryCode'] == 'RU'
    assert request.json['DeviceInfo'] == {
        'PhoneManufacturer': 'Yandex Backend',
        'PhoneModel': 'Yandex Backend',
        'DeviceID': 'Yandex Backend',
        'DeviceType': 'Yandex Backend',
        'AppFramework': 1,
        'OS': 'Yandex Backend',
        'OSVersion': 'Yandex Backend',
        'AppID': 'Yandex Backend',
    }


def check_hardcode_get_fields(request):
    assert request.query['listRequestModel.ip'] == '5.255.255.77'
    assert request.query['listRequestModel.lang'] == 'RU'
    assert request.query['listRequestModel.appFramework'] == '1'
    assert request.query['listRequestModel.country'] == 'Russia'
    assert request.query['listRequestModel.countryCode'] == 'RU'


@pytest.fixture(name='mock_link_create', autouse=True)
def _mock_link_create(mockserver):
    @mockserver.json_handler('/processing-2can/api/v1/payment/submit')
    def mock(request):
        check_hardcode_post_fields(request)

        context.requests.append(request.json)

        prefix, token = request.headers['Authorization'].split(' ')

        assert prefix == 'Basic'
        assert base64.b64decode(token) == context.expected_token

        if context.status_code == 200:
            return {
                'Transaction': {
                    'ExternalPayment': {
                        'Link': 'https://2can.ru:443/pay/' + str(
                            context.initial_id + len(context.requests),
                        ),
                    },
                },
            }
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.expected_token = b'default@yandex:234234234'
            self.handler = mock
            self.initial_id = 59228661320002403

    context = Context()

    return context


@pytest.fixture(name='mock_transactions_history', autouse=True)
def _mock_transactions_history(mockserver):
    @mockserver.json_handler('/processing-2can/api/v1/payment/listHistory')
    def mock(request):
        # context.requests.append(request.json)
        check_hardcode_get_fields(request)

        if context.status_code == 200:
            if context.link is not None:
                return {
                    'InProcess': [
                        {
                            'Description': context.description,
                            'ID': context.transaction_id,
                            'Status': 'TEST',
                            'State': 400,
                            'Substate': 411,
                            'ExternalPayment': {'Link': context.link},
                            'Amount': 40,
                            'CurrencyID': 'RUB',
                            'ExtID': '',
                        },
                    ],
                }
            return {
                'Transactions': [
                    {
                        'Description': context.description,
                        'ID': context.transaction_id,
                        'Status': 'TEST',
                        'State': 400,
                        'Substate': 402,
                        'Amount': 40,
                        'CurrencyID': 'RUB',
                        'ExtID': '',
                    },
                ],
            }
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.link = None
            self.description = 'Test'
            self.transaction_id = '5e882507-8447-47fe-8b10-32afe0021209'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_payment_transaction_id', autouse=True)
def _mock_payment_transaction_id(mockserver, current_state):
    @mockserver.json_handler(
        r'/processing-2can/api/v1/payment/(?P<transaction_id>.+)$', regex=True,
    )
    def mock(request, transaction_id):
        if context.status_code == 200:
            return {
                'Transactions': (
                    context.transactions
                    if context.transactions is not None
                    else [
                        {
                            'Description': context.description,
                            'Date': context.date,
                            'State': context.state,
                            'Substate': context.substate,
                            'Result': {'Code': context.code},
                            'ID': transaction_id,
                            'Status': 'TEST',
                            'RRN': 'something',
                            'Amount': 40,
                            'CurrencyID': 'RUB',
                            'ExtID': current_state.payment_id,
                            'TranPos': {
                                'ID': 123123,
                                'Email': (
                                    current_state.performer.agent.login
                                    if current_state.performer is not None
                                    else None
                                ),
                            },
                        },
                    ]
                ),
            }
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.state = 400
            self.substate = 411
            self.code = 0
            self.date = '2021-08-20T15:33:27'
            self.transactions = None
            self.description = 'Test'
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_reversecnp', autouse=True)
def _mock_refund(mockserver):
    @mockserver.json_handler('/processing-2can/api/v1/payment/reversecnp')
    def mock(request):
        check_hardcode_post_fields(request)
        context.requests.append(request)

        prefix, token = request.headers['Authorization'].split(' ')

        assert prefix == 'Basic'
        assert base64.b64decode(token) == context.expected_token

        if context.status_code == 200:
            return {
                'TransactionID': 'baea2851-9438-48e6-88e4-df1148642f43',
                'ErrorCode': 0,
            }
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.expected_token = b'default@yandex:234234234'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_ucommunications')
def _mock_ucommunications(mockserver):
    @mockserver.json_handler('/ucommunications/general/sms/send')
    def send_sms(request):
        return {
            'message': 'OK',
            'code': '200',
            'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
            'status': 'sent',
        }

    return send_sms


@pytest.fixture(name='mock_clck')
def _mock_clck(mockserver):
    @mockserver.json_handler('/clck/--')
    def mock(request):
        # context.requests.append(request.json)
        if context.status_code == 200:
            return {}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_agglomeration')
def _mock_agglomeration(mockserver):
    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    def mock(request):
        # context.requests.append(request.json)
        if context.status_code == 200:
            return {'name': '12345', 'oebs_mvp_id': 'MSK'}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_corp_api')
def _mock_corp_api(mockserver):
    @mockserver.json_handler('/taxi-corp-integration/v1/client')
    def mock(request):
        # context.requests.append(request.json)
        if context.status_code == 200:
            return {
                'client_id': '70a499f9eec844e9a758f4bc33e667c0',
                'name': 'Test',
                'contract_id': '123445',
                'billing_client_id': '113132234',
                'billing_contract_id': '3192522',
                'services': {
                    'cargo': {
                        'is_active': True,
                        'is_visible': True,
                        'contract_id': '123445',
                        'is_auto_activate': False,
                        'min_balance_threshold': None,
                        'is_test': False,
                        'deactivate_threshold_date': None,
                        'deactivate_threshold_ride': None,
                        'low_balance_threshold': None,
                        'low_balance_notification_enabled': None,
                        'contract_info': {
                            'manager_id': '20453',
                            'status': 'active',
                            'payment_type': 'postpaid',
                            'contract_id': '3192501',
                            'services': [1040, 718],
                            'is_offer': False,
                            'balance': None,
                            'is_blocked': None,
                            'offer_accepted': None,
                        },
                        'person': {
                            'id': '14773872',
                            'emails': ['m-SC@qCWF.rKU'],
                            'emails_ids': ['6e230e786dc644f1b327a33ab198e2f5'],
                            'tin_id': 'c339cc48dc254f86b5e038fc84c6c9d1',
                        },
                        'next_day_delivery': True,
                    },
                },
                'country': 'rus',
            }
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='active_contracts')
def _active_contracts(mockserver):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def mock(request):
        # context.requests.append(request.json)
        if context.status_code == 200:
            return [
                {
                    'ID': 3192501,
                    'EXTERNAL_ID': '1837219/21',
                    'PERSON_ID': 14773872,
                    'IS_ACTIVE': 1,
                    'IS_SIGNED': 1,
                    'IS_SUSPENDED': 0,
                    'CURRENCY': 'RUR',
                    'NETTING': None,
                    'NETTING_PCT': None,
                    'LINK_CONTRACT_ID': None,
                    'SERVICES': [1040, 718],
                    'NDS_FOR_RECEIPT': None,
                    'OFFER_ACCEPTED': None,
                    'NDS': None,
                    'PAYMENT_TYPE': 3,
                    'PARTNER_COMMISSION_PCT': None,
                    'PARTNER_COMMISSION_PCT2': None,
                    'IND_BEL_NDS_PERCENT': None,
                    'END_DT': None,
                    'FINISH_DT': None,
                    'DT': '2021-04-15 00:00:00',
                    'CONTRACT_TYPE': 0,
                    'IND_BEL_NDS': None,
                    'COUNTRY': None,
                    'IS_FAXED': 0,
                    'IS_DEACTIVATED': 0,
                    'IS_CANCELLED': 0,
                    'FIRM_ID': 13,
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [['2021-04-15 00:00:00', [1040, 718]]],
                    },
                },
            ]
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='billing_replication_contract')
def _billing_replication_contract(mockserver):
    @mockserver.json_handler('/billing-replication/contract/')
    def mock(request):
        if context.status_code == 200:
            return [
                {
                    'ID': context.contract_ids[0],
                    'EXTERNAL_ID': '2200658/21',
                    'PERSON_ID': context.person_ids[0],
                    'IS_ACTIVE': 1,
                    'IS_SIGNED': 1,
                    'IS_SUSPENDED': 0,
                    'CURRENCY': 'RUR',
                    'SERVICES': context.services[0],
                    'PAYMENT_TYPE': 3,
                    'DT': '2021-07-23 00:00:00',
                    'CONTRACT_TYPE': 0,
                    'IS_FAXED': 0,
                    'IS_DEACTIVATED': 0,
                    'IS_CANCELLED': 0,
                    'FIRM_ID': 13,
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [
                            ['2021-07-23 00:00:00', context.services[0]],
                        ],
                    },
                },
                {
                    'ID': context.contract_ids[1],
                    'EXTERNAL_ID': '2200689/21',
                    'PERSON_ID': context.person_ids[1],
                    'IS_ACTIVE': 1,
                    'IS_SIGNED': 1,
                    'IS_SUSPENDED': 0,
                    'CURRENCY': 'RUR',
                    'SERVICES': context.services[1],
                    'PAYMENT_TYPE': 3,
                    'DT': '2021-07-23 00:00:00',
                    'CONTRACT_TYPE': 0,
                    'IS_FAXED': 0,
                    'IS_DEACTIVATED': 0,
                    'IS_CANCELLED': 0,
                    'FIRM_ID': 13,
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [
                            ['2021-07-23 00:00:00', context.services[1]],
                        ],
                    },
                },
            ]
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.person_ids = [16001342, 16001342]
            self.contract_ids = [3738050, 3738110]
            self.services = [[1040, 718], [650, 135]]
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='billing_replication_person')
def _billing_replication_person(mockserver):
    @mockserver.json_handler('/billing-replication/person/')
    def mock(request):
        if context.status_code == 200:
            return [
                {
                    'ID': context.person_id,
                    'DELIVERY_TYPE': '4',
                    'LEGAL_ADDRESS_POSTCODE': '666666',
                    'NAME': 'Юр. лицо или ПБОЮЛqdZd Дмитриева',
                    'LONGNAME': '000 WBXG',
                    'PHONE': '+7 812 3990776',
                    'INN': context.inn,
                    'CLIENT_ID': '114321660',
                    'AUTHORITY_DOC_TYPE': 'Свидетельство о регистрации',
                    'LEGALADDRESS': 'Avenue 5',
                    'TYPE': 'ur',
                    'EMAIL': 'm-SC@qCWF.rKU',
                    'SIGNER_PERSON_NAME': 'Signer RR',
                    'KPP': '767726208',
                    'OGRN': '379956466494603',
                    'BIK': '044525440',
                    'ACCOUNT': '40702810650063542948',
                    'DT': '2021-07-23 13:31:05',
                },
            ]
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.inn = '7814663521'
            self.person_id = '16001342'
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='billing_orders_process')
def _billing_orders_process(mockserver):
    @mockserver.json_handler('/billing-orders/v2/process/async')
    def mock(request):
        context.last_request = request.json
        if context.status_code == 200:
            return {
                'orders': [
                    {
                        'doc_id': int(
                            request.json['orders'][0]['external_ref'],
                        ),  # history_event_id
                        'topic': 'test',
                        'external_ref': '1234',
                    },
                ],
            }
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock
            self.last_request = {}

    context = Context()

    return context


@pytest.fixture(name='mock_driver_profiles_retrieve', autouse=True)
def _mock_driver_profiles_retrieve(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock(request):
        body = json.loads(request.get_data())
        context.requests.append(body)
        if context.status_code != 200:
            return mockserver.make_response(
                status=context.status_code,
                json={
                    'code': context.error_code,
                    'message': context.error_message,
                },
            )
        profiles = []
        for park_driver_profile_id in body['id_in_set']:
            park_id, driver_id = park_driver_profile_id.split('_')

            profiles.append(
                {
                    'park_driver_profile_id': park_driver_profile_id,
                    'revision': '0',
                    'data': {
                        'park_id': park_id,
                        'uuid': driver_id,
                        'full_name': {
                            'first_name': 'Иван',
                            'middle_name': 'Иванович',
                            'last_name': 'Ёршунов',
                        },
                        'phone_pd_ids': [{'pd_id': '+71234567890_id'}],
                        'email_pd_ids': [],
                    },
                },
            )
        return mockserver.make_response(
            json.dumps({'profiles': profiles}), 200,
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


def _build_agent_info(
        ibox_id, *, is_active=True, client_id=11112, login='test@ya.ru',
):
    return {
        'ID': ibox_id,
        'State': 1 if is_active else 0,
        'ClientID': client_id,
        'Email': login,
    }


@pytest.fixture(name='mock_web_api_agent_create', autouse=True)
def _mock_web_api_agent_create(mockserver):
    @mockserver.json_handler(
        r'/web-api-2can/api/v1/merchant/(?P<merchant_id>\d+)/pos/create$',
        regex=True,
    )
    def mock(request, merchant_id):
        prefix, token = request.headers['Authorization'].split(' ')

        assert prefix == 'Basic'
        assert base64.b64decode(token) == context.expected_token

        context.requests.append(request.json)
        return {
            'Pos': (
                _build_agent_info(context.ibox_id)
                if context.with_pos
                else None
            ),
            'ErrorCode': context.error_code,
            'ErrorMessage': context.error_message,
            'Validations': [],
        }

    class Context:
        def __init__(self):
            self.requests = []
            self.ibox_id = _DEFAULT_IBOX_ID
            self.with_pos = True
            self.error_code = 0
            self.error_message = ''
            self.expected_token = b'default@yandex:234234234'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_web_api_agent_list', autouse=True)
def _mock_web_api_agent_list(mockserver):
    @mockserver.json_handler(
        r'/web-api-2can/api/v1/merchant/(?P<merchant_id>\d+)/pos/list$',
        regex=True,
    )
    def mock(request, merchant_id):
        prefix, token = request.headers['Authorization'].split(' ')

        assert prefix == 'Basic'
        assert base64.b64decode(token) == b'default@yandex:234234234'

        context.requests.append(request.json)
        return {
            'Poses': [
                _build_agent_info(
                    context.ibox_id, is_active=context.is_active,
                ),
            ],
            'ErrorCode': context.error_code,
            'ErrorMessage': context.error_message,
            'Validations': [],
        }

    class Context:
        def __init__(self):
            self.requests = []
            self.ibox_id = _DEFAULT_IBOX_ID
            self.is_active = True
            self.error_code = 0
            self.error_message = ''
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_web_api_agent_update', autouse=True)
def _mock_web_api_agent_update(mockserver):
    @mockserver.json_handler(
        r'/web-api-2can/api/v1/merchant/(?P<merchant_id>\d+)'
        r'/pos/(?P<pos_id>\d+)/update$',
        regex=True,
    )
    def mock(request, merchant_id, pos_id):
        prefix, token = request.headers['Authorization'].split(' ')

        assert prefix == 'Basic'
        assert base64.b64decode(token) == context.expected_token

        context.last_request = request
        context.last_pos_id = pos_id

        # in the case of change state
        new_state = request.json.get('State')
        if new_state is not None:
            is_blocked = new_state == 0
            context.agent_statuses[int(pos_id)] = AgentStatus(
                is_blocked=is_blocked,
            )

        return {
            'Pos': _build_agent_info(context.ibox_id),
            'ErrorCode': context.error_code,
            'ErrorMessage': context.error_message,
            'Validations': [],
        }

    @dataclasses.dataclass
    class AgentStatus:
        is_blocked: bool = True

    class Context:
        def __init__(self):
            self.last_request = None
            self.last_pos_id = None
            self.ibox_id = _DEFAULT_IBOX_ID
            self.agent_statuses = collections.defaultdict(
                AgentStatus,
            )  # ibox_id -> AgentStatus
            self.expected_pos_id = None
            self.expected_token = b'default@yandex:234234234'
            self.error_code = 0
            self.error_message = ''
            self.handler = mock

        def flush(self):
            self.last_request = None
            self.last_pos_id = None
            self.handler.flush()

    context = Context()

    return context


@pytest.fixture(name='mock_tags_upload', autouse=True)
def _mock_tags_upload(mockserver):
    def _is_repeated_request(request):
        for previous_request in context.requests:
            if (
                    previous_request.headers['X-Idempotency-Token']
                    == request.headers['X-Idempotency-Token']
            ):
                return True
        return False

    @mockserver.json_handler('/tags/v2/upload')
    def mock(request):
        context.requests.append(request)
        if _is_repeated_request(request):
            return mockserver.make_response(
                status=202, json={'code': '202', 'message': '202'},
            )
        return {}

    class Context:
        def __init__(self):
            self.requests = []
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='default_ibox_id')
async def _default_ibox_id():
    return _DEFAULT_IBOX_ID


@pytest.fixture(name='rps_limiter')
def _rps_limiter(mockserver):
    class RateLimiterContext:
        def __init__(self):
            self.budgets = {}
            self.is_down = False
            self.fail_attempts = 0
            # resources from the last 'wait_request'
            self.requested = collections.defaultdict(
                lambda: collections.defaultdict(int),
            )
            self.resources = set()

        def set_budget(self, resource, budget):
            self.budgets[resource] = budget
            self.resources.add(resource)

        @property
        def call_count(self):
            return _rps_quotas.times_called

        async def wait_request(self, service, **resources):
            await _rps_quotas.wait_call()
            assert self.requested[service] == dict(resources)
            self.requested[service].clear()

    context = RateLimiterContext()

    @mockserver.json_handler('/statistics/v1/rps-quotas')
    def _rps_quotas(request):
        service = request.args['service']
        requests = request.json['requests']
        for req in requests:
            if req['resource'] in context.resources:
                context.requested[service][req['resource']] += 1
        if context.is_down:
            return mockserver.make_response(status=500)
        if context.fail_attempts > 0:
            context.fail_attempts -= 1
            return mockserver.make_response(status=500)
        quotas = []
        for quota_request in requests:
            resource = quota_request['resource']
            requested = quota_request['requested-quota']
            quota = 0
            if resource in context.budgets:
                quota = min(context.budgets[resource], requested)
                context.budgets[resource] -= quota
            quotas.append({'resource': resource, 'assigned-quota': quota})
        return {'quotas': quotas}

    return context
