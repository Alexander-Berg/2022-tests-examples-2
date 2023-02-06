# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable
import dataclasses

from aiohttp import web
from lxml import etree
import pytest

import corp_requests.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
pytest_plugins = ['corp_requests.generated.service.pytest_plugins']


@pytest.fixture
def mock_mds(mockserver):
    @mockserver.json_handler(r'/mds/get-taxi/', prefix=True)
    def redirect(request):
        if request.query.get('redirect') == 'yes':
            return mockserver.make_response(
                '',
                status=302,
                headers={
                    'Location': (
                        '//mds.yandex.net/get-taxi/group/key?sign=sign'
                    ),
                },
            )
        return mockserver.make_response(
            '598/725bb76df6fb42b191a1db00dd9b275e', status=200,
        )

    @mockserver.json_handler(r'/mds/upload-taxi', prefix=True)
    def upload(request):
        return mockserver.make_response(
            """<?xml version="1.0" encoding="utf-8"?>
<post obj="namespace.filename" id="123" groups="3" size="100" key="key">
</post>""",
            status=200,
        )


@pytest.fixture
def mock_personal(request, load_json):
    marker = request.node.get_closest_marker('personal_data')
    if not marker:
        request.node.add_marker(
            pytest.mark.personal_data(load_json('personal_data.json')),
        )


@pytest.fixture
def mock_personal_random_gen_login(mockserver, load_json):
    pd_data = load_json('personal_data.json')

    @mockserver.json_handler(
        r'/personal/v1/(?P<data_type>\w+)/store', regex=True,
    )
    def mock_store(request, data_type):
        for item in pd_data[data_type]:
            if item['value'] == request.json['value']:
                return item

        # crunch for randomly generated
        if data_type == 'yandex_logins':
            return {'id': 'pd_id', 'value': 'qwerty@gmail.com'}

        return mockserver.make_response(status=404)


@pytest.fixture
def territories_mock(mockserver):
    @mockserver.json_handler('/territories/v1/countries/retrieve')
    def _find(request):
        return {'country': 'rus', 'region_id': 'kek'}


@pytest.fixture
def mock_zaiper_add_org(mock_zapier):
    @mock_zapier('/hooks/catch/123/abc')
    async def _handler(request):
        return web.json_response({'success': 'true'}, status=200)

    return _handler


@pytest.fixture
def blackbox_mock(mockserver):
    class BlackboxMock:
        count_ = 0

        @staticmethod
        @mockserver.json_handler('/blackbox/blackbox')
        async def passport(request):
            method = request.query.get('method', '')

            if method == 'userinfo':
                return {'users': [{}]}

            return {}

    return BlackboxMock()


@pytest.fixture
def mock_passport_internal(mockserver):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/account/register/by_middleman/',
    )
    def register(request):
        return {'status': 'ok', 'uid': '12345'}

    return register


@pytest.fixture
def mock_sender(mockserver):
    @mockserver.json_handler(
        r'/sender/api/0/(?P<account_slug>\w+)/transactional'
        r'/(?P<campaign_slug>\w+)/send',
        regex=True,
    )
    def send(request, account_slug, campaign_slug):
        return {}


@pytest.fixture
def mock_captcha(mockserver):
    class CaptchaAnswers:
        @staticmethod
        def make_ok_response():
            element = etree.Element('image_check')
            element.text = 'ok'
            response = etree.tostring(element)
            return response

        @staticmethod
        def make_not_found_response():
            element = etree.Element('image_check')
            element.text = 'failed'
            element.set('error', 'not found')
            response = etree.tostring(element)
            return response

        @staticmethod
        def make_doesnt_match_response():
            element = etree.Element('image_check')
            element.text = 'failed'
            response = etree.tostring(element)
            return response

        @staticmethod
        def make_inconsistent_type_response():
            element = etree.Element('image_check')
            element.text = 'failed'
            element.set('error', 'inconsistent type')
            response = etree.tostring(element)
            return response

    @mockserver.handler('/captcha/check')
    def check(request):
        data = request.args
        if data['rep'] == 'captcha_value':
            response = CaptchaAnswers.make_ok_response()
        else:
            response = CaptchaAnswers.make_doesnt_match_response()
        return mockserver.make_response(response, status=200)


@pytest.fixture
def mock_corp_admin(mockserver):
    @mockserver.json_handler('/corp-admin/v1/suggest/login')
    def mock_suggest_login(request):
        return mockserver.make_response(
            json={'login': 'new_login'}, status=200,
        )

    @mockserver.json_handler('/corp-admin/v1/register')
    def mock_register(request):
        return mockserver.make_response(
            json={'login': 'new_login', 'password': 'P@ssw0rd'}, status=200,
        )


@pytest.fixture
def mock_staff(mockserver):
    @mockserver.json_handler('/staff/v3/persons')
    async def get_persons(request):
        return mockserver.make_response(
            json={'status': 'ok', 'uid': '12345'}, status=200,
        )


@pytest.fixture
def mock_dadata_suggestions(mockserver):
    class MockDadata:
        @dataclasses.dataclass
        class DadataSuggestionsData:
            suggest_response: dict
            find_by_id_response: dict

        data = DadataSuggestionsData(
            suggest_response={'suggestions': []},
            find_by_id_response={'suggestions': []},
        )

        @staticmethod
        @mockserver.json_handler(
            '/dadata-suggestions/suggestions/api/4_1/rs/findById/party',
        )
        async def find_by_id(request):
            if MockDadata.data.find_by_id_response:
                return mockserver.make_response(
                    json=MockDadata.data.find_by_id_response, status=200,
                )
            return mockserver.make_response(json={}, status=404)

    return MockDadata()


@pytest.fixture
def mock_corp_clients(mockserver):
    class MockCorpClients:
        @dataclasses.dataclass
        class CorpClientsData:
            get_client_response: dict
            create_client_response: dict
            get_contracts_response: dict
            get_services_response: dict
            get_service_response: dict
            sf_managers_response: dict
            clients_list: dict

        data = CorpClientsData(
            get_client_response={},
            create_client_response={'id': 'client_id'},
            get_contracts_response={},
            get_services_response={},
            get_service_response={'is_active': True},
            sf_managers_response={},
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
        @mockserver.json_handler('/corp-clients/v1/clients')
        async def clients(request):
            if request.method == 'GET':
                if MockCorpClients.data.get_client_response:
                    return mockserver.make_response(
                        json=MockCorpClients.data.get_client_response,
                        status=200,
                    )
                return mockserver.make_response(
                    json={'message': 'client-not-found'}, status=404,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/clients/create')
        async def create_client(request):
            if request.method == 'POST':
                return mockserver.make_response(
                    json=MockCorpClients.data.create_client_response,
                    status=200,
                )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/clients/list')
        async def clients_list(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.clients_list, status=200,
                )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/clients/list/accurate')
        async def clients_list_accurate(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.clients_list, status=200,
                )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/contracts')
        async def get_contracts(request):
            return mockserver.make_response(
                json=MockCorpClients.data.get_contracts_response, status=200,
            )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/contracts/settings/update')
        def update_contract_settings(request):
            return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/services')
        async def get_services(request):
            return mockserver.make_response(
                json=MockCorpClients.data.get_services_response, status=200,
            )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/taxi')
        async def service_taxi(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_response, status=200,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/cargo')
        async def service_cargo(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_response, status=200,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/drive')
        async def service_drive(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_response, status=200,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/eats')
        async def service_eats(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_response, status=200,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/eats2')
        async def service_eats2(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_response, status=200,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/market')
        async def service_market(request):
            return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/tanker')
        async def service_tanker(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_response, status=200,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/sf/managers')
        def get_sf_managers(request):
            return mockserver.make_response(
                json=MockCorpClients.data.sf_managers_response, status=200,
            )

    return MockCorpClients()
