# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import typing
import urllib

import pytest

from cargo_tariffs_plugins import *  # noqa: F403 F401


@pytest.fixture(name='mock_cargo_reports_csv_to_json')
def _mock_cargo_reports_csv_to_json(mockserver):
    class Context:
        request = None
        response = []
        mock = None
        response_status_code = 200

    ctx = Context()

    @mockserver.json_handler('/cargo-reports/v1/csv/parse-to-json')
    def _mock(request, *args, **kwargs):
        ctx.request = request
        return mockserver.make_response(
            json=ctx.response, status=ctx.response_status_code,
        )

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='mock_cargo_reports_json_to_csv')
def _mock_cargo_reports_json_to_csv(mockserver):
    class Context:
        request = None
        response = []
        mock = None

    ctx = Context()

    @mockserver.json_handler('/cargo-reports/v1/csv/serialize-json')
    def _mock(request, *args, **kwargs):
        ctx.request = request.json
        return ctx.response

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='default_ndd_client_tariff')
def _default_ndd_client_tariff():
    return {
        'type': 'ndd_client_base_prices',
        'delivery': {'intake': '100', 'return_price_pct': '10.5'},
        'parcels': {
            'add_declared_value_pct': '5',
            'weight_prices': [
                {'begin': '0', 'price_per_kilogram': '5.5'},
                {'begin': '2.5', 'price_per_kilogram': '2.5'},
            ],
            'included_weight_price': '13',
        },
    }


@pytest.fixture(name='default_json_to_csv_request')
def _default_json_to_csv_request(default_ndd_client_tariff):
    return {
        'table': [
            {
                'c.employer_id.equal': 'ID работника',
                't.p.type': 't.p.type',
                't.p.delivery.intake': 'Хз что это',
                't.p.delivery.return_price_pct': 'Хз что это',
                't.p.parcels.add_declared_value_pct': 'Хз что это',
                't.p.parcels.weight_prices.0.begin': 'Порог 0',
                't.p.parcels.weight_prices.1.begin': 'Порог 1',
                't.p.parcels.weight_prices.0.price_per_kilogram': 'Цена с 0',
                't.p.parcels.weight_prices.1.price_per_kilogram': 'Цена с 1',
                't.p.parcels.included_weight_price': 'Хз что это',
                't.tariff_status': 'Статус тарифа',
            },
            {
                'c': {'employer_id': {'equal': 'corp_id_1'}},
                't': {
                    'p': default_ndd_client_tariff,
                    'tariff_status': 'active',
                },
            },
        ],
    }


@pytest.fixture(name='zero_ndd_client_tariff')
def _zero_ndd_client_tariff():
    return {
        'type': 'ndd_client_base_prices',
        'delivery': {'intake': '0', 'return_price_pct': '0'},
        'parcels': {
            'add_declared_value_pct': '0',
            'weight_prices': [
                {'begin': '0', 'price_per_kilogram': '0'},
                {'begin': '0', 'price_per_kilogram': '0'},
            ],
            'included_weight_price': '0',
        },
    }


@pytest.fixture(name='v1_tariffs_services_list')
async def _v1_tariffs_services_list(taxi_cargo_tariffs):
    class GroupedServices:
        url = '/cargo-tariffs/admin/v1/services/list'

        async def get(self):
            return await taxi_cargo_tariffs.get(self.url)

    return GroupedServices()


@pytest.fixture(name='v1_services_scheme')
async def _v1_services_scheme(taxi_cargo_tariffs):
    class Services:
        url = '/cargo-tariffs/admin/v1/service/'

        async def get_service_scheme(self, service: str):
            return await taxi_cargo_tariffs.get(
                self.url, params={'service': service},
            )

    return Services()


@pytest.fixture(name='default_drafts_list_response')
def _default_drafts_list_response(default_ndd_client_tariff):
    return [
        {
            'id': 444,
            'version': 1,
            'status': 'need_approval',
            'data': {'document': default_ndd_client_tariff},
        },
    ]


@pytest.fixture(name='mock_drafts_list')
def _mock_drafts_list(mockserver, default_drafts_list_response):
    class DraftsListContext:
        request = None
        with_active_draft = False
        response = None

    ctx = DraftsListContext()

    @mockserver.json_handler('taxi-approvals/drafts/list/')
    def _mock(request, *args, **kwargs):
        change_doc_id = request.json['change_doc_ids'][0]
        ctx.request = request.json
        if ctx.with_active_draft:
            ctx.response = default_drafts_list_response
            ctx.response[0]['change_doc_id'] = change_doc_id
            ctx.response[0]['data']['tariff_id'] = change_doc_id.split('_', 1)[
                1
            ]
        else:
            ctx.response = []
        return ctx.response

    return ctx


@pytest.fixture(name='v1_tariff_creator')
async def _v1_tariff_creator(taxi_cargo_tariffs):
    class Client:
        url = '/cargo-tariffs/admin/v1/tariff/create'
        params = {'service': 'ndd_client'}
        conditions = []

        async def create(self):
            return await taxi_cargo_tariffs.post(
                self.url,
                params=self.params,
                json={'conditions': self.conditions},
            )

    return Client()


@pytest.fixture(name='v1_tariff_retriever')
async def _v1_tariff_retriever(taxi_cargo_tariffs, mock_drafts_list):
    class Client:
        url = '/cargo-tariffs/admin/v1/tariff/retrieve'
        params = {'service': 'ndd_client'}

        async def retrieve(self, tariff_id=None, with_active_draft=False):
            mock_drafts_list.with_active_draft = with_active_draft
            if tariff_id:
                self.params['id'] = tariff_id
            return await taxi_cargo_tariffs.get(self.url, params=self.params)

    return Client()


@pytest.fixture(name='v1_tariff_deleter')
async def _v1_tariff_deleter(taxi_cargo_tariffs):
    class Client:
        url = '/cargo-tariffs/admin/v1/tariff/delete'
        params = {'service': 'ndd_client'}

        async def delete(self, tariff_id=None):
            if tariff_id:
                self.params['id'] = tariff_id
            return await taxi_cargo_tariffs.delete(
                self.url, params=self.params,
            )

    return Client()


@pytest.fixture(name='v1_document_creator')
async def _v1_document_creator(taxi_cargo_tariffs):
    class Client:
        url = '/cargo-tariffs/admin/v1/tariff/add-document'

        async def create(self, tariff_id, document):
            return await taxi_cargo_tariffs.post(
                self.url, json={'tariff_id': tariff_id, 'document': document},
            )

    return Client()


@pytest.fixture(name='default_source_zone_condition')
def _default_source_zone_condition():
    return {'field_name': 'source_zone', 'sign': 'equal', 'value': 'moscow'}


@pytest.fixture(name='insert_tariffs_to_db')
async def _insert_tariffs_to_db(
        pgsql,
        v1_tariff_creator,
        v1_document_creator,
        zero_ndd_client_tariff,
        default_source_zone_condition,
):
    class InsertWrapper:
        conditions = []

        async def insert_dummy(self, intake='0', source_zone='moscow'):
            default_source_zone_condition['value'] = source_zone
            v1_tariff_creator.conditions = [
                *self.conditions,
                default_source_zone_condition,
            ]
            resp = await v1_tariff_creator.create()
            tariff_id = resp.json()['id']
            zero_ndd_client_tariff['delivery']['intake'] = intake
            resp = await v1_document_creator.create(
                tariff_id, zero_ndd_client_tariff,
            )
            document_id = resp.json()['id']
            return tariff_id, document_id

    return InsertWrapper()


@pytest.fixture(name='add_tariff_condition')
def add_tariff_condition_fixture(v1_tariff_creator, taxi_cargo_tariffs):
    async def _inner(conditions: typing.List[dict]):
        v1_tariff_creator.conditions = conditions
        resp = await v1_tariff_creator.create()
        assert resp.status_code == 200
        await taxi_cargo_tariffs.invalidate_caches(clean_update=True)
        return resp.json()['id']

    return _inner


@pytest.fixture(name='add_tariff_document')
def add_tariff_document_fixture(v1_document_creator, taxi_cargo_tariffs):
    async def _inner(tariff_id: str, tariff_document: typing.Dict):
        resp = await v1_document_creator.create(tariff_id, tariff_document)
        assert resp.status_code == 200
        await taxi_cargo_tariffs.invalidate_caches(clean_update=True)

        return resp.json()['id']

    return _inner


@pytest.fixture(name='add_tariff')
def add_tariff_fixture(add_tariff_document, add_tariff_condition):
    async def _inner(conditions: typing.List, document: typing.Dict):
        tariff_id = await add_tariff_condition(conditions=conditions)
        document_id = await add_tariff_document(
            tariff_id=tariff_id, tariff_document=document,
        )

        return tariff_id, document_id

    return _inner


@pytest.fixture(name='add_tariffs')
def add_tariffs_fixture(add_tariff):
    async def _inner(tariffs: typing.List[dict]):
        for tariff in tariffs:
            await add_tariff(
                conditions=tariff['conditions'], document=tariff['document'],
            )

    return _inner


@pytest.fixture(name='fill_db')
def fill_db_fixture(add_tariff):
    async def _inner():
        conditions = [
            {
                'field_name': 'employer_id',
                'sign': 'equal',
                'value': 'corp_id_1',
            },
        ]
        document = {
            'type': 'ndd_client_base_prices',
            'delivery': {'intake': '100', 'return_price_pct': '10.5'},
            'parcels': {
                'add_declared_value_pct': '5',
                'weight_prices': [
                    {'begin': '0', 'price_per_kilogram': '5.5'},
                    {'begin': '2.5', 'price_per_kilogram': '2.5'},
                ],
                'included_weight_price': '13',
            },
        }

        return await add_tariff(conditions=conditions, document=document)

    return _inner


@pytest.fixture(name='v1_admin_csv')
async def _v1_admin_csv(taxi_cargo_tariffs):
    class Client:
        url = '/tariffs/v1/admin/v1/tariff/{operation}/csv'
        params = {'service': 'ndd_client'}

        async def export_csv(self, body):
            url = self.url.format(operation='export')
            return await taxi_cargo_tariffs.post(
                url, params=self.params, json=body,
            )

        async def import_csv(self, body):
            url = self.url.format(operation='import')
            return await taxi_cargo_tariffs.post(
                url,
                params=self.params,
                headers={'Content-Type': 'application/csv'},
                data=body,
            )

    return Client()


@pytest.fixture(name='tariff_json_example')
def _tariff_json_example(default_ndd_client_tariff):
    return [
        {
            'conditions': [
                {
                    'field_name': 'employer_id',
                    'sign': 'equal',
                    'value': '0123456789012345678901234567890a',
                },
                {
                    'field_name': 'source_zone',
                    'sign': 'equal',
                    'value': 'Moscow_CKAD',
                },
                {
                    'field_name': 'destination_zone',
                    'sign': 'equal',
                    'value': 'Moscow_CKAD',
                },
                {
                    'field_name': 'tariff_category',
                    'sign': 'equal',
                    'value': 'interval_with_fees',
                },
            ],
            'document': default_ndd_client_tariff,
        },
        {
            'conditions': [
                {
                    'field_name': 'employer_id',
                    'sign': 'equal',
                    'value': '0123456789012345678901234567890a',
                },
                {
                    'field_name': 'source_zone',
                    'sign': 'equal',
                    'value': 'Moscow_CKAD',
                },
                {
                    'field_name': 'destination_zone',
                    'sign': 'equal',
                    'value': 'Moscow_CKAD',
                },
                {
                    'field_name': 'tariff_category',
                    'sign': 'equal',
                    'value': 'interval_strict',
                },
            ],
            'document': default_ndd_client_tariff,
        },
        {
            'conditions': [
                {
                    'field_name': 'employer_id',
                    'sign': 'equal',
                    'value': '0123456789012345678901234567890a',
                },
                {
                    'field_name': 'source_zone',
                    'sign': 'equal',
                    'value': 'Moscow_CKAD',
                },
                {
                    'field_name': 'destination_zone',
                    'sign': 'equal',
                    'value': 'SPB_KAD',
                },
                {
                    'field_name': 'tariff_category',
                    'sign': 'equal',
                    'value': 'interval_with_fees',
                },
            ],
            'document': default_ndd_client_tariff,
        },
    ]


def default_conditions_order_config():
    return {
        'ndd_client': [
            {
                'condition_group_name': 'client',
                'fields': [{'name': 'employer_id'}],
            },
            {
                'condition_group_name': 'source_geo',
                'fields': [{'name': 'source_zone'}],
            },
            {
                'condition_group_name': 'destination_geo',
                'fields': [{'name': 'destination_zone'}],
            },
            {
                'condition_group_name': 'tariff',
                'fields': [{'name': 'tariff_category'}],
            },
        ],
    }


@pytest.fixture(autouse=True)
def employer_list_cache(mockserver):
    @mockserver.json_handler(
        '/logistic-platform-admin/api/admin/employer/list',
    )
    def _api_admin_employer_list(request):
        return {
            'objects': [
                {
                    'employer_id': '25643',
                    'employer_code': 'employer_code_1',
                    'employer_meta': {
                        'corp_client_id': '0123456789012345678901234567890a',
                    },
                },
                {
                    'employer_id': '87623746',
                    'employer_meta': {
                        'corp_client_id': '09812340981239827394879283749824',
                    },
                },
                {
                    'employer_code': 'corp_id_1',
                    'employer_meta': {
                        'corp_client_id': 'corp_client_with_multiconditions',
                    },
                },
                {'employer_code': '7928374'},
            ],
        }


@pytest.fixture(name='cargo_matcher_tariff_requirements')
def _cargo_matcher_tariff_requirements(mockserver):
    class Context:
        request = None
        response = []
        mock = None
        response_status_code = 200

    ctx = Context()

    @mockserver.json_handler('/cargo-matcher/internal/v1/tariff_requirements')
    def _mock(request, *args, **kwargs):
        ctx.request = request
        ctx.response = {
            'requirements': [
                {
                    'default': False,
                    'name': 'add_req1',
                    'required': True,
                    'text': 'requirement.add_req1.text',
                    'title': 'requirement.add_req1.title',
                    'type': 'bool',
                },
                {
                    'default': True,
                    'name': 'add_req2',
                    'required': False,
                    'text': 'requirement.add_req2.text',
                    'title': 'requirement.add_req2.title',
                    'type': 'bool',
                },
            ],
        }
        return mockserver.make_response(
            json=ctx.response, status=ctx.response_status_code,
        )

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='mock_tariff_settings')
def _mock_tariff_settings(mockserver):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_settings/list')
    def _mock_tariff_setting_list(request):
        params = urllib.parse.parse_qs(request.query_string.decode())
        cursor = params.get('cursor', [''])[0]
        if cursor == 'final':
            return {'zones': [], 'next_cursor': 'final'}
        return {
            'zones': [
                {
                    'categories': [
                        {
                            'can_be_default': True,
                            'card_payment_settings': {
                                'max_compensation': 5000,
                                'max_manual_charge': 5000,
                                'max_refund': 5000,
                            },
                            'charter_contract': True,
                            'client_constraints': [],
                            'client_requirements': [
                                'door_to_door',
                                'cargo_loaders',
                            ],
                            'comments_disabled': False,
                            'disable_ban_for_feedback': False,
                            'disable_destination_change': False,
                            'disable_live_location': False,
                            'disable_zone_leave': False,
                            'driver_change_cost': {},
                            'fixed_price_enabled': True,
                            'free_cancel_timeout': 300,
                            'glued_requirements': [],
                            'is_default': True,
                            'legal_entities_enabled': True,
                            'mark_as_new': False,
                            'max_card_payment': 5000,
                            'max_corp_payment': 5000,
                            'max_route_points_count': 5,
                            'name': 'express',
                            'only_for_soon_orders': False,
                            'persistent_requirements': [
                                'animaltransport',
                                'nosmoking',
                            ],
                            'req_destination': False,
                            'service_levels': [50],
                            'tanker_key': 'name.express',
                            'toll_roads_enabled': False,
                        },
                    ],
                    'home_zone': 'moscow',
                    'timezone': 'Europe/Moscow',
                },
            ],
            'next_cursor': 'final',
        }
