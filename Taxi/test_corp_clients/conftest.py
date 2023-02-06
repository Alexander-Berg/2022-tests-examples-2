# pylint: disable=redefined-outer-name

import datetime
import uuid

from aiohttp import web
import pytest

import corp_clients.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['corp_clients.generated.service.pytest_plugins']

CLIENT_ID_TO_EDO_ACCEPTED = {'to_active': True}


@pytest.fixture
def blackbox_mock(mockserver):
    class BlackboxMock:
        @staticmethod
        @mockserver.json_handler('/blackbox/blackbox')
        async def passport(request):
            return {'users': [{'uid': {'value': 'new_yandex_uid'}}]}

    return BlackboxMock()


@pytest.fixture
def corp_billing_mock(mockserver):
    class MockCorpBilling:
        @staticmethod
        @mockserver.json_handler('corp-billing/v1/clients/find')
        async def clients_find(request):
            return {'clients': []}

        @staticmethod
        @mockserver.json_handler('corp-billing/v1/clients/create')
        async def clients_create(request):
            data = request.json
            return {
                'revision': 1,
                'external_ref': data['external_ref'],
                'payment_method_name': data['payment_method_name'],
                'all_services_suspended': False,
                'services': [],
            }

        @staticmethod
        @mockserver.json_handler('corp-billing/v1/clients/update')
        async def clients_update(request):
            data = request.json
            return data

    return MockCorpBilling()


@pytest.fixture
def personal_mock(request, load_json):
    marker = request.node.get_closest_marker('personal_data')
    if not marker:
        request.node.add_marker(
            pytest.mark.personal_data(load_json('personal_data.json')),
        )


@pytest.fixture
def drive_mock(mockserver):
    class DriveMock:
        new_account_id = (
            uuid.uuid4().int % 2 ** 16
        )  # mongo can't store big ints

        @staticmethod
        @mockserver.json_handler('drive/api/b2b/organization/create')
        async def create_organization(request):
            return {'account_id': DriveMock.new_account_id}

    return DriveMock()


@pytest.fixture
def mock_salesforce_query(mock_salesforceb2b):
    @mock_salesforceb2b('/services/data/v46.0/query')
    async def _handler(request):
        select_contract = (
            'SELECT OwnerId,Contract_Num_Yandex_Taxi__c '
            'from Contract '
            'Where Contract_Num_Yandex_Taxi__c IN '
            '(\'101/12\',\'103/12\',\'109/12\',\'105/12\')'
        )

        select_user = (
            'SELECT Tier__c,Name,Phone,Extension,MobilePhone,Id,Email '
            'from User '
            'Where Id IN (\'0051w000004fvEKAAY\',\'0051w000004olFjAAI\') '
            'AND Tier__c IN (\'Enterprise\',\'SMB\')'
        )

        query = request.query['q']

        if select_contract == query:
            return web.json_response(
                {
                    'totalSize': 2,
                    'done': True,
                    'records': [
                        {
                            'attributes': {'type': 'Contract'},
                            'OwnerId': '0051w000004fvEKAAY',
                            'Contract_Num_Yandex_Taxi__c': '101/12',
                        },
                        {
                            'attributes': {'type': 'Contract'},
                            'OwnerId': '0051w000004olFjAAI',
                            'Contract_Num_Yandex_Taxi__c': '103/12',
                        },
                    ],
                },
                status=200,
            )
        if select_user == query:
            return web.json_response(
                {
                    'totalSize': 2,
                    'done': True,
                    'records': [
                        {
                            'attributes': {'type': 'User'},
                            'Tier__c': 'SMB',
                            'Name': 'Мария Козлова',
                            'Phone': None,
                            'Extension': None,
                            'MobilePhone': '+79777777777',
                            'Id': '0051w000004fvEKAAY',
                            'Email': None,
                        },
                    ],
                },
                status=200,
            )

        return web.json_response({}, status=200)

    return _handler


CLIENT_REQUEST_DB = 'corp_client_requests_data.json'
MANAGER_REQUEST_DB = 'corp_manager_requests_data.json'


@pytest.fixture
def mock_corp_requests_search(mock_corp_requests, load_json):
    def filter_request(request):
        # serialize datetime to string
        if request.get('updated'):
            request['updated'] = request['updated'].isoformat()
        if request.get('created'):
            request['created'] = request['created'].isoformat()
        if request.get('_id'):
            request['id'] = request['_id']
        return request

    def base_fields():
        # limit, offset and other are required properties,
        # so we have to set them to some value
        return {
            'limit': -1,
            'offset': -1,
            'total': -1,
            # 'country': 'isr',
            'sort': [{'field': 'created', 'direction': 'asc'}],
        }

    @mock_corp_requests('/v1/client-requests/search')
    async def _client_requests_handler(request):
        corp_requests_response = load_json(CLIENT_REQUEST_DB)
        result = []
        for item in corp_requests_response:
            if (
                    item.get('updated').timestamp()
                    >= datetime.datetime.fromisoformat(
                        request.json.get('updated_since'),
                    ).timestamp()
                    and item.get('status') == request.json.get('status')
            ):
                result.append(item)
        result = list(map(filter_request, result))
        return web.json_response(
            {
                'items': result,
                # 'country': 'isr',
                **base_fields(),
                **request.json,
            },
        )

    @mock_corp_requests('/v1/manager-requests/search')
    async def _manager_requests_handler(request):
        corp_requests_response = load_json(MANAGER_REQUEST_DB)
        result = []
        for item in corp_requests_response:
            if (
                    item.get('updated').timestamp()
                    >= datetime.datetime.fromisoformat(
                        request.json.get('updated_since'),
                    ).timestamp()
                    and item.get('status') in request.json['status']
                    if request.json.get('status')
                    else False
            ):
                item.update(
                    #  required fields
                    **{
                        'id': '',
                        'created': datetime.datetime(2000, 1, 2, 0, 0),
                        'enterprise_name_short': '',
                        'company_tin': '',
                        'manager_login': '',
                        'contract_type': 'postpaid',
                    },
                )
                result.append(item)
        result = list(map(filter_request, result))
        return web.json_response(
            {'items': result, **base_fields(), **request.json},
        )


@pytest.fixture
def mock_salesforce_auth(mock_salesforceb2b):
    @mock_salesforceb2b('/services/oauth2/token')
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
            status=200,
        )

    return _handler


@pytest.fixture
def mock_trust_bindings(mock_yb_trust_payments):
    @mock_yb_trust_payments('/bindings')
    async def _handler(request):
        return web.json_response(
            {
                'status': 'success',
                'purchase_token': 'faccc93b62950ad7c5ec199d627d806',
            },
            status=200,
        )

    return _handler


@pytest.fixture
def mock_trust_bindings_start(mock_yb_trust_payments):
    @mock_yb_trust_payments('/bindings/faccc93b62950ad7c5ec199d627d806/start')
    async def _handler(request):
        return web.json_response(
            {'status': 'success', 'binding_url': 'aaa'}, status=200,
        )

    return _handler


@pytest.fixture
def mock_ext_balance_invoice_pdf(mock_ext_yandex_balance):
    @mock_ext_yandex_balance('/httpapitvm/get_invoice_from_mds')
    async def _handler(request):
        return web.json_response(
            {
                'mds_link': (
                    'http://s3.mdst.yandex.net/balance/invoices_d7.pdf'
                ),
                'content_type': 'application/pdf',
                'filename': 'Б-1593066-2.pdf',
            },
            status=200,
        )

    return _handler


@pytest.fixture
def mock_corp_edo(mockserver):
    @mockserver.handler('/corp-edo/v1/invitations')
    async def _handler(request):
        client_id = request.query['client_id']
        return web.json_response(
            {
                'invitations': [
                    {
                        'services': 'taxi',
                        'edo_accepted': CLIENT_ID_TO_EDO_ACCEPTED.get(
                            client_id, False,
                        ),
                        'client_id': client_id,
                        'created_at': '2020-11-11 12:12:12',
                        'synced_at': '2020-11-11 12:12:12',
                        'updated_at': '2020-11-11 12:12:12',
                        'created_by_corp_edo': True,
                        'id': '111',
                        'inn': '111111111',
                        'operator': 'sbis',
                        'organization': 'taxi',
                        'status': 'FRIENDS',
                    },
                ],
            },
            status=200,
        )

    return _handler
