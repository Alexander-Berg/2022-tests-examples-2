import datetime
import json

import bson
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from ivr_dispatcher_plugins import *  # noqa: F403 F401

from tests_ivr_dispatcher import utils


CARRIER_INFO = {
    'name': 'Иван',
    'address': '123456, Варшавское шоссе',
    'work_hours': '11-13',
    'type': 'carrier_permit_owner',
    'entity_id': 'id1',
}

PARK_INFO = {
    'name': 'Ромашка',
    'address': '12345678, Рязанское шоссе',
    'work_hours': '9-18',
    'type': 'park',
    'entity_id': 'id2',
}


_NOW_DATE = datetime.date(year=2007, month=1, day=1)


def regular_operator(number):
    return {
        'id': 1000 + number,
        'login': f'operator_{number:03}',
        'agent_id': f'1000000{number:03}',
        'state': 'ready',
        'callcenter_id': ('volgograd_cc' if number % 2 else 'krasnodar_cc'),
        'full_name': 'some_full_name',
        'yandex_uid': f'461{number:03}',
        'queues': [],
        'role_in_telephony': (
            'ru_disp_operator' if number % 4 else 'ru_disp_team_leader'
        ),
        'supervisor_login': f'operator_{1 + number % 2}',
        'employment_date': _NOW_DATE.isoformat(),
    }


OPERATORS = [
    {
        'id': 1,
        'login': 'operator_1',
        'agent_id': '111',
        'state': 'ready',
        'callcenter_id': 'volgograd_cc',
        'full_name': 'some_full_name',
        'yandex_uid': '1001',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 2,
        'login': 'operator_2',
        'agent_id': '222',
        'state': 'ready',
        'callcenter_id': 'krasnodar_cc',
        'full_name': 'some_full_name',
        'yandex_uid': '1002',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 3,
        'login': 'operator_no_calls',
        'agent_id': 'no_calls_id',
        'state': 'ready',
        'callcenter_id': 'volgograd_cc',
        'full_name': 'some_full_name',
        'yandex_uid': '1003',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 4,
        'login': 'operator_no_agent_id',
        'agent_id': None,
        'state': 'ready',
        'callcenter_id': 'krasnodar_cc',
        'full_name': 'some_full_name',
        'yandex_uid': '1004',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 1111,
        'login': 'operator_111',
        'agent_id': '1000000111',
        'state': 'deleted',
        'callcenter_id': 'volgograd_cc',
        'full_name': 'some_full_name',
        'yandex_uid': '1111111',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 1111,
        'login': 'operator_111',
        'agent_id': '1000000111',
        'state': 'deleted',
        'callcenter_id': 'volgograd_cc',
        'full_name': 'some_full_name',
        'yandex_uid': 'some_operator_uid',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'employment_date': _NOW_DATE.isoformat(),
    },
] + [regular_operator(i) for i in range(1, 19)]


@pytest.fixture(name='mock_int_authproxy')
def mock_int_authproxy(mockserver):
    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _mock_profile(request, *args, **kwargs):
        assert 'sourceid' not in request.json
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == 'call_center'
        assert 'user' in request.json
        assert 'personal_phone_id' in request.json['user']
        return {
            'dont_ask_name': False,
            'experiments': [],
            'name': 'Name',
            'personal_phone_id': request.json['user']['personal_phone_id'],
            'user_id': utils.DEFAULT_USER_ID,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/draft')
    def _mock_draft(request, *args, **kwargs):
        assert 'sourceid' not in request.json
        assert 'callcenter' in request.json
        assert 'comment' in request.json
        assert 'key' not in request.json['callcenter']
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {'orderid': utils.DEFAULT_ORDER_ID}

    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                },
            ],
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def _mock_commit(request, *args, **kwargs):
        assert 'sourceid' not in request.json
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == 'call_center'
        assert request.json['orderid'] == utils.DEFAULT_ORDER_ID
        assert request.json['userid'] == utils.DEFAULT_USER_ID
        return {'orderid': utils.DEFAULT_ORDER_ID, 'status': 'some'}

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _mock_estimate(request, *args, **kwargs):
        assert 'sourceid' not in request.json
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == 'call_center'
        assert len(request.json.get('route', [])) > 1
        offer = {
            'offer': 'c9e8879792bc595eecc7b5ddb4f4b8a6',
            'is_fixed_price': True,
            'service_levels': [
                {
                    'class': 'econom',
                    'cost_message_details': {
                        'cost_breakdown': [
                            {
                                'display_amount': '1141 руб., ~73 мин в пути',
                                'display_name': 'cost',
                            },
                        ],
                    },
                    'details_tariff': [
                        {'type': 'price', 'value': 'от 90 руб.'},
                        {
                            'type': 'comment',
                            'value': 'включено 1 мин., далее 2 руб./мин.',
                        },
                        {
                            'type': 'comment',
                            'value': 'включено 1 км, далее 11 руб./км',
                        },
                    ],
                    'estimated_waiting': {'message': 'Мало свободных машин'},
                    'price': '363 руб.',
                    'price_raw': 363,
                    'time': '73 мин',
                    'time_raw': 73,
                },
            ],
            'currency_rules': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
        }
        if request.json.get('route', [])[1] == [11.00, 33.00]:
            offer['service_levels'][0]['price_raw'] = 3000
            return offer
        return offer


@pytest.fixture(name='mock_clck')
def mock_clck(mockserver):
    class MockClck:
        @staticmethod
        @mockserver.handler('/clck_simple/--')
        def click_simple(request):
            return mockserver.make_response('clck_url')

        @staticmethod
        @mockserver.handler('/clck/--')
        def click(request):
            return mockserver.make_response(
                json.dumps(['clck_url', True]), status=200,
            )

    return MockClck


@pytest.fixture(name='mock_order_core')
async def mock_order_core(mockserver, load_json):
    class MockOrderCore:
        @staticmethod
        @mockserver.json_handler('/order-core/v1/tc/order-fields')
        def order_core(request):
            response = load_json('order_core_default_response.json')
            return response

    return MockOrderCore()


@pytest.fixture(name='mock_user_api')
def mock_user_api(mockserver, load_json):
    class MockUserApi:
        @staticmethod
        @mockserver.json_handler('/user-api/user_phones')
        def _user_phones(request):
            assert request.json['validate_phone'] is True
            assert request.json['type'] == 'yandex'
            assert 'phone' in request.json
            phone = request.json['phone']
            response = load_json('user_api_user_phones_response.json')
            response['id'] = '{}_up_id'.format(phone)
            response['personal_phone_id'] = '{}_id'.format(phone)
            response['phone'] = phone
            return response

        @staticmethod
        @mockserver.json_handler('/user-api/v2/user_phones/get')
        async def retrieve_personal_id(request):
            data = request.json
            assert data['id'] == utils.DEFAULT_PHONE_ID
            return {
                'id': str(utils.DEFAULT_PHONE_ID),
                'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
            }

        @staticmethod
        @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve')
        async def retrieve_phone_id_by_personal(request):
            data = request.json
            assert data['personal_phone_id'] == utils.DEFAULT_PERSONAL_PHONE_ID
            assert data['type'] == 'yandex'
            return {
                'id': utils.DEFAULT_PHONE_ID,
                'phone': utils.DEFAULT_USER_PHONE,
                'type': 'yandex',
                'is_taxi_staff': False,
                'is_yandex_staff': False,
                'is_loyal': False,
                'stat': {
                    'total': 0,
                    'big_first_discounts': 0,
                    'complete': 0,
                    'complete_card': 0,
                    'complete_apple': 0,
                    'complete_google': 0,
                    'fake': 0,
                },
            }

        @staticmethod
        @mockserver.json_handler('/user-api/users/search')
        def users_search(request):
            application = (
                ['call_center', 'callcenter']
                if utils.DEFAULT_APPLICATION == 'call_center'
                else utils.DEFAULT_APPLICATION
            )
            assert request.json['applications'] == application

            assert request.json['phone_ids'] == [utils.DEFAULT_PHONE_ID]
            return {
                'items': [
                    {
                        'id': utils.DEFAULT_USER_ID,
                        'created': '2020-08-19T13:30:44.388+0000',
                        'updated': '2020-08-19T13:30:44.4+0000',
                        'phone_id': utils.DEFAULT_PHONE_ID,
                        'application': utils.DEFAULT_APPLICATION,
                        'application_version': '1',
                    },
                ],
            }

    return MockUserApi()


@pytest.fixture(name='mock_parks')
def mock_parks(mockserver):
    class MockParks:
        @staticmethod
        @mockserver.json_handler('/parks/cars/legal-entities')
        async def legal_entities(request):
            return {'legal_entities': [CARRIER_INFO, PARK_INFO]}

    return MockParks()


@pytest.fixture(name='mock_personal_phones')
def mock_personal_phones(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_retrieve(request, *args, **kwargs):
        p_id = request.json['id']
        return mockserver.make_response(
            json={'id': p_id, 'value': p_id.replace('_id', '')}, status=200,
        )

    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_store(request, *args, **kwargs):
        assert request.json['validate'] is True
        return mockserver.make_response(
            json={
                'id': request.json['value'] + '_id',
                'value': request.json['value'],
            },
            status=200,
        )


@pytest.fixture()
def mock_personal(mockserver):
    class MockPersonal:
        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/retrieve')
        async def phones_retrieve(request):
            data = request.json
            if data['id'] == utils.DEFAULT_PERSONAL_PHONE_ID:
                return {'id': data['id'], 'value': utils.DEFAULT_USER_PHONE}
            if data['id'] == utils.DEFAULT_DRIVER_PERSONAL_PHONE_ID:
                return {'id': data['id'], 'value': utils.DEFAULT_DRIVER_PHONE}
            raise NotImplementedError()

        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/store')
        def _mock_store(request, *args, **kwargs):
            assert request.json['validate'] is True
            assert request.json['value'] == utils.DEFAULT_USER_PHONE
            return mockserver.make_response(
                json={
                    'id': utils.DEFAULT_PERSONAL_PHONE_ID,
                    'value': request.json['value'],
                },
                status=200,
            )

    return MockPersonal()


@pytest.fixture()
def mock_octonode(mockserver):
    class MockOctonode:
        @staticmethod
        @mockserver.json_handler('/octonode', prefix=True)
        async def octonode(request):
            data = request.json
            if data.get('session_id'):
                return {'session_id': data['session_id']}
            return {'session_id': 'mocked_session_id'}

    return MockOctonode()


@pytest.fixture()
async def mock_tanya(mockserver):
    class MockTanya:
        @staticmethod
        @mockserver.json_handler('/tanya-telephony/create_leg')
        def tanya(request):
            req_data = request.json
            assert 'session_id' in req_data
            return {
                'session_id': req_data.get('session_id', 'mocked_session_id'),
            }

    return MockTanya()


@pytest.fixture()
def mock_fleet_vehicles(mockserver):
    class MockFleetVehicles:
        @staticmethod
        @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
        async def retrieve(request):
            data = request.json
            return {
                'vehicles': [
                    {
                        'park_id_car_id': data['id_in_set'][0],
                        'data': {
                            'number': 'A666MP77',
                            'number_normalized': 'A666MP77',
                            'brand': 'Audi',
                            'model': 'A8',
                            'color': 'синий',
                        },
                    },
                ],
            }

    return MockFleetVehicles()


@pytest.fixture()
def mock_fleet_parks(mockserver):
    class MockFleetParks:
        @staticmethod
        @mockserver.json_handler('/fleet-parks/v1/parks/contacts/retrieve')
        async def retrieve(request):
            return {
                'description': 'my park description',
                'passengers': {'phone': '+123'},
            }

    return MockFleetParks()


@pytest.fixture(autouse=True)
def mock_cars_catalog(mockserver):
    class MockCarsCatalog:
        @staticmethod
        @mockserver.json_handler('cars-catalog/api/v1/cars/get_colors')
        def get_colors(request):
            data = {
                'items': [
                    {
                        'data': {
                            'raw_color': 'синий',
                            'normalized_color': 'Синий',
                            'color_code': 'FFFFFF',
                        },
                        'revision': 1,
                    },
                ],
            }
            return mockserver.make_response(200, json=data)

    return MockCarsCatalog()


@pytest.fixture
def mock_tariffs(mockserver):
    class MockTariffs:
        @staticmethod
        @mockserver.json_handler(
            '/taxi-tariffs/v1/tariff/by_category', prefix=True,
        )
        async def get_tariff_by_category(request):
            return {
                'home_zone': 'moscow',
                'date_from': '2020-01-01T00:00:00.000Z',
                'categories': [
                    {
                        'id': utils.DEFAULT_TARIFF_CATEGORY_ID,
                        'category_name': 'econom',
                        'category_type': 'application',
                        'time_from': '00:00',
                        'time_to': '23:59',
                        'waiting_included': 5,
                        'name_key': 'some_val',
                        'category_name_key': 'some_val',
                        'day_type': 2,
                        'currency': 'RUB',
                        'included_one_of': [],
                        'minimal': 49.0,
                        'paid_cancel_fix': 100.0,
                        'add_minimal_to_paid_cancel': True,
                        'meters': [],
                        'special_taximeters': [
                            {
                                'zone_name': 'moscow',
                                'price': {
                                    'time_price_intervals': [
                                        {'begin': 0.0, 'price': 0.5},
                                    ],
                                    'time_price_intervals_meter_id': 0,
                                    'distance_price_intervals': [
                                        {'begin': 0.0, 'price': 2.0},
                                    ],
                                    'distance_price_intervals_meter_id': 0,
                                },
                            },
                        ],
                        'zonal_prices': [
                            {
                                'source': 'moscow',
                                'destination': 'dme',
                                'route_without_jams': False,
                                'price': {
                                    'time_price_intervals': [
                                        {'begin': 0.0, 'price': 1.0},
                                    ],
                                    'time_price_intervals_meter_id': 0,
                                    'distance_price_intervals': [
                                        {'begin': 0.0, 'price': 3.0},
                                    ],
                                    'distance_price_intervals_meter_id': 0,
                                },
                            },
                        ],
                    },
                ],
            }

    return MockTariffs()


@pytest.fixture(autouse=True)
def cars_catalog_request(mockserver):
    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_brand_models')
    def _mock_brand_models(request):
        assert request.method == 'GET'
        data = {
            'items': [
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'BMW',
                        'raw_model': 'X2',
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': 'X2',
                        'corrected_model': 'BMW X2',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'BMW',
                        'raw_model': 'X5',
                        'normalized_mark_code': 'BMW',
                        'normalized_model_code': 'X5',
                        'corrected_model': 'BMW X5',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'Audi',
                        'raw_model': 'A5',
                        'normalized_mark_code': 'AUDI',
                        'normalized_model_code': 'A5',
                        'corrected_model': 'Audi A5',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'Audi',
                        'raw_model': 'A8',
                        'normalized_mark_code': 'AUDI',
                        'normalized_model_code': 'A8',
                        'corrected_model': 'Audi A8',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'Газель',
                        'raw_model': 'Next',
                        'normalized_mark_code': 'Газель',
                        'normalized_model_code': 'Next',
                        'corrected_model': 'Газель Next',
                    },
                },
                {
                    'revision': 0,
                    'data': {
                        'raw_brand': 'Kia',
                        'raw_model': 'Rio',
                        'normalized_mark_code': 'Kia',
                        'normalized_model_code': 'Rio',
                        'corrected_model': 'Kia Rio',
                    },
                },
            ],
        }
        return mockserver.make_response(response=json.dumps(data))


@pytest.fixture
def mock_ucommunications(mockserver):
    class MockUcommunications:
        @staticmethod
        @mockserver.json_handler('/ucommunications/user/sms/send', prefix=True)
        async def send_sms(request):
            return {'code': 'code', 'message': 'message'}

    return MockUcommunications()


@pytest.fixture
def mock_callcenter_qa(mockserver):
    class MockCallcenterQa:
        support_ratings = []

        @staticmethod
        def reset_db():
            MockCallcenterQa.support_ratings = []

        @staticmethod
        @mockserver.json_handler('/callcenter-qa/v1/rating/save', prefix=True)
        async def handle(request):
            rating = request.json.get('rating')
            call_guid = request.json['call_guid']
            MockCallcenterQa.support_ratings.append(
                (datetime.datetime.utcnow(), rating, call_guid),
            )
            return {}

    return MockCallcenterQa()


@pytest.fixture(name='mock_callcenter_operators_list', autouse=True)
def _mock_callcenter_operators_list(mockserver):
    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _operators_list(request):
        ops = [
            {
                'id': op['id'],
                'login': op['login'],
                'yandex_uid': op['yandex_uid'],
                'agent_id': op['agent_id'],
                'state': op['state'],
                'first_name': 'name',
                'last_name': 'surname',
                'callcenter_id': op['callcenter_id'],
                'roles': [op['role_in_telephony']],
                'name_in_telephony': op['login'],
                'created_at': '2016-06-01T22:05:25Z',
                'updated_at': '2016-06-22T22:05:25Z',
                'supervisor_login': op.get('supervisor_login'),
                'employment_date': op.get('employment_date'),
                'roles_info': [
                    {'role': 'ru_disp_operator', 'source': 'admin'},
                ],
            }
            for op in OPERATORS
        ]
        return mockserver.make_response(
            status=200, json={'next_cursor': len(OPERATORS), 'operators': ops},
        )


@pytest.fixture(name='cargo_support_flow_store')
def mock_cargo_sup_flow_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_store(request):
        assert request.json['validate'] is True
        assert request.json['value'] == utils.DEFAULT_USER_PHONE
        return mockserver.make_response(
            json={
                'id': utils.DEFAULT_PERSONAL_PHONE_ID,
                'value': request.json['value'],
            },
            status=200,
        )


@pytest.fixture(name='cargo_support_flow_statuses')
def mock_cargo_sup_flow_statuses(mockserver):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _mock_driver_status(request):
        driver = request.json['driver_ids'][-1]
        return {
            'statuses': [
                {
                    'status': 'offline',
                    'park_id': driver['park_id'],
                    'driver_id': driver['driver_id'],
                    'orders': [
                        {
                            'id': utils.DEFAULT_ALIAS_ID,
                            'status': 'transporting',
                        },
                    ],
                },
            ],
        }


@pytest.fixture(name='cargo_support_flow_order_core')
def mock_cargo_sup_flow_order_core(mockserver):
    def mock(tariff_class, nearest_zone):
        @mockserver.json_handler(
            '/order-core/internal/processing/v1/order-proc/get-fields',
        )
        def _mock_order_core(request):
            assert request.content_type == 'application/bson'
            assert request.query['order_id'] == utils.DEFAULT_ALIAS_ID
            assert request.query['require_latest']
            return mockserver.make_response(
                status=200,
                content_type='application/bson',
                response=bson.BSON.encode(
                    {
                        'document': {
                            'processing': {'version': 19},
                            '_id': utils.DEFAULT_ORDER_ID,
                            'order': {
                                'performer': {
                                    'tariff': {'class': tariff_class},
                                },
                                'nz': nearest_zone,
                                'version': 10,
                            },
                        },
                        'revision': {
                            'order.version': 10,
                            'processing.version': 19,
                        },
                    },
                ),
            )

    return mock
