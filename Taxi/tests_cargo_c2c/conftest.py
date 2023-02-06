# pylint: disable=wildcard-import, unused-wildcard-import
# pylint: disable=import-error, too-many-lines
import copy

import pytest
import base64

from cargo_c2c_plugins import *  # noqa: F403 F401 I100
from testsuite.utils import matching

from Crypto.Cipher import AES
from Crypto.Util import Padding


ORDER_ID = 'b1fe01ddc30247279f806e6c5e210a9f'

DEFAULT_ESTIMATE_REQUEST = {
    'delivery_description': {
        'zone_name': 'moscow',
        'payment_info': {'id': 'card-123', 'type': 'card'},
        'route_points': [
            {'type': 'source', 'coordinates': [55.0, 55.0]},
            {'type': 'destination', 'coordinates': [56.0, 56.0]},
        ],
        'due': '2020-01-01T00:00:00+00:00',
    },
    'taxi_tariffs': [
        {'taxi_tariff': 'cargo', 'taxi_requirements': {'a': '123', 'b': 123}},
        {
            'taxi_tariff': 'express',
            'taxi_requirements': {'a': '123', 'b': 123},
        },
    ],
}

DEFAULT_NDD_ESTIMATE_REQUEST = {
    'delivery_description': {
        'zone_name': 'moscow',
        'payment_info': {'id': 'card-123', 'type': 'card'},
        'route_points': [
            {
                'type': 'source',
                'coordinates': [37.5, 55.7],
                'uri': 'ytpp://delivery_ndd_zone/source_station_id',
            },
            {
                'type': 'destination',
                'coordinates': [37.5, 55.8],
                'uri': 'ytpp://delivery_ndd_zone/destination_station_id',
            },
        ],
        'due': '2020-01-01T00:00:00+00:00',
    },
    'taxi_tariffs': [
        {'taxi_tariff': 'ndd', 'taxi_requirements': {'package_size': 1}},
    ],
}

DEFAULT_DRAFT_REQUEST = {
    'offer_id': 'some id',
    'additional_delivery_description': {
        'comment': 'some_comment',
        'payment_info': {'id': 'card-123', 'type': 'card'},
        'route_points': [
            {
                'type': 'source',
                'uri': 'some uri',
                'coordinates': [55, 55],
                'full_text': 'some full_text',
                'short_text': 'some short_text',
                'area_description': 'some area_description',
                'contact': {'name': 'some_name', 'phone': '+79999999999'},
                'comment': 'comment',
            },
            {
                'type': 'destination',
                'uri': 'some uri',
                'coordinates': [56, 56],
                'full_text': 'some full_text',
                'short_text': 'some short_text',
                'area_description': 'some area_description',
                'contact': {'name': 'some_name', 'phone': '+79999999999'},
            },
        ],
    },
    'brand': 'yataxi',
}


DEFAULT_OFFER = {
    'offer_id': '01234567890123456789012345678912',
    'calc_id': 'cargo-pricing/v1/01234567890123456789012345678912',
    'estimate_response': {
        'type': '',
        'offer_id': '01234567890123456789012345678912',
        'taxi_tariff': 'express',
        'price': '200.999',
        'currency': 'RUB',
        'decision': 'order_allowed',
    },
    'delivery_description': {
        'zone_name': 'moscow',
        'payment_info': {'type': 'card', 'id': 'card-123'},
        'route_points': [
            {'type': 'source', 'coordinates': [55.0, 55.0]},
            {'type': 'destination', 'coordinates': [56.0, 56.0]},
        ],
        'due': '2020-01-01T00:00:00+00:00',
    },
    'taxi_tariff': {
        'taxi_tariff': 'express',
        'taxi_requirements': {'a': '123', 'b': 123},
    },
    'pa_auth_context': {
        'phone_pd_id': 'phone_pd_id_1',
        'user_id': 'some_user_id',
        'yandex_uid': 'yandex_uid',
        'locale': 'en',
        'remote_ip': '1.1.1.1',
    },
    'expectations': {'seconds_to_arrive': 778, 'meters_to_arrive': 7067},
    'driver_eta_request_link_id': '01234567890123456789012345678912',
}


DEFAULT_CLAIMS_REQUEST = {
    'claim': {
        'due': '2020-01-01T00:00:00+00:00',
        'items': [
            {
                'cost_currency': 'RUB',
                'cost_value': '0',
                'droppof_point': 1,
                'pickup_point': 0,
                'quantity': 1,
                'title': 'Посылка',
            },
        ],
        'comment': 'some_comment',
        'route_points': [
            {
                'point_id': 0,
                'visit_order': 1,
                'contact': {'name': '', 'phone': '+79999999999'},
                'address': {
                    'fullname': 'some full_text',
                    'shortname': 'some short_text',
                    'coordinates': [55.0, 55.0],
                    'uri': 'some uri',
                    'description': 'some area_description',
                    'comment': 'comment',
                },
                'skip_confirmation': True,
                'type': 'source',
            },
            {
                'point_id': 1,
                'visit_order': 2,
                'contact': {'name': '', 'phone': '+79999999999'},
                'address': {
                    'fullname': 'some full_text',
                    'shortname': 'some short_text',
                    'coordinates': [56.0, 56.0],
                    'uri': 'some uri',
                    'description': 'some area_description',
                },
                'skip_confirmation': True,
                'type': 'destination',
            },
        ],
        'client_requirements': {'taxi_class': 'express'},
        'skip_door_to_door': True,
        'skip_client_notify': True,
        'skip_emergency_notify': True,
        'skip_act': True,
        'optional_return': False,
        'c2c_data': {'payment_method_id': 'card-123', 'payment_type': 'card'},
    },
    'estimation_result': {
        'offer': {
            'offer_id': 'cargo-pricing/v1/01234567890123456789012345678912',
            'price_raw': 0,
            'price': '200.999',
        },
        'zone_id': 'moscow',
        'currency_rules': {
            'code': 'RUB',
            'text': 'руб.',
            'template': '$VALUE$ $SIGN$$CURRENCY$',
            'sign': '₽',
        },
        'taxi_class': 'express',
        'requirements': {'a': '123', 'b': 123},
    },
    'c2c_claim_origin_info': {
        'origin': 'yandexgo',
        'user_agent': 'some_agent',
        'customer_ip': '1.1.1.1',
    },
}


@pytest.fixture(name='get_default_order_id')
def _get_default_order_id():
    def _wrapper():
        return ORDER_ID

    return _wrapper


@pytest.fixture(name='get_default_draft_request')
def _get_default_draft_request():
    def _wrapper():
        return copy.deepcopy(DEFAULT_DRAFT_REQUEST)

    return _wrapper


@pytest.fixture(name='get_default_offer')
def _get_default_offer():
    def _wrapper():
        return copy.deepcopy(DEFAULT_OFFER)

    return _wrapper


@pytest.fixture(name='get_default_estimate_request')
def _get_default_estimate_request():
    def _wrapper():
        return copy.deepcopy(DEFAULT_ESTIMATE_REQUEST)

    return _wrapper


@pytest.fixture(name='get_default_ndd_estimate_request')
def _get_default_ndd_estimate_request():
    def _wrapper():
        return copy.deepcopy(DEFAULT_NDD_ESTIMATE_REQUEST)

    return _wrapper


@pytest.fixture(name='get_default_claims_request')
def _get_default_claims_request():
    def _wrapper():
        return copy.deepcopy(DEFAULT_CLAIMS_REQUEST)

    return _wrapper


@pytest.fixture(name='create_cargo_claims_orders')
async def create_cargo_claims_orders(taxi_cargo_c2c):
    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-clients-orders',
        json={
            'orders': [
                {
                    'id': {
                        'phone_pd_id': 'phone_pd_id_1',
                        'order_id': ORDER_ID,
                        'order_provider_id': 'cargo-claims',
                    },
                    'roles': ['sender'],
                },
                {
                    'id': {
                        'phone_pd_id': 'phone_pd_id_2',
                        'order_id': ORDER_ID,
                        'order_provider_id': 'cargo-claims',
                    },
                    'roles': ['recipient'],
                },
                {
                    'id': {
                        'phone_pd_id': 'phone_pd_id_3',
                        'order_id': ORDER_ID,
                        'order_provider_id': 'cargo-claims',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    )
    assert response.status_code == 200


@pytest.fixture(name='create_logistic_platform_orders')
async def create_logistic_platform_orders(taxi_cargo_c2c):
    async def _wrapper():
        response = await taxi_cargo_c2c.post(
            '/v1/actions/save-clients-orders',
            json={
                'orders': [
                    {
                        'id': {
                            'phone_pd_id': 'phone_pd_id_1',
                            'order_id': ORDER_ID,
                            'order_provider_id': 'logistic-platform',
                        },
                        'roles': ['initiator'],
                    },
                    {
                        'id': {
                            'phone_pd_id': 'phone_pd_id_2',
                            'order_id': ORDER_ID,
                            'order_provider_id': 'logistic-platform',
                        },
                        'roles': ['recipient'],
                    },
                ],
            },
        )
        assert response.status_code == 200

    return _wrapper


@pytest.fixture(name='create_market_orders')
async def create_market_orders(taxi_cargo_c2c):
    async def _wrapper():
        response = await taxi_cargo_c2c.post(
            '/v1/actions/save-clients-orders',
            json={
                'orders': [
                    {
                        'id': {
                            'phone_pd_id': 'phone_pd_id_1',
                            'order_id': 'some_market_id',
                            'order_provider_id': 'cargo-claims',
                        },
                        'roles': ['sender'],
                    },
                    {
                        'id': {
                            'phone_pd_id': 'phone_pd_id_2',
                            'order_id': 'some_market_id',
                            'order_provider_id': 'cargo-claims',
                        },
                        'roles': ['recipient'],
                    },
                    {
                        'id': {
                            'phone_pd_id': 'phone_pd_id_3',
                            'order_id': 'some_market_id',
                            'order_provider_id': 'cargo-claims',
                        },
                        'roles': ['recipient'],
                    },
                ],
            },
        )
        assert response.status_code == 200

    return _wrapper


@pytest.fixture(name='create_taxi_orders')
async def create_taxi_orders(taxi_cargo_c2c):
    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-clients-orders',
        json={
            'orders': [
                {
                    'id': {
                        'phone_pd_id': 'phone_pd_id_1',
                        'order_id': ORDER_ID,
                        'order_provider_id': 'taxi',
                    },
                    'roles': ['initiator', 'sender'],
                },
                {
                    'id': {
                        'phone_pd_id': 'phone_pd_id_2',
                        'order_id': ORDER_ID,
                        'order_provider_id': 'taxi',
                    },
                    'roles': ['recipient'],
                },
                {
                    'id': {
                        'phone_pd_id': 'phone_pd_id_3',
                        'order_id': ORDER_ID,
                        'order_provider_id': 'taxi',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    )
    assert response.status_code == 200


@pytest.fixture(name='create_cargo_c2c_orders')
def create_cargo_c2c_orders(
        taxi_cargo_c2c,
        mockserver,
        mock_cargo_pricing,
        default_pa_headers,
        default_calc_response,
        get_default_draft_request,
        get_default_estimate_request,
        get_default_claims_request,
):
    async def _wrapper(
            estimate_request=None,
            draft_request=None,
            expected_claims_request=None,
            add_coupon=False,
            add_postcard=False,
            claim_comment='some_comment',
            route_comment=None,
            add_user_default_tips=None,
    ):
        @mockserver.json_handler('/cargo-pricing/v1/taxi/calc/retrieve')
        def _calc(request):
            response = default_calc_response.copy()
            response['request'] = mock_cargo_pricing.v2_calc_mock.next_call()[
                'request'
            ].json
            return response

        @mockserver.json_handler('/cargo-claims/v2/claims/c2c/create')
        def _create_claim(request):
            req_json = request.json.copy()
            req_json['claim']['c2c_data'].pop('cargo_c2c_order_id')
            if not expected_claims_request:
                assert req_json == get_default_claims_request()
            else:
                assert req_json == expected_claims_request
            return {
                'id': 'some_cargo_ref_id',
                'items': [
                    {
                        'pickup_point': 1,
                        'droppof_point': 2,
                        'title': 'item title 1',
                        'cost_value': '10.40',
                        'cost_currency': 'RUB',
                        'quantity': 1,
                    },
                ],
                'comment': claim_comment,
                'route_points': [
                    {
                        'id': 1,
                        'visit_order': 1,
                        'address': {
                            'fullname': '1',
                            'coordinates': [37.8, 55.4],
                            'country': '1',
                            'city': '1',
                            'street': '1',
                            'building': '1',
                            'comment': route_comment,
                        },
                        'contact': {'phone': '+79999999991', 'name': 'string'},
                        'type': 'source',
                        'visit_status': 'pending',
                        'visited_at': {},
                    },
                    {
                        'id': 2,
                        'visit_order': 2,
                        'address': {
                            'fullname': '2',
                            'coordinates': [37.8, 55.4],
                            'country': '2',
                            'city': '2',
                            'street': '2',
                            'building': '2',
                            'comment': route_comment,
                        },
                        'contact': {'phone': '+79999999992', 'name': 'string'},
                        'type': 'destination',
                        'visit_status': 'pending',
                        'visited_at': {},
                    },
                ],
                'status': 'accepted',
                'version': 1,
                'created_ts': '2020-09-23T14:44:03.154152+00:00',
                'updated_ts': '2020-09-23T14:44:03.154152+00:00',
                'revision': 1,
                'user_request_revision': '123',
            }

        @mockserver.json_handler('/uantifraud/v1/delivery/can_make_order')
        def _mock_can_make_order(request):
            return mockserver.make_response(json={'status': 'allow'})

        if not estimate_request:
            estimate_request = get_default_estimate_request()

        if not draft_request:
            draft_request = get_default_draft_request()

        if not expected_claims_request:
            expected_claims_request = copy.deepcopy(
                get_default_claims_request(),
            )

        if add_coupon:
            estimate_request['delivery_description']['payment_info'][
                'coupon'
            ] = 'LUCKY_ONE_2000'

        if add_postcard:
            response = await taxi_cargo_c2c.post(
                '/4.0/cargo-c2c/v1/delivery/postcard/generate-upload-link',
                json={'content_type': 'image/jpeg'},
                headers=default_pa_headers('phone_pd_id_3'),
            )
            assert response.status_code == 200

            draft_request['additional_delivery_description']['postcard'] = {
                'user_message': 'hi, buddy!',
                'path': response.json()['path'],
                'download_url': response.json()['download_url'],
            }

        if add_user_default_tips:
            draft_request['additional_delivery_description']['tips'] = {
                'type': 'percent',
                'value': 10,
            }

        response = await taxi_cargo_c2c.post(
            '/v1/delivery/estimate',
            json=estimate_request,
            headers=default_pa_headers('phone_pd_id_3'),
        )
        assert response.status_code == 200

        draft_request['offer_id'] = response.json()['estimations'][0][
            'offer_id'
        ]
        response = await taxi_cargo_c2c.post(
            '/4.0/cargo-c2c/v1/delivery/draft',
            json=draft_request,
            headers=default_pa_headers('phone_pd_id_3'),
        )
        assert response.status_code == 200

        order_id = response.json()['delivery_id'].split('/')[1]

        response = await taxi_cargo_c2c.post(
            '/v1/processing/delivery-order/commit',
            json={
                'id': {
                    'order_id': order_id,
                    'order_provider_id': 'cargo-c2c',
                    'phone_pd_id': 'phone_pd_id_3',
                },
            },
        )
        assert response.status_code == 200

        response = await taxi_cargo_c2c.post(
            '/v1/processing/delivery-order/create-c2c-order',
            json={
                'id': {
                    'order_id': order_id,
                    'order_provider_id': 'cargo-c2c',
                    'phone_pd_id': 'phone_pd_id_3',
                },
            },
        )
        assert response.status_code == 200

        response = await taxi_cargo_c2c.post(
            '/v1/actions/save-clients-orders',
            json={
                'orders': [
                    {
                        'id': {
                            'phone_pd_id': 'phone_pd_id_1',
                            'order_id': order_id,
                            'order_provider_id': 'cargo-c2c',
                        },
                        'roles': ['sender'],
                    },
                    {
                        'id': {
                            'phone_pd_id': 'phone_pd_id_2',
                            'order_id': order_id,
                            'order_provider_id': 'cargo-c2c',
                        },
                        'roles': ['recipient'],
                    },
                    {
                        'id': {
                            'phone_pd_id': 'phone_pd_id_3',
                            'order_id': order_id,
                            'order_provider_id': 'cargo-c2c',
                        },
                        'roles': ['initiator'],
                        'user_id': 'some_user_id',
                    },
                ],
            },
        )

        return order_id

    return _wrapper


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.geoareas(filename='geoareas_moscow.json'))
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))


@pytest.fixture(name='create_logistic_platform_c2c_orders')
def _create_logistic_platform_c2c_orders(
        taxi_cargo_c2c,
        mockserver,
        default_pa_headers,
        get_default_ndd_estimate_request,
):
    offers_create_request = {
        'info': {'operator_request_id': matching.AnyString()},
        'source': {'platform_station': {'platform_id': 'source_station_id'}},
        'destination': {
            'type': 'platform_station',
            'platform_station': {'platform_id': 'destination_station_id'},
        },
        'items': [
            {
                'count': 1,
                'name': 'Не указано',
                'article': 'Не указано',
                'billing_details': {
                    'unit_price': 1000,
                    'assessed_unit_price': 1000,
                },
                'place_barcode': 'stub',
            },
        ],
        'places': [
            {
                'physical_dims': {
                    'weight_gross': 4,
                    'dx': 1,
                    'dy': 2,
                    'dz': 3,
                },
                'barcode': 'stub',
            },
        ],
        'billing_info': {'payment_method': 'already_paid'},
        'recipient_info': {
            'phone': '',
            'first_name': 'Не указано',
            'last_name': 'Не указано',
        },
        'sender_info': {
            'phone': '',
            'first_name': 'Не указано',
            'last_name': 'Не указано',
        },
        'originator_info': {
            'phone': '',
            'first_name': 'Не указано',
            'last_name': 'Не указано',
        },
        'last_mile_policy': 'self_pickup',
    }

    @pytest.mark.geoareas(filename='geoareas_moscow.json')
    @pytest.mark.tariffs(filename='tariffs.json')
    async def _wrapper():
        @mockserver.json_handler('/uantifraud/v1/delivery/can_make_order')
        def _mock_can_make_order(request):
            return mockserver.make_response(json={'status': 'allow'})

        @mockserver.json_handler(
            '/logistic-platform-uservices/api/c2c/platform/offers/create',
        )
        def _offers_create(request):
            assert request.json == offers_create_request
            return {
                'offers': [
                    {
                        'offer_details': {
                            'pricing_total': '239 RUB',
                            'delivery_interval': {
                                'max': '2022-05-15T23:59:59.000000Z',
                                'policy': 'self_pickup',
                                'min': '2022-05-15T00:00:00.000000Z',
                            },
                            'pickup_interval': {
                                'max': '2022-05-13T09:00:00.000000Z',
                                'min': '2022-05-13T08:00:00.000000Z',
                            },
                        },
                        'offer_id': 'lp_offer_id',
                        'expires_at': '2022-05-13T07:22:19.000000Z',
                    },
                ],
            }

        @mockserver.json_handler(
            '/logistic-platform-uservices/api/c2c/platform/offers/confirm',
        )
        def _offers_confirm(request):
            offers_confirm_request = copy.deepcopy(offers_create_request)
            offers_confirm_request['sender_info']['phone'] = '+79999999999'
            offers_confirm_request['recipient_info']['phone'] = '+79999999999'
            offers_confirm_request['originator_info']['phone'] = 'phone_pd_i'
            offers_confirm_request['originator_info'][
                'yandex_uid'
            ] = 'yandex_uid'
            offers_confirm_request['originator_info']['user_ip'] = '1.1.1.1'
            offers_confirm_request['offer_id'] = 'lp_offer_id'
            offers_confirm_request['billing_info']['taxi_payment_method'] = {
                'id': 'card-123',
                'type': 'card',
            }
            assert request.json == offers_confirm_request
            return {'request_id': 'some_request_id'}

        response = await taxi_cargo_c2c.post(
            '/v1/delivery/estimate',
            json=get_default_ndd_estimate_request(),
            headers=default_pa_headers('phone_pd_id_3'),
        )
        offer_id = response.json()['estimations'][0]['offer_id']
        assert offer_id.startswith('logistic-platform/')

        draft_request = {
            'offer_id': offer_id,
            'additional_delivery_description': {
                'route_points': [
                    {
                        'type': 'source',
                        'uri': 'some uri',
                        'coordinates': [37.5, 55.7],
                        'full_text': 'some full_text',
                        'short_text': 'some short_text',
                        'area_description': 'some area_description',
                        'contact': {'phone': '+79999999999'},
                        'comment': 'comment',
                    },
                    {
                        'type': 'destination',
                        'uri': 'some uri',
                        'coordinates': [37.5, 55.8],
                        'full_text': 'some full_text',
                        'short_text': 'some short_text',
                        'area_description': 'some area_description',
                        'contact': {'phone': '+79999999999'},
                    },
                ],
                'payment_info': {'id': 'card-123', 'type': 'card'},
            },
        }
        response = await taxi_cargo_c2c.post(
            '/4.0/cargo-c2c/v1/delivery/draft',
            json=draft_request,
            headers=default_pa_headers('phone_pd_id_3'),
        )
        assert response.status_code == 200
        delivery_id = response.json()['delivery_id']
        assert delivery_id.startswith('logistic-platform-c2c')

        order_id = delivery_id.split('/')[1]
        response = await taxi_cargo_c2c.post(
            '/v1/processing/delivery-order/create-c2c-order',
            json={
                'id': {
                    'order_id': order_id,
                    'order_provider_id': 'logistic-platform-c2c',
                    'phone_pd_id': 'phone_pd_id_3',
                },
            },
        )
        assert response.status_code == 200

        response = await taxi_cargo_c2c.post(
            '/v1/actions/save-clients-orders',
            json={
                'orders': [
                    {
                        'id': {
                            'phone_pd_id': 'phone_pd_id_1',
                            'order_id': order_id,
                            'order_provider_id': 'logistic-platform-c2c',
                        },
                        'roles': ['sender'],
                    },
                    {
                        'id': {
                            'phone_pd_id': 'phone_pd_id_2',
                            'order_id': order_id,
                            'order_provider_id': 'logistic-platform-c2c',
                        },
                        'roles': ['recipient'],
                    },
                    {
                        'id': {
                            'phone_pd_id': 'phone_pd_id_3',
                            'order_id': order_id,
                            'order_provider_id': 'logistic-platform-c2c',
                        },
                        'roles': ['initiator'],
                        'user_id': 'some_user_id',
                    },
                ],
            },
        )

        return order_id

    return _wrapper


@pytest.fixture(name='default_pa_headers')
def _default_pa_headers():
    def _wrapper(phone_pd_id, app_brand='yataxi', language='en'):
        return {
            'X-Yandex-UID': 'yandex_uid',
            'X-Request-Language': language,
            'X-YaTaxi-User': (
                f'personal_phone_id={phone_pd_id},'
                'personal_email_id=333,'
                'eats_user_id=444'
            ),
            'X-Request-Application': (
                f'app_name=iphone,app_ver1=10,app_ver2=2,app_brand={app_brand}'
            ),
            'User-Agent': 'some_agent',
            'X-Remote-IP': '1.1.1.1',
            'X-YaTaxi-UserId': 'some_user_id',
            'Timezone': 'Europe/Moscow',
        }

    return _wrapper


@pytest.fixture(autouse=True)
def mock_user_api(mockserver):
    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve_bulk')
    def _phones(request):
        return {
            'items': [
                {
                    'id': 'phone_id_1',
                    'phone': 'phone_1',
                    'type': 'yandex',
                    'personal_phone_id': 'phone_pd_id_1',
                },
                {
                    'id': 'phone_id_2',
                    'phone': 'phone_2',
                    'type': 'yandex',
                    'personal_phone_id': 'phone_pd_id_2',
                },
            ],
        }

    @mockserver.json_handler('/user-api/users/search')
    def _user_ids(request):
        return {
            'items': [
                {
                    'id': 'user_id_2_2',
                    'created': '2020-08-19T13:30:44.388+0000',
                    'updated': '2020-08-19T13:30:44.4+0000',
                    'phone_id': 'phone_id_2',
                    'application': 'android',
                    'application_version': '1',
                },
                {
                    'id': 'user_id_1_1',
                    'created': '2019-08-19T13:30:44.388+0000',
                    'updated': '2019-08-19T13:30:44.4+0000',
                    'phone_id': 'phone_id_1',
                    'application': 'iphone',
                    'application_version': '1',
                },
                {
                    'id': 'user_id_1_2',
                    'created': '2020-08-19T13:30:44.388+0000',
                    'updated': '2020-08-19T13:30:44.4+0000',
                    'phone_id': 'phone_id_1',
                    'application': 'iphone',
                    'application_version': '1',
                },
                {
                    'id': 'user_id_2_1',
                    'created': '2019-08-19T13:30:44.388+0000',
                    'updated': '2019-08-19T13:30:44.4+0000',
                    'phone_id': 'phone_id_2',
                    'application': 'iphone',
                    'application_version': '1',
                },
            ],
        }

    @mockserver.json_handler('/user-api/v2/user_phones/get')
    def _user_phones(request):
        return {
            'id': request.json['id'],
            'personal_phone_id': request.json['id'],
        }

    @mockserver.json_handler('/user-api/users/get')
    def _user_get(request):
        return {
            'id': request.json['id'],
            'phone_id': 'phone_id',
            'yandex_uid': 'yandex_uid',
            'yandex_uid_type': 'portal',
            'application': 'iphone',
        }


@pytest.fixture(autouse=True)
def mock_c2c(mockserver, load_json):
    @mockserver.json_handler('/cargo-c2c/v1/actions/save-clients-orders')
    def _save_clients_orders(request):
        orders = []
        for order_to_save in request.json['orders']:
            order = {
                'id': order_to_save['id'],
                'roles': order_to_save['roles'],
                'sharing_key': 'some_sharing_key',
                'user_id': 'some_cool_user',
            }
            orders.append(order)
        return mockserver.make_response(json={'orders': orders})


@pytest.fixture
def mock_claims_full(mockserver, load_json):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json(context.file_name)
        if context.claim_status:
            resp['status'] = context.claim_status
        if context.current_point_id:
            resp['current_point_id'] = context.current_point_id
        if context.corp_client_id:
            resp['corp_client_id'] = context.corp_client_id
        if context.tariff:
            resp['matched_cars'] = [{'taxi_class': context.tariff}]
        if context.payment_type:
            resp['c2c_data']['payment_type'] = context.payment_type
        if context.current_point_id and context.update_point_visit_status:
            for point in resp['route_points']:
                if point['id'] == context.current_point_id:
                    point['visit_status'] = context.update_point_visit_status
        if context.final_price:
            resp['pricing']['final_price'] = context.final_price
        if context.current_point:
            resp['on_the_way_state']['current_point'] = context.current_point
        if context.warnings:
            resp['warnings'] = context.warnings

        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json(context.file_name)
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        for point in full['route_points']:
            print(point)
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    class Context:
        def __init__(self):
            self.file_name = 'claim_full_response.json'
            self.points_eta_filename = 'claim_points_eta.json'
            self.current_point_id = None
            self.claim_status = None
            self.corp_client_id = None
            self.tariff = None
            self.update_point_visit_status = None
            self.payment_type = None
            self.final_price = None
            self.current_point = None
            self.warnings = None

    context = Context()
    return context


@pytest.fixture(autouse=True)
def mock_driver_trackstory(mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def _position(request):
        assert request.json == {'driver_id': 'parkid1_driverid1'}
        return mockserver.make_response(
            json={'position': context.position, 'type': 'raw'}, status=200,
        )

    class Context:
        def __init__(self):
            self.position = {
                'direction': 0,
                'lat': 37.5,
                'lon': 55.7,
                'speed': 0,
                'timestamp': 100,
            }

    context = Context()
    return context


@pytest.fixture
def mock_waybill_info(mockserver, load_json):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _waybill_info(request):
        resp = load_json(context.file_name)
        return mockserver.make_response(json=resp)

    class Context:
        def __init__(self):
            self.file_name = 'waybill_info_response.json'

    context = Context()
    return context


@pytest.fixture(autouse=True)
def mock_processing(mockserver, load_json):
    @mockserver.json_handler('/processing/v1/delivery/order/create-event')
    def _create_event(request):
        return {'event_id': '123'}

    @mockserver.json_handler('/processing/v1/delivery/order/events')
    def _events(request):
        return {'events': []}


def _decode_value(x):
    return {'id': x['id'], 'value': x['id'][:-3]}


def _decode_request(request):
    return {'items': [_decode_value(x) for x in request.json['items']]}


@pytest.fixture(autouse=True)
def mock_personal(mockserver, load_json):
    for data_type in ['phones']:

        @mockserver.json_handler(f'/personal/v1/{data_type}/bulk_retrieve')
        async def _(request):
            return mockserver.make_response(
                status=200, json=_decode_request(request),
            )

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return {'id': request.json['id'], 'value': request.json['id'][:-3]}

    @mockserver.json_handler('/personal/v1/phones/store')
    def _phone_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones_bulk_store(request):
        return {
            'items': [
                {'id': item['value'] + '_id', 'value': item['value']}
                for item in request.json['items']
            ],
        }


@pytest.fixture(autouse=True)
def mock_udriver_photos(mockserver, load_json):
    @mockserver.json_handler('/udriver-photos/driver-photos/v1/photo')
    def _get_photo(request):
        return {
            'actual_photo': {
                'avatar_url': 'testavatar',
                'portrait_url': 'testportrait',
            },
        }


@pytest.fixture(name='config_estimate_result_validation')
async def _config_estimate_result_validation(taxi_config, taxi_cargo_c2c):
    taxi_config.set_values(
        {
            'CARGO_MATCHER_ESTIMATE_RESULT_VALIDATION_PARAMS': {
                'max_route_distance_meter': 1500,
                'max_route_time_minutes': 15,
            },
        },
    )
    await taxi_cargo_c2c.invalidate_caches()


@pytest.fixture(name='default_calc_response', autouse=True)
def _default_calc_response(testpoint):
    return {
        'calc_id': 'cargo-pricing/v1/01234567890123456789012345678912',
        'price': '200.999',
        'units': {
            'currency': 'RUB',
            'distance': 'kilometer',
            'time': 'minute',
        },
        'pricing_case': 'default',
        'services': [],
        'details': {
            'paid_waiting_in_destination_price': '25.0000',
            'paid_waiting_in_destination_time': '30.0000',
            'paid_waiting_in_transit_price': '20.0000',
            'paid_waiting_in_transit_time': '0.0000',
            'paid_waiting_price': '0.0000',
            'paid_waiting_time': '60.0000',
            'pricing_case': 'default',
            'total_distance': '3541.0878',
            'total_time': '1077.0000',
        },
        'taxi_pricing_response': {},
    }


@pytest.fixture(name='default_calc_response_v2', autouse=True)
def _default_calc_response_v2(testpoint):
    return {
        'calculations': [
            {
                'calc_id': 'cargo-pricing/v1/01234567890123456789012345678912',
                'result': {
                    'calc_id': (
                        'cargo-pricing/v1/01234567890123456789012345678912'
                    ),
                    'prices': {
                        'total_price': '200.999',
                        'source_waiting_price_per_unit': '5',
                        'destination_waiting_price_per_unit': '10',
                    },
                    'details': {
                        'algorithm': {'pricing_case': 'default'},
                        'currency': {'code': 'RUB'},
                        'services': [
                            {
                                'name': 'base_price',
                                'text': 'Заказ',
                                'total_price': '100',
                                'components': [
                                    {
                                        'name': 'boarding',
                                        'text': 'Подача',
                                        'total_price': '100',
                                    },
                                ],
                            },
                            {
                                'name': 'paid_waiting',
                                'text': 'Ожидание',
                                'total_price': '100.999',
                                'components': [
                                    {
                                        'name': 'paid_waiting',
                                        'text': 'Ожидание у отправителя',
                                        'total_price': '100.999',
                                        'quantity': {
                                            'duration': 900,
                                            'type': 'time',
                                        },
                                    },
                                ],
                            },
                        ],
                        'waypoints': [
                            {
                                'type': 'pickup',
                                'position': [
                                    37.58505871591705,
                                    55.75112587081837,
                                ],
                                'waiting': {
                                    'total_waiting': '0',
                                    'paid_waiting': '0',
                                    'free_waiting_time': '300',
                                    'was_limited': False,
                                    'paid_waiting_disabled': False,
                                },
                                'route': {
                                    'time_from_start': '0',
                                    'distance_from_start': '0',
                                },
                                'cargo_items': [],
                            },
                            {
                                'type': 'dropoff',
                                'position': [
                                    37.58574980969229,
                                    55.75155701795171,
                                ],
                                'waiting': {
                                    'total_waiting': '0',
                                    'paid_waiting': '0',
                                    'free_waiting_time': '600',
                                    'was_limited': False,
                                    'paid_waiting_disabled': False,
                                },
                                'route': {
                                    'time_from_start': '74.800003',
                                    'distance_from_start': '67.742577',
                                },
                                'cargo_items': [],
                            },
                        ],
                    },
                    'cancel_options': {},
                    'diagnostics': {},
                },
            },
            {
                'calc_id': 'cargo-pricing/v1/01234567890123456789012345678912',
                'result': {
                    'calc_id': (
                        'cargo-pricing/v1/01234567890123456789012345678912'
                    ),
                    'prices': {'total_price': '200.999'},
                    'details': {
                        'algorithm': {'pricing_case': 'default'},
                        'currency': {'code': 'RUB'},
                        'services': [],
                        'waypoints': [],
                    },
                    'cancel_options': {},
                    'diagnostics': {},
                },
            },
            {
                'calc_id': 'cargo-pricing/v1/01234567890123456789012345678912',
                'result': {
                    'calc_id': (
                        'cargo-pricing/v1/01234567890123456789012345678912'
                    ),
                    'prices': {'total_price': '229.999'},
                    'details': {
                        'algorithm': {'pricing_case': 'default'},
                        'currency': {'code': 'RUB'},
                        'services': [],
                        'waypoints': [],
                    },
                    'cancel_options': {},
                    'diagnostics': {},
                },
            },
        ],
    }


@pytest.fixture(name='mock_cargo_pricing', autouse=True)
def _mock_cargo_pricing_v2(mockserver, default_calc_response_v2):
    class Context:
        def __init__(self):
            self.expected_v2_calc_request = None
            self.v2_calc_mock = None
            calcs = default_calc_response_v2.copy()['calculations']
            self.v2_calc_response_data = {
                'cargo': calcs[0],
                'express': calcs[1],
                'courier': calcs[2],
            }

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc')
    def _calc(request):
        if ctx.expected_v2_calc_request is not None:
            assert request.json == ctx.expected_v2_calc_request
        response = {'calculations': []}
        for tarrif in request.json['calc_requests']:
            response['calculations'].append(
                ctx.v2_calc_response_data[tarrif['tariff_class']],
            )
        return response

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc/confirm-usage')
    def _confirm_usage(request):
        return {}

    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc/retrieve')
    def _retrieve(request):
        return default_calc_response_v2

    ctx.v2_calc_mock = _calc

    return ctx


@pytest.fixture(name='mock_logistic_platform', autouse=True)
def _mock_logistic_platform(mockserver, load_json):
    @mockserver.json_handler(
        '/logistic-platform-admin/api/admin/request/trace',
    )
    def _mock_trace(request):
        resp = load_json('logistic-platform/trace/%s' % context.file_name)
        resp['model']['request_tags'] = context.request_tags
        return resp

    class Context:
        def __init__(self):
            self.file_name = 'delivered.json'
            self.request_tags = []

    context = Context()
    return context


@pytest.fixture(name='mock_request_info', autouse=True)
def _mock_request_info(mockserver, load_json):
    @mockserver.json_handler(
        'logistic-platform-uservices/api/internal/platform/request/info',
    )
    def _mock_info(request):
        return {
            'request': {
                'items': [
                    {
                        'physical_dims': {
                            'predefined_volume': 0,
                            'dz': 0,
                            'dy': 0,
                            'dx': 0,
                        },
                        'name': 'Универсальная щетка для унитаза',
                        'article': '178506',
                        'count': 1,
                        'billing_details': {
                            'assessed_unit_price': 99000,
                            'nds': 0,
                            'inn': '330640485495',
                            'currency': 'RUB',
                            'unit_price': 99000,
                            'tax_system_code': 0,
                        },
                        'refused_count': 0,
                        'place_barcode': '',
                    },
                ],
                'source': {
                    'platform_station': {
                        'platform_id': 'e7d48f98-7e8f-4a82-8dab-8723e7487097',
                    },
                },
                'info': {
                    'operator_request_id': '565757_1',
                    'referral_source': '',
                },
                'particular_items_refuse': False,
                'recipient_info': {
                    'phone': '+71111111111',
                    'first_name': 'Галина',
                },
                'sender_info': {'phone': '+70000000002', 'first_name': 'Иван'},
                'initiator_info': {
                    'phone': '+70000000003',
                    'first_name': 'Всеволод',
                },
                'destination': {
                    'interval': {'from': 1645077600, 'to': 1645110000},
                    'type': 'custom_location',
                    'interval_utc': {
                        'from': '2022-02-17T06:00:00.000000Z',
                        'to': '2022-02-17T15:00:00.000000Z',
                    },
                    'custom_location': {
                        'latitude': 37.730859,
                        'longitude': 55.685538,
                        'details': {
                            'comment': '',
                            'full_address': 'г Москва, ул Полбина, д 32, кв 1',
                            'room': '',
                        },
                    },
                },
                'places': [
                    {
                        'physical_dims': {
                            'predefined_volume': 1000,
                            'dz': 10,
                            'weight_gross': 100,
                            'dy': 10,
                            'dx': 10,
                        },
                        'barcode': '213851',
                    },
                ],
                'billing_info': {
                    'payment_method': 'card_on_receipt',
                    'delivery_cost': 0,
                },
            },
            'full_items_price': 99000,
            'request_id': '14e25e2c-21c4-4b63-b2d2-666b9570eba1',
            'state': {
                'status': 'DELIVERY_PROCESSING_STARTED',
                'description': 'Заказ подтвержден в сортировочном центре',
            },
        }


@pytest.fixture(name='mock_order_statuses_history')
def _mock_order_statuses_history(mockserver, get_default_order_id, load_json):
    @mockserver.json_handler(
        'logistic-platform-admin/api/internal/platform/request/history',
    )
    def _get_order_statuses_history(request):
        if context.file_name:
            return load_json(
                'logistic-platform/history/%s' % context.file_name,
            )
        return {'state_history': []}

    class Context:
        def __init__(self):
            self.file_name = 'delivered.json'

    context = Context()
    return context


@pytest.fixture(name='mock_driver_eta', autouse=True)
def driver_eta(mockserver):
    v2_response = {
        'classes': {
            'cargo': {
                'estimated_distance': 7067,
                'estimated_time': 778,
                'found': True,
                'search_settings': {
                    'limit': 10,
                    'max_distance': 15000,
                    'max_route_distance': 15000,
                    'max_route_time': 900,
                },
                'paid_supply_enabled': False,
                'order_allowed': True,
            },
            'express': {
                'found': True,
                'estimated_distance': 7067,
                'estimated_time': 778,
                'search_settings': {
                    'limit': 10,
                    'max_distance': 15000,
                    'max_route_distance': 15000,
                    'max_route_time': 900,
                },
                'paid_supply_enabled': False,
                'order_allowed': True,
            },
        },
    }

    @mockserver.json_handler('/driver-eta/driver-eta/v2/eta')
    def _v2_eta(request):
        if context.mock_v2_eta_expected_request:
            assert request.json == context.mock_v2_eta_expected_request
        return context.v2_response

    class Context:
        def __init__(self):
            self.mock_v2_eta = _v2_eta

            self.mock_v2_eta_expected_request = None

            self.v2_response = v2_response

    context = Context()
    return context


@pytest.fixture(autouse=True)
def mock_admin_images(mockserver, load_json):
    @mockserver.json_handler('/admin-images/internal/list')
    def _mock_core(request):
        return load_json('admin_images_response.json')


@pytest.fixture(autouse=True)
def mock_unique_drivers(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve(request):
        assert request.json == {'profile_id_in_set': ['parkid1_driverid1']}
        return mockserver.make_response(
            json={
                'uniques': [
                    {
                        'park_driver_profile_id': 'parkid1_driverid1',
                        'data': {'unique_driver_id': 'unique_driver_id_1'},
                    },
                ],
            },
            status=200,
        )


@pytest.fixture(autouse=True)
def mock_driver_ratings(mockserver):
    @mockserver.json_handler('/driver-ratings/v2/driver/rating')
    def _rating(request):
        assert request.query == {'unique_driver_id': 'unique_driver_id_1'}
        return mockserver.make_response(
            json={'unique_driver_id': 'unique_driver_id_1', 'rating': '4.79'},
            status=200,
        )


@pytest.fixture(autouse=True)
def mock_driver_profiles(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _retireve(request):
        return mockserver.make_response(
            json={
                'profiles': [
                    {
                        'data': {
                            'phone_pd_ids': [{'pd_id': '+7123_id'}],
                            'full_name': {'first_name': 'Иван'},
                        },
                        'park_driver_profile_id': 'db_id1_uuid1',
                    },
                ],
            },
            status=200,
        )


@pytest.fixture(autouse=True)
def mock_cardstorage(mockserver):
    @mockserver.json_handler('/cardstorage/v1/card')
    def _mock_v1_card(request):
        return {
            'card_id': '1',
            'billing_card_id': '1',
            'permanent_card_id': '1',
            'currency': 'RUB',
            'expiration_month': 12,
            'expiration_year': 2020,
            'owner': 'Mr',
            'possible_moneyless': False,
            'region_id': 'RU',
            'regions_checked': ['RU'],
            'system': 'VISA',
            'valid': True,
            'bound': True,
            'unverified': False,
            'busy': False,
            'busy_with': [],
            'from_db': True,
            'number': '51002222****4444',
            'bin': '510022',
        }


@pytest.fixture(autouse=True)
def mock_payment_method(mockserver):
    @mockserver.json_handler(
        'cargo-finance/internal/cargo-finance/payment-methods/v1',
    )
    def _mock_payment_methods_v1(request):
        return {
            'methods': [
                {
                    'id': 'cargocorp-1234',
                    'display': {
                        'type': 'some_type',
                        'image_tag': 'image_tag',
                        'title': 'CRGCRP',
                    },
                    'discounts': [],
                    'details': {
                        'type': 'corpcard',
                        'cardstorage_id': 'card-1234',
                        'owner_yandex_uid': 'yandex_uid',
                        'is_disabled': False,
                    },
                },
            ],
        }


@pytest.fixture(autouse=True)
def mock_parks_commute(mockserver):
    @mockserver.json_handler('/parks-commute/v1/parks/retrieve_by_park_id')
    def _retireve(request):
        return {'parks': [{'park_id': 'park_id', 'data': {'clid': 'clid'}}]}


@pytest.fixture(autouse=True)
def mock_yamaps(yamaps):
    @yamaps.set_fmt_geo_objects_callback
    def _mock_maps(request):
        return [
            {
                'description': 'Москва, Россия',
                'geocoder': {
                    'address': {
                        'country': 'Россия',
                        'formatted_address': (
                            'Россия, Москва, Садовническая улица'
                        ),
                        'locality': 'Москва',
                        'street': 'Садовническая улица',
                    },
                    'id': '8063585',
                },
                'geometry': [37.615928, 55.757333],
                'name': 'Садовническая улица',
                'uri': 'ymapsbm1://geo?exit1',
            },
        ]


@pytest.fixture(autouse=True)
def mock_special_zones(mockserver):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}


@pytest.fixture(autouse=True)
def mock_parks_replica(mockserver):
    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _retireve(request):
        return {
            'parks': [
                {
                    'park_id': 'park_id',
                    'data': {
                        'legal_address': 'legal_address',
                        'ogrn': '123',
                        'long_name': 'ООО ПАРК',
                    },
                },
            ],
        }


@pytest.fixture(name='build_ucommunications_body')
def _build_ucommunications_body():
    def _wrapper(
            title,
            body,
            order_id='',
            order_provider_id='',
            roles='',
            status='',
            tariff_class='',
    ):
        return {
            'payload': {
                'logistics': {
                    'type': 'delivery-state-changed',
                    'notification_group': f'{order_provider_id}/{order_id}',
                    'delivery_id': f'{order_provider_id}/{order_id}',
                    'meta': {
                        'order_provider_id': order_provider_id,
                        'order_status': status,
                        'roles': roles,
                        'tariff_class': tariff_class,
                    },
                },
            },
            'repack': {
                'apns': {
                    'aps': {
                        'alert': {'body': body, 'title': title},
                        'content-available': 1,
                        'thread-id': f'{order_provider_id}/{order_id}',
                    },
                },
                'gcm': {'notification': {'title': title, 'body': body}},
                'hms': {'notification': {'title': title, 'body': body}},
            },
        }

    return _wrapper


@pytest.fixture(autouse=True)
def save_client_order(testpoint):
    @testpoint('save-client-order')
    def _testpoint(arg):
        if context.expected_roles is not None:
            assert arg['orders'][0]['roles'] == context.expected_roles
        context.times_called += 1
        context.next_call_ = {'arg': arg}

    class Context:
        def __init__(self):
            self.expected_roles = None
            self.times_called = 0
            self.next_call_ = None

        def next_call(self):
            return self.next_call_

    context = Context()
    return context


@pytest.fixture(autouse=True)
def push_notify(testpoint):
    @testpoint('push-notify')
    def _testpoint(arg):
        pass

    return _testpoint


@pytest.fixture(autouse=True)
def order_processing_order_create_requested(
        testpoint,
):  # pylint: disable=C0103
    @testpoint('order-processing-order-create-requested')
    def _testpoint(arg):
        pass

    return _testpoint


@pytest.fixture(autouse=True)
def order_processing_order_cancel_requested(
        testpoint,
):  # pylint: disable=C0103
    @testpoint('order-processing-order-cancel-requested')
    def _testpoint(arg):
        pass

    return _testpoint


@pytest.fixture(autouse=True)
def order_processing_order_terminated(testpoint):  # pylint: disable=C0103
    @testpoint('order-processing-order-terminated')
    def _testpoint(arg):
        pass

    return _testpoint


@pytest.fixture(autouse=True)
def order_processing_feedback_requested(testpoint):  # pylint: disable=C0103
    @testpoint('order-processing-feedback-requested')
    def _testpoint(arg):
        pass

    return _testpoint


@pytest.fixture(autouse=True)
def _mock_user_api(mockserver):
    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_info(request):
        return {
            'id': request.json['id'],
            'token_only': True,
            'authorized': True,
            'application': 'iphone',
            'application_version': '4.90.0',
            'phone': {
                'id': 'some-yataxi-phone-id',
                'personal_id': 'some-yataxi-phone-id',
            },
        }


@pytest.fixture
def mock_passenger_feedback(mockserver, load_json):
    @mockserver.json_handler(
        '/passenger-feedback/passenger-feedback/v2/feedback',
    )
    def _mock_save_feedback(request):
        assert request.json == {
            'id': 'user_id_2_2',
            'phone_id': 'some-yataxi-phone-id',
            'order_id': 'some_taxi_order_id',
            'order_created_time': '2019-03-17T00:00:00+00:00',
            'order_status': 'assigned',
            'rating': context.expected_rating,
        }
        context.times_called += 1
        return mockserver.make_response(json={})

    class Context:
        def __init__(self):
            self.expected_rating = None
            self.times_called = 0

    context = Context()
    return context


@pytest.fixture
def build_notify_stq_kwargs():
    def _wrapper(
            phone_pd_id,
            order_id,
            order_provider_id,
            role,
            status,
            notification_id,
            key_title,
            key_body,
            body_count=None,
            push_content_args_title=None,
            push_content_args_body=None,
    ):
        stq_kwargs = {
            'id': {
                'phone_pd_id': phone_pd_id,
                'order_id': order_id,
                'order_provider_id': order_provider_id,
            },
            'notification_id': notification_id,
            'push_payload': {
                'logistics': {
                    'type': 'delivery-state-changed',
                    'delivery_id': f'cargo-c2c/{order_id}',
                    'notification_group': f'cargo-c2c/{order_id}',
                    'meta': {
                        'tariff_class': 'courier',
                        'order_provider_id': 'cargo-c2c',
                        'roles': [role],
                        'order_status': status,
                    },
                },
            },
            'push_content': {
                'title': {
                    'keyset': 'cargo',
                    'key': f'{key_title}.title',
                    'locale': 'ru',
                },
                'body': {
                    'keyset': 'cargo',
                    'key': f'{key_body}.body',
                    'locale': 'ru',
                },
            },
            'log_extra': {'_link': matching.AnyString()},
        }

        if body_count is not None:
            stq_kwargs['push_content']['body']['count'] = body_count
        if push_content_args_title is not None:
            stq_kwargs['push_content']['title'][
                'args'
            ] = push_content_args_title
        if push_content_args_body is not None:
            stq_kwargs['push_content']['body']['args'] = push_content_args_body

        return stq_kwargs

    return _wrapper


@pytest.fixture
def taxi_processing(taxi_cargo_c2c):
    async def _wrapper(
            order_id,
            event,
            status,
            initiator_phone_id=None,
            tariff_class=None,
            locale=None,
            source_point=None,
            destination_points=None,
            door_to_door=None,
            application=None,
            zone=None,
            route_sharing_key=None,
            taxi_status=None,
            performer=None,
            corp_client_id=None,
    ):
        response = {'order_id': order_id, 'event': event, 'status': status}

        if initiator_phone_id:
            response['initiator_phone_id'] = initiator_phone_id
        if tariff_class:
            response['tariff_class'] = tariff_class
        if locale:
            response['locale'] = locale
        if source_point:
            response['source_point'] = source_point
        if destination_points:
            response['destination_points'] = destination_points
        if door_to_door:
            response['door_to_door'] = door_to_door
        if application:
            response['application'] = application
        if zone:
            response['zone'] = zone
        if route_sharing_key:
            response['route_sharing_key'] = route_sharing_key
        if taxi_status:
            response['taxi_status'] = taxi_status
        if performer:
            response['performer'] = performer
        if corp_client_id:
            response['corp_client_id'] = corp_client_id

        await taxi_cargo_c2c.post(
            '/v1/processing/taxi/process-event', json=response,
        )

    return _wrapper


@pytest.fixture(name='mock_request_history', autouse=True)
def _mock_request_history(mockserver, load_json):
    @mockserver.json_handler(
        'logistic-platform-admin/api/internal/platform/request/history',
    )
    def _mock_info(request):
        return {
            'state_history': [
                {
                    'timestamp': 1647521911,
                    'status': 'CREATED_IN_PLATFORM',
                    'description': 'Заказ создан в логистической платформе',
                },
                {
                    'timestamp': 1647522621,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'CREATED',
                    'timestamp_utc': '2022-03-17T13:10:21.000000Z',
                    'description': 'Заказ подтвержден',
                },
                {
                    'timestamp': 1647522621,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'ESTIMATING',
                    'timestamp_utc': '2022-03-17T13:10:21.000000Z',
                    'description': 'Идет процесс оценки заявки',
                },
                {
                    'timestamp': 1647522621,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'READY_FOR_APPROVAL',
                    'timestamp_utc': '2022-03-17T13:10:21.000000Z',
                    'description': 'Заявка успешно оценена',
                },
                {
                    'timestamp': 1647522674,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'ACCEPTED',
                    'timestamp_utc': '2022-03-17T13:11:14.000000Z',
                    'description': 'Заявка подтверждена клиентом',
                },
                {
                    'timestamp': 1647522674,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'PERFOMER_LOOKUP',
                    'timestamp_utc': '2022-03-17T13:11:14.000000Z',
                    'description': 'Заявка взята в обработку',
                },
                {
                    'timestamp': 1647522686,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'VALIDATING',
                    'timestamp_utc': '2022-03-17T13:11:26.000000Z',
                    'description': 'Идет поиск исполнителя',
                },
                {
                    'timestamp': 1647522688,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'DELIVERY_TRACK_RECEIVED',
                    'timestamp_utc': '2022-03-17T13:11:28.000000Z',
                    'description': 'Заказ создан в системе службы доставки',
                },
                {
                    'timestamp': 1647523102,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'READY_FOR_PICKIP_CONFIRMATION',
                    'timestamp_utc': '2022-03-17T13:18:22.000000Z',
                    'description': 'Водитель ждет',
                },
                {
                    'timestamp': 1647523102,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'PICKUPED',
                    'timestamp_utc': '2022-03-17T13:18:22.000000Z',
                    'description': 'Водитель успешно забрал груз.',
                },
                {
                    'timestamp': 1647523378,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'READY_FOR_DELIVERY_CONFIRMATION',
                    'timestamp_utc': '2022-03-17T13:22:58.000000Z',
                    'description': 'Водитель ждет код подтверждения',
                },
                {
                    'timestamp': 1647523378,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'DELIVERY_DELIVERED',
                    'timestamp_utc': '2022-03-17T13:22:58.000000Z',
                    'description': 'Доставлен',
                },
                {
                    'timestamp': 1647523378,
                    'event_state': {
                        'node_to_id': 'f902e300-cfbf-4cb5-ba88-0163e1f1c9f9',
                        'node_from_id': '29c56387-2bb9-44fe-9533-6cd993942761',
                        'type': 'transfer',
                        'id': '140fd62f-73fc-4d14-a685-da4a4a670939',
                    },
                    'status': 'DELIVERED_FINISH',
                    'timestamp_utc': '2022-03-17T13:22:58.000000Z',
                    'description': 'Доставлен - подтверждено',
                },
            ],
        }


@pytest.fixture(name='mock_request_get', autouse=True)
def _mock_request_get(mockserver, load_json):
    @mockserver.json_handler('logistic-platform-admin/api/admin/request/get')
    def _mock_info(request):
        return {
            'model': {
                'employer': 'strizh',
                'places_info': [
                    {
                        'events_chain': [
                            {
                                'reservation_details': {
                                    'external_order_id': '',
                                    'output_carriage_id': '',
                                    'internal_place_id': (
                                        'd7632b53-873b-4171-bb3a-9feff6b0414b'
                                    ),
                                    'node_id': (
                                        '0379ffc8-724e-4b80-bfee-924c20dc9f1c'
                                    ),
                                    'operator_id': 'beru',
                                    'reserve_take_ts': 1646132815,
                                    'reserve_put_ts': 1646131015,
                                    'input_carriage_id': '',
                                    'reservation_id': (
                                        '7a3e0de9-8464-4fe5-85eb-159ef5dbfe7a'
                                    ),
                                    'status': 'draft',
                                },
                                'node_details': {
                                    'implementation': {
                                        'class_name': 'external_station',
                                        'contacts': {
                                            'phone': '+79260000000',
                                            'tag_name': 'contact',
                                            'patronymic': '',
                                            'last_name': 'склада',
                                            'first_name': '',
                                            'email': '',
                                            'comments': '',
                                        },
                                        'station': {
                                            'location_ll': {
                                                'lat': 55.774532,
                                                'lon': 37.632745,
                                            },
                                            'location_details': {
                                                'street': 'Проспект Мира',
                                                'geo_id': 213,
                                                'locality': 'Москва',
                                                'country': 'Россия',
                                                'housing': '',
                                                'building': '',
                                                'house': '12',
                                                'comment': 'оставить у двери',
                                                'settlement': 'Москва',
                                                'room': '',
                                                'region': 'Москва',
                                            },
                                            'integrations': [],
                                            'station_full_name': '',
                                            'courier_id': 0,
                                            'delivery_service_id': '',
                                            'excluded_input_intervals': [],
                                            'enabled_in_platform': True,
                                            'station_type': 'warehouse',
                                            'enabled': True,
                                            'revision': 0,
                                            'timetable_input': {
                                                'time_zone': 0,
                                                'restrictions': [
                                                    {
                                                        'time_to': 2359,
                                                        'time_from': 0,
                                                    },
                                                ],
                                            },
                                            'operator_station_id': (
                                                '10000998614'
                                            ),
                                            'dropoff_allowed': False,
                                            'station_name': '',
                                            'physical_limits': {},
                                            'self_pickup_allowed': False,
                                            'lms_ids': [],
                                            'instruction': '',
                                            'deprecated': False,
                                            'is_manually_created': False,
                                            'timetable_output': {
                                                'time_zone': 0,
                                                'restrictions': [
                                                    {
                                                        'time_to': 2359,
                                                        'time_from': 0,
                                                    },
                                                ],
                                            },
                                            'location': [37.632745, 55.774532],
                                            'payment_methods': [],
                                            'need_synchronization': True,
                                            'operator_id': 'beru',
                                            'station_id': '',
                                        },
                                    },
                                    'node_id': (
                                        '0379ffc8-724e-4b80-bfee-924c20dc9f1c'
                                    ),
                                    'need_input_electronic_certificate': False,
                                    'need_output_electronic_certificate': (
                                        False
                                    ),
                                    'is_deferred_courier': False,
                                    'public_output_carriage_id': '',
                                    'code': 'n_from',
                                    'branches_limit_for_place': 3,
                                    'visits_limit_for_place': 1,
                                },
                                'type': 'NODE',
                            },
                            {
                                'action_details': {
                                    'execution_idx': 0,
                                    'operator_contractor_id': '',
                                    'internal_contractor_id': '',
                                    'action_code': 'ea87',
                                    'confirmation_info': {
                                        'need_electronic_certificate': False,
                                        'external_confirmation_code': '',
                                    },
                                    'action_id': 191983,
                                    'requested_action_type': 'take_resource',
                                    'action_status': 'add',
                                    'status': 'waiting',
                                    'resource_id': (
                                        '44925534-adfe-4599-a3e6-a9cdbfa0b753'
                                    ),
                                    'requested_instant': {
                                        'max': 1646132815,
                                        'policy': 'interval_strict',
                                        'min': 1646131015,
                                    },
                                    'requested_instant_hr': (
                                        '2022-03-01T10:36:55.000000Z'
                                    ),
                                },
                                'type': 'ACTION',
                            },
                            {
                                'type': 'TRANSFER',
                                'transfer_details': {
                                    'semi_live_batching_allowed': False,
                                    'action_to_id': 191982,
                                    'node_from_id': (
                                        '0379ffc8-724e-4b80-bfee-924c20dc9f1c'
                                    ),
                                    'return_node_id': (
                                        '0379ffc8-724e-4b80-bfee-924c20dc9f1c'
                                    ),
                                    'waybill_planner_task_id': '',
                                    'output_carriage_id': '',
                                    'sharing_url': '',
                                    'is_allow_to_be_second_in_batching': True,
                                    'enabled': True,
                                    'next_planning_timestamp': 0,
                                    'transfer_id': (
                                        'a1a2e602-19b3-4977-abba-402eb9226ef6'
                                    ),
                                    'generation_tag_id': '',
                                    'live_batching_allowed': False,
                                    'batching_allowed': False,
                                    'input_carriage_id': '',
                                    'node_to_id': (
                                        'ef5dbc03-6e46-4849-b388-35ad201ea5a0'
                                    ),
                                    'is_allowed_to_be_in_taxi_batch': True,
                                    'is_rover_allowed': False,
                                    'external_order_id': '',
                                    'status': 'draft',
                                    'new_logistic_contract': False,
                                    'internal_place_id': (
                                        'd7632b53-873b-4171-bb3a-9feff6b0414b'
                                    ),
                                    'operator_id': 'taxi-external',
                                    'action_from_id': 191983,
                                },
                            },
                            {
                                'reservation_details': {
                                    'external_order_id': 'fake:d1d7452',
                                    'output_carriage_id': '',
                                    'internal_place_id': (
                                        'd7632b53-873b-4171-bb3a-9feff6b0414b'
                                    ),
                                    'node_id': (
                                        'ef5dbc03-6e46-4849-b388-35ad201ea5a0'
                                    ),
                                    'operator_id': 'external_operator',
                                    'reserve_take_ts': 1646154000,
                                    'reserve_put_ts': 1646143200,
                                    'input_carriage_id': '',
                                    'reservation_id': (
                                        '9e4f9ca1-4241-4388-a770-6cf3c2689c71'
                                    ),
                                    'status': 'approved',
                                },
                                'node_details': {
                                    'implementation': {
                                        'class_name': 'tmp',
                                        'coord': {
                                            'lat': 55.76815715,
                                            'lon': 37.63223287,
                                        },
                                        'details': {
                                            'street': 'Сретенка',
                                            'floor': '8',
                                            'geo_id': 213,
                                            'locality': 'Москва',
                                            'country': 'Россия',
                                            'porch': '404',
                                            'federal_district': (
                                                'Центральный федеральный округ'
                                            ),
                                            'house': '14',
                                            'metro': 'Пражская',
                                            'room': '303',
                                            'region': (
                                                'Москва и Московская область'
                                            ),
                                            'intercom': '007',
                                        },
                                    },
                                    'node_id': (
                                        'ef5dbc03-6e46-4849-b388-35ad201ea5a0'
                                    ),
                                    'need_input_electronic_certificate': False,
                                    'override_processing_interval': (
                                        '2022-03-01T14'
                                    ),
                                    'need_output_electronic_certificate': (
                                        False
                                    ),
                                    'is_deferred_courier': False,
                                    'public_output_carriage_id': '',
                                    'code': 'n_to',
                                    'branches_limit_for_place': 10,
                                    'visits_limit_for_place': 3,
                                },
                                'type': 'NODE',
                            },
                        ],
                    },
                ],
            },
        }


OFFERS_ENCRYPTION_SECRET_KEY = b'not_a_secret_testsuite_key______'

OFFERS_ENCRYPTION_MAGIC_BYTES = '1:'

OFFERS_ENCRYPTION_IV = base64.b64decode(b'28yjLr+bgEYXw6qe/6Q0KA==')

AES_BLOCK_SIZE = 16


@pytest.fixture(name='aes_encrypt')
def _aes_encrypt():
    def _wrapper(data):
        data = Padding.pad(data, AES_BLOCK_SIZE)
        cipher = AES.new(
            OFFERS_ENCRYPTION_SECRET_KEY,
            AES.MODE_CBC,
            iv=OFFERS_ENCRYPTION_IV,
        )
        encrypted = cipher.encrypt(data)
        return OFFERS_ENCRYPTION_MAGIC_BYTES + base64.b64encode(
            OFFERS_ENCRYPTION_IV + encrypted,
        ).decode('utf-8')

    return _wrapper


@pytest.fixture(name='aes_decrypt')
def _aes_decrypt():
    def _wrapper(data):
        data_payload = data[len(OFFERS_ENCRYPTION_MAGIC_BYTES) :]
        raw = base64.b64decode(data_payload)
        assert AES.block_size == AES_BLOCK_SIZE
        cipher = AES.new(
            OFFERS_ENCRYPTION_SECRET_KEY,
            AES.MODE_CBC,
            raw[: len(OFFERS_ENCRYPTION_IV)],
        )
        decrypted = cipher.decrypt(raw[AES_BLOCK_SIZE:])
        return Padding.unpad(decrypted, AES_BLOCK_SIZE).decode('utf-8')

    return _wrapper
