# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from typing import Optional

import pytest

PROFILE_REQUEST = {
    'user': {'personal_phone_id': 'personal_phone_id_1'},
    'name': 'Насруло',
    'sourceid': 'cargo',
}


@pytest.fixture(name='get_default_profile_response')
def get_default_profile_resp():
    return {
        'dont_ask_name': False,
        'experiments': [],
        'name': 'Насруло',
        'personal_phone_id': 'personal_phone_id_1',
        'user_id': 'taxi_user_id_1',
    }


@pytest.fixture(autouse=True)
def mock_profile(mockserver, get_default_profile_response):
    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _profile(request):
        assert request.json == PROFILE_REQUEST
        return get_default_profile_response


@pytest.fixture(name='changedestinations_response')
def default_changedest_resp():
    return {
        'change_id': '3a78e3efbffb4700b8649c109e62b451',
        'name': 'comment ',
        'status': 'success',
        'value': [
            {
                'type': 'address',
                'country': 'Россия',
                'fullname': 'Россия, Москва, 8 Марта, 4',
                'geopoint': [33.1, 52.1],
                'locality': 'Москва',
                'porchnumber': '',
                'premisenumber': '4',
                'thoroughfare': '8 Марта',
            },
        ],
    }


@pytest.fixture(autouse=True)
def mock_nearest_zone(mockserver):
    @mockserver.json_handler('/int-authproxy/v1/nearestzone')
    def _nearestzone(request):
        return {'nearest_zone': 'moscow'}

    return _nearestzone


@pytest.fixture(autouse=True)
def mock_changedestination(mockserver, changedestinations_response):
    @mockserver.json_handler('/int-authproxy/v1/changedestinations')
    def _changedestinations(request):
        return changedestinations_response

    return _changedestinations


@pytest.fixture(name='mock_corp_api', autouse=True)
def _mock_corp_api(mockserver):
    @mockserver.json_handler(
        '/taxi-corp-integration/v1/client_tariff_plan/current',
    )
    def _corp_api(request):
        return {
            'tariff_plan_series_id': 'tariff_plan_id_123',
            'client_id': 'corp_client_id_12312312312312312',
            'date_from': '2020-01-22T15:30:00+00:00',
            'date_to': '2021-01-22T15:30:00+00:00',
            'disable_tariff_fallback': False,
        }


@pytest.fixture(name='mock_tariffs', autouse=True)
def _mock_tariffs(mockserver, load_json):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff/corp/current')
    def _tariffs(request):
        return {
            'id': 'tariff_id',
            'categories': load_json('categories.json'),
            'disable_paid_supply_price': False,
        }


@pytest.fixture(name='get_4_points_route')
def get_4_foints():
    return [
        {
            'id': 100,
            'address': {
                'fullname': '1',
                'coordinates': [1, 2],
                'door_code': '78#12в',
            },
            'contact': {
                'personal_phone_id': 'personal_phone_id_1',
                'personal_email_id': 'personal_email_id_123',
                'name': 'Насруло',
            },
            'type': 'source',
            'visit_order': 1,
            'visit_status': 'pending',
            'visited_at': {},
        },
        {
            'id': 2,
            'address': {
                'fullname': '2',
                'coordinates': [2, 3],
                'comment': 'точка 2',
            },
            'contact': {
                'personal_phone_id': 'personal_phone_id_456',
                'personal_email_id': 'personal_email_id_123',
                'name': 'Vasya',
            },
            'type': 'destination',
            'visit_order': 2,
            'visit_status': 'pending',
            'visited_at': {},
        },
        {
            'id': 3,
            'address': {'fullname': '3', 'coordinates': [3, 4]},
            'contact': {
                'personal_phone_id': 'receiver_phone_id',
                'personal_email_id': 'personal_email_id_123',
                'name': 'Петр',
            },
            'type': 'destination',
            'visit_order': 3,
            'visit_status': 'pending',
            'visited_at': {},
        },
        {
            'id': 4,
            'address': {'fullname': '6', 'coordinates': [4, 5]},
            'contact': {
                'personal_phone_id': 'personal_phone_id_456',
                'personal_email_id': 'personal_email_id_123',
                'name': 'Vasya',
            },
            'type': 'return',
            'visit_order': 4,
            'visit_status': 'pending',
            'visited_at': {},
        },
    ]


@pytest.fixture
def get_default_claim_response():
    return {
        'id': 'test_claim_1',
        'emergency_contact': {
            'name': 'name',
            'personal_phone_id': '+79998887777_id',
        },
        'status': 'accepted',
        'user_request_revision': '123',
        'version': 3,
        'created_ts': '2020-01-27T15:40:00+00:00',
        'updated_ts': '2020-01-27T15:40:00+00:00',
        'corp_client_id': 'corp_client_id_1_______32symbols',
        'taxi_offer': {
            'offer_id': 'taxi_offer_id_1',
            'price_raw': 999,
            'price': '999.0010',
        },
        'pricing': {
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.0010',
            },
            'currency': 'RUB',
        },
        'taxi_requirements': {'cargo_type': 'lcv_m'},
        'matched_cars': [{'taxi_class': 'cargo', 'cargo_type': 'lcv_m'}],
        'items': [
            {
                'id': 13,
                'pickup_point': 1,
                'droppof_point': 2,
                'title': 'cargo_item_1',
                'quantity': 50,
                'weight': 7.0,
                'cost_value': '10.20',
                'cost_currency': 'RUR',
                'size': {'length': 1.0, 'width': 2.0, 'height': 3.0},
            },
        ],
        'route_points': [
            {
                'id': 1,
                'address': {
                    'fullname': 'ул. Лужники, 24, стр. 1',
                    'country': 'Россия',
                    'coordinates': [37.552166, 55.715677],
                    'porch': '4',
                    'floor': 12,
                    'flat': 321,
                    'uri': 'whatever',
                    'door_code': '78#12в',
                },
                'contact': {
                    'personal_phone_id': 'personal_phone_id_1',
                    'personal_email_id': 'personal_email_id_1',
                    'name': 'Насруло',
                },
                'type': 'source',
                'visit_order': 1,
                'visit_status': 'pending',
                'skip_confirmation': False,
                'visited_at': {},
            },
            {
                'id': 2,
                'address': {
                    'fullname': 'МФК Око',
                    'country': 'Россия',
                    'coordinates': [37.534945, 55.749381],
                    'sfloor': '4',
                    'sflat': '1',
                },
                'contact': {
                    'personal_phone_id': 'receiver_phone_id',
                    'name': 'Петр',
                },
                'type': 'destination',
                'visit_order': 2,
                'visit_status': 'pending',
                'skip_confirmation': True,
                'visited_at': {},
            },
            {
                'id': 3,
                'address': {
                    'fullname': 'Возврат товара',
                    'country': 'Россия',
                    'coordinates': [39.534945, 55.749381],
                    'floor': 4,
                    'flat': 1,
                    'sfloor': '4',
                    'sflat': '1',
                },
                'contact': {
                    'personal_phone_id': 'receiver_phone_id',
                    'name': 'Петр',
                },
                'type': 'return',
                'visit_order': 3,
                'visit_status': 'pending',
                'skip_confirmation': True,
                'visited_at': {},
            },
        ],
    }


@pytest.fixture
def get_default_draft_request():
    return {
        'id': 'taxi_user_id_1',
        'cargo_ref_id': 'test_claim_1',
        'class': ['cargo'],
        'corpweb': True,
        'delivery': {'include_rovers': False},
        'extra_contact_phone': 'receiver_phone',
        'extra_passenger_name': 'Петр',
        'payment': {
            'type': 'corp',
            'payment_method_id': 'corp-corp_client_id_1_______32symbols',
        },
        'comment': 'Заказ с подтверждением по СМС.',
        'parks': [],
        'requirements': {'cargo_type': 'lcv_m'},
        'route': [
            {
                'country': 'Россия',
                'fullname': 'ул. Лужники, 24, стр. 1',
                'geopoint': [37.552166, 55.715677],
                'uri': 'whatever',
                'extra_data': {
                    'apartment': '321',
                    'floor': '12',
                    'porch': '4',
                    'doorphone_number': '78#12в',
                    'comment': 'Код от подъезда/домофона: 78#12в.',
                },
            },
            {
                'country': 'Россия',
                'fullname': 'МФК Око',
                'geopoint': [37.534945, 55.749381],
                'extra_data': {'apartment': '1', 'floor': '4'},
            },
        ],
    }


@pytest.fixture(name='mock_blackbox_info', autouse=True)
def _mock_blackbox_info(mockserver, default_courier_demand_multiplier):
    def do_mock(
            courier_demand_multiplier: Optional[
                float
            ] = default_courier_demand_multiplier,
            claims_courier_demand_multiplier: Optional[list] = None,
    ):
        @mockserver.json_handler(
            '/eats-logistics-performer-payouts/v1/blackbox/info',
        )
        def mock(request):
            response = {}
            if courier_demand_multiplier is not None:
                response[
                    'courier_demand_multiplier'
                ] = courier_demand_multiplier
            if claims_courier_demand_multiplier is not None:
                response[
                    'claims_courier_demand_multiplier'
                ] = claims_courier_demand_multiplier
            return response

        return mock

    do_mock()

    return do_mock


@pytest.fixture(name='call_v1_setcar_data')
def _call_v1_setcar_data(taxi_cargo_orders, default_order_id):
    async def _call(request=None):
        if request is None:
            request = {
                'cargo_ref_id': f'order/{default_order_id}',
                'tariff_class': f'courier',
                'order_id': 'taxi-order',
                'performer_info': {
                    'driver_profile_id': 'driver_id1',
                    'park_id': 'park_id1',
                    'transport_type': f'pedestrian',
                },
            }
        response = await taxi_cargo_orders.post(
            '/v1/setcar-data', headers={'Accept-Language': 'ru'}, json=request,
        )
        return response

    return _call
