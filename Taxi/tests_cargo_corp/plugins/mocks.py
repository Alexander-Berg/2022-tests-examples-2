import pytest

from tests_cargo_corp import utils


class BasicMock:
    def __init__(self):
        self.response_code = None
        self.response_json = None

        self.default_responses = {}

        self.expected_data = {}

    def set_response_by_code(self, response_code):
        self.response_code = response_code
        self.response_json = self.default_responses.get(
            response_code, utils.BAD_RESPONSE,
        )

    def set_response(self, response_code=200, response_json=None):
        self.response_code = response_code
        self.response_json = response_json

    def get_response(self):
        if self.response_code is None:
            self.set_response_by_code(response_code=200)
        return {'code': self.response_code, 'json': self.response_json}

    def set_expected_data(self, data):
        self.expected_data = data

    def get_expected_data(self):
        return self.expected_data


@pytest.fixture(name='personal_mocks', autouse=True)
def _personal_mocks(mockserver):
    class Handlers:
        @staticmethod
        @mockserver.json_handler('/personal/v1/yandex_logins/store')
        def _yandex_logins_store(request):
            return {
                'id': request.json['value'] + '_id',
                'value': request.json['value'],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/yandex_logins/bulk_retrieve')
        def _mock_bulk_retrieve_yandex_logins(request):
            return {
                'items': [
                    {
                        'id': x['id'],
                        'value': x['id'][:-3] if len(x['id']) > 3 else '',
                    }
                    for x in request.json['items']
                ],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/yandex_logins/retrieve')
        def _yandex_logins_retrieve(request):
            pd_id = request.json['id']
            return {'id': pd_id, 'value': pd_id[:-3] if len(pd_id) > 3 else ''}

        @staticmethod
        @mockserver.json_handler('/personal/v1/emails/store')
        def _emails_store(request):
            return {
                'id': request.json['value'] + '_id',
                'value': request.json['value'],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/store')
        def _phones_store(request):
            return {
                'id': request.json['value'] + '_id',
                'value': request.json['value'],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/bulk_store')
        def _mock_bulk_store_phones(request):
            return {
                'items': [
                    {'id': x['value'] + '_id', 'value': x['value']}
                    for x in request.json['items']
                ],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/emails/bulk_store')
        def _mock_bulk_store_emails(request):
            return {
                'items': [
                    {'id': x['value'] + '_id', 'value': x['value']}
                    for x in request.json['items']
                ],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
        def _mock_bulk_retrieve_phones(request):
            return {
                'items': [
                    {
                        'id': x['id'],
                        'value': x['id'][:-3] if len(x['id']) > 3 else '',
                    }
                    for x in request.json['items']
                ],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/retrieve')
        def _mock_retrieve_phone(request):
            pd_id = request.json['id']
            return {'id': pd_id, 'value': pd_id[:-3] if len(pd_id) > 3 else ''}

        @staticmethod
        @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
        def _mock_bulk_retrieve_emails(request):
            return {
                'items': [
                    {
                        'id': x['id'],
                        'value': x['id'][:-3] if len(x['id']) > 3 else '',
                    }
                    for x in request.json['items']
                ],
            }

        @staticmethod
        @mockserver.json_handler('/personal/v1/emails/retrieve')
        def _emails_retrieve(request):
            pd_id = request.json['id']
            return {'id': pd_id, 'value': pd_id[:-3] if len(pd_id) > 3 else ''}

    return Handlers()


@pytest.fixture(name='feeds_prepare')
def _feeds_prepare(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses[200] = {
                'polling_delay': 10,
                'etag': 'test_etag',
                'feed': [
                    {
                        'feed_id': 'test_feed_id',
                        'created': '2017-04-04T15:32:22+0110',
                        'request_id': 'request_id',
                        'payload': {'additionalProperty1': 1},
                    },
                ],
                'has_more': False,
            }
            self.default_responses[304] = {}
            self.expected_channels = None

        def set_expected_channels(self, expected_channels):
            self.expected_channels = expected_channels

        def get_expected_channels(self):
            return self.expected_channels

        def set_feed(self, feed: list):
            self.default_responses[200]['feed'] = feed

        @property
        def times_called(self):
            return _feeds_v1_fetch_handler.times_called

    context = Context()

    @mockserver.json_handler('feeds/v1/fetch')
    def _feeds_v1_fetch_handler(request):
        assert request.json['service'].startswith('cargo-corp-')

        context_expected_channels = context.get_expected_channels()
        if context_expected_channels:
            channels_in_request = set(request.json['channels'])
            expected_channels = set(context_expected_channels)
            assert channels_in_request == expected_channels

        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='blackbox')
def _blackbox(mockserver):
    class Context:
        def __init__(self):
            self.request_args = {
                'aliases': 'all',
                'dbfields': 'subscription.suid.669',
                'format': 'json',
                'method': 'user_ticket',
                'getphones': 'bound',
                'phone_attributes': '102,108',
            }
            self.response = {
                'users': [
                    {
                        'id': '123',
                        'uid': {'value': '123'},
                        'login': 'my-test',
                        'phones': [
                            {
                                'id': '45588690',
                                'attributes': {
                                    '102': '0987654321',
                                    '108': '1',
                                },
                            },
                            {
                                'id': '45588691',
                                'attributes': {
                                    '102': '12345678910',
                                    '105': '1',
                                },
                            },
                        ],
                    },
                ],
            }

        def set_response(self, response):
            self.response = response

        def get_response(self):
            return self.response

        def set_request_args(self, args):
            self.request_args = args

        def get_request_args(self):
            return self.request_args

    context = Context()

    @mockserver.json_handler('/blackbox')
    def _blackbox(request):
        assert dict(request.args) == context.request_args
        return context.response

    return context


@pytest.fixture(name='get_cargo_corp_list', autouse=True)
def _corp_list(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses = {
                200: {'corp_clients': []},
                404: {'code': 'not_found', 'message': 'Not found'},
            }

        def set_ok_response(self, corp_clients):
            self.default_responses[200] = {'corp_clients': corp_clients}

        @property
        def times_called(self):
            return _cargo_corp_list_handler.times_called

    context = Context()

    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/employee/corp-client/list',
    )
    def _cargo_corp_list_handler(request):
        assert 'role_name' not in request.query

        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='get_taxi_corp_id', autouse=True)
def _get_taxi_corp_id(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses = {
                200: {'corp_client_id': utils.CORP_CLIENT_ID},
                404: {'code': 'not_found', 'message': 'Not found'},
            }

        @property
        def times_called(self):
            return _taxi_corp_integration_handler.times_called

    context = Context()

    @mockserver.json_handler(
        'taxi-corp-integration/v1/authproxy/corp_client_id',
    )
    def _taxi_corp_integration_handler(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'
        yandex_uid = request.json.get('uid')
        assert yandex_uid

        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='get_taxi_corp_contracts', autouse=True)
def _taxi_corp_contracts(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses = {
                200: {},
                400: {'code': 'bad_request', 'message': 'Bad request'},
                404: {'code': 'not_found', 'message': 'Not found'},
            }
            self.set_contracts(has_contracts=True)

        def set_contracts(
                self,
                has_contracts,
                payment_type='prepaid',
                is_sent=True,
                is_faxed=True,
                is_signed=True,
                is_active=True,
        ):
            if has_contracts:
                self.default_responses[200]['contracts'] = [
                    {
                        'payment_type': payment_type,
                        'contract_id': 5,
                        'external_id': '5',
                        'is_sent': is_sent,
                        'is_faxed': is_faxed,
                        'is_signed': is_signed,
                        'is_active': is_active,
                        'is_offer': True,
                        'currency': 'RUB',
                        'services': [],
                        'balances': {
                            'apx_sum': '0',
                            'balance': '150',
                            'discount_bonus_sum': '0',
                            'receipt_sum': '250',
                            'total_charge': '100',
                        },
                    },
                ]
            else:
                self.default_responses[200]['contracts'] = []

        @property
        def times_called(self):
            return _taxi_corp_contracts_handler.times_called

    context = Context()

    @mockserver.json_handler('/corp-clients-uservices/v1/contracts')
    def _taxi_corp_contracts_handler(request):
        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='get_taxi_corp_info', autouse=True)
def _taxi_corp_info(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses = {
                200: {'id': utils.CORP_CLIENT_ID, 'name': 'Ромашки и цветы'},
                400: {'code': 'bad_request', 'message': 'Bad request'},
                404: {'code': 'not_found', 'message': 'Not found'},
            }

        @property
        def times_called(self):
            return _taxi_corp_info_handler.times_called

    context = Context()

    @mockserver.json_handler('/corp-clients-uservices/v1/clients')
    def _taxi_corp_info_handler(request):
        assert request.args['fields'] == 'name'
        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='get_flow_phoenix_state', autouse=True)
def _flow_phoenix_state(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_passport_account = utils.PASSPORT_ACCOUNT
            self.default_new_ticket_cases = {
                False: {
                    'disable_reason': {
                        'code': 'has_unresolved_tickets',
                        'message': 'Unfinished registration process.',
                        'details': {
                            'ticket_id': (
                                'phoenix:afcc418a22ba449f96c817e48afa4150'
                            ),
                        },
                    },
                },
                True: {'token': 'afcc418a22ba449f96c817e48afa4150'},
            }
            self.default_tickets = [
                {'ticket_id': 'afcc418a22ba449f96c817e48afa4150'},
            ]

        def set_response_details(self, passport_account=None, tickets=None):
            if passport_account is None:
                passport_account = self.default_passport_account
            if tickets is None:
                tickets = self.default_tickets
            new_ticket = self.default_new_ticket_cases[not tickets]

            self.response_code = 200
            self.response_json = {
                'passport_account': passport_account,
                'tickets': tickets,
                'new_ticket': new_ticket,
                'client_events_channels': [
                    {'channel': 'b2bweb:phoenix'},
                    {'channel': 'tariff-editor:phoenix'},
                    {
                        'channel': (
                            'b2bweb:phoenix:'
                            '37860dfe71ca51c379b44d197bc3ec9a2ec1da97'
                        ),
                    },
                    {
                        'channel': (
                            'tariff-editor:'
                            'phoenix:37860dfe71ca51c379b44d197bc3ec9a2ec1da97'
                        ),
                    },
                ],
            }

        def get_response(self):
            if self.response_code is None:
                self.set_response_details()
            return {'code': self.response_code, 'json': self.response_json}

        @property
        def times_called(self):
            return _flow_phoenix_state_handler.times_called

    context = Context()

    @mockserver.json_handler('cargo-crm/b2b/cargo-crm/flow/phoenix/state')
    def _flow_phoenix_state_handler(request):
        assert request.headers['Accept-Language'] == 'ru'
        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='mocked_cargo_tasks')
async def _mocked_cargo_tasks(mockserver):
    class Context:
        def __init__(self):
            self.create_prepay_invoice = BasicMock()
            self.get_public_tariff = BasicMock()
            self.get_client_tariff = BasicMock()

        @property
        def create_prepay_invoice_times_called(self):
            return _create_prepay_invoice.times_called

        @property
        def get_public_tariff_times_called(self):
            return _get_public_tariff.times_called

        @property
        def get_client_tariff_times_called(self):
            return _get_client_tariff.times_called

    context = Context()

    @mockserver.json_handler('/cargo-tasks/v1/billing/create-prepay-invoice')
    async def _create_prepay_invoice(request):
        assert (
            request.json == context.create_prepay_invoice.get_expected_data()
        )
        response = context.create_prepay_invoice.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    @mockserver.json_handler('/cargo-tasks/v1/public/tariff')
    async def _get_public_tariff(request):
        assert request.json == context.get_public_tariff.get_expected_data()
        response = context.get_public_tariff.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    @mockserver.json_handler('/cargo-tasks/v1/client/tariff')
    async def _get_client_tariff(request):
        assert request.json == context.get_client_tariff.get_expected_data()
        response = context.get_client_tariff.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='mocked_cargo_crm')
async def _mocked_cargo_crm(mockserver):
    class Context:
        def __init__(self):
            self.notification_contract_accepted = BasicMock()

        @property
        def notification_contract_accepted_times_called(self):
            return _notification_contract_accepted.times_called

    context = Context()

    @mockserver.json_handler(
        '/cargo-crm/internal/cargo-crm/notification/contract-accepted',
    )
    async def _notification_contract_accepted(request):
        assert (
            request.json
            == context.notification_contract_accepted.get_expected_data()
        )
        response = context.notification_contract_accepted.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='cargo_corp_card_list')
def _cargo_corp_card_list(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses[200] = {
                'bound_cards': [
                    {'card_id': utils.CARD_ID, 'yandex_uid': utils.YANDEX_UID},
                ],
            }

        def set_cards(self, cards):
            self.default_responses[200]['bound_cards'] = cards

        @property
        def times_called(self):
            return _client_card_list.times_called

    context = Context()

    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/card/list',
    )
    def _client_card_list(request):
        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='cargo_corp_client_info')
def _cargo_corp_client_info(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses[200] = utils.CORP_CLIENT_INFO

        @property
        def times_called(self):
            return _client_info_get.times_called

    context = Context()

    @mockserver.json_handler('/cargo-corp/internal/cargo-corp/v1/client/info')
    def _client_info_get(request):
        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


ADMIN_ROLE = {
    'id': utils.OWNER_ROLE,
    'name': utils.OWNER_ROLE,
    'permissions': [{'id': 'perm_id_1', 'name': 'perm_name_1'}],
    'is_removable': False,
    'is_general': True,
}


@pytest.fixture(name='cargo_corp_role_list')
def _cargo_corp_role_list(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses[200] = {'roles': []}

        def set_roles(self, roles):
            self.default_responses[200]['roles'] = roles

        def set_admin_role(self):
            self.set_roles([ADMIN_ROLE])

        @property
        def times_called(self):
            return _client_role_list.times_called

    context = Context()

    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/role/list',
    )
    def _client_role_list(request):
        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(name='cargo_fin_debts_state')
def _cargo_fin_debts_state(mockserver):
    class Context(BasicMock):
        def __init__(self):
            super().__init__()

            self.default_responses[200] = {'has_debts': False, 'actions': {}}

        def set_ok_default(self, has_debts):
            self.default_responses[200]['has_debts'] = has_debts

        @property
        def times_called(self):
            return _debts_state.times_called

    context = Context()

    @mockserver.json_handler('/cargo-finance/b2b/cargo-finance/debts/state')
    def _debts_state(request):
        response = context.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context


@pytest.fixture(autouse=True)
def territories_countries_list(mockserver, load_json):
    @mockserver.json_handler('/territories/v1/countries/list')
    def mock_countries_list(request):
        request.get_data()
        return load_json('countries.json')

    return mock_countries_list


@pytest.fixture(name='mocked_corp_admin')
def _mocked_corp_admin(mockserver):
    class Context:
        def __init__(self) -> None:
            self.assign_tariff_plan = BasicMock()
            self.get_tariff_plans = BasicMock()

    context = Context()

    @mockserver.json_handler('/corp-admin/v1/client-tariff-plans/assign')
    async def _assign_tariff_plan(request):
        expected_data = context.assign_tariff_plan.get_expected_data()
        assert request.json.get('date_from') == expected_data['date_from']
        assert request.json.get('date_to') == expected_data['date_to']

        response = context.assign_tariff_plan.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    @mockserver.json_handler('/corp-admin/v1/client-tariff-plans')
    async def _get_tariff_plans(request):
        response = context.get_tariff_plans.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context
