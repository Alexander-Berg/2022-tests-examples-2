# pylint: disable=C0302
import copy
import pytest
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util import Padding
from testsuite.utils import matching


DEFAULT_RESPONSE = {
    'estimations': [
        {
            'type': 'succeed',
            'price': '200.999',
            'taxi_tariff': 'express',
            'currency': 'RUB',
        },
        {
            'type': 'succeed',
            'price': '200.999',
            'taxi_tariff': 'cargo',
            'currency': 'RUB',
        },
    ],
}


ESTIMATE_PA_AUTH_CONTEXT = {
    'locale': 'en',
    'phone_pd_id': 'phone_pd_id_1',
    'user_id': 'some_user_id',
    'yandex_uid': 'yandex_uid',
}

DRAFT_PA_AUTH_CONTEXT = {
    'locale': 'en',
    'phone_pd_id': 'phone_pd_id_1',
    'user_id': 'some_user_id',
    'yandex_uid': 'yandex_uid',
    'user_agent': 'some_agent',
    'remote_ip': '1.1.1.1',
    'application': 'iphone',
}

SEARCH_SETTINGS = {
    'limit': 10,
    'max_distance': 15000,
    'max_route_distance': 15000,
    'max_route_time': 900,
}
FOUND_ETA = {
    'estimated_distance': 7067,
    'estimated_time': 778,
    'found': True,
    'search_settings': SEARCH_SETTINGS,
}
NOT_FOUND_ETA = {'found': False, 'search_settings': SEARCH_SETTINGS}


async def test_estimate_error(
        taxi_cargo_c2c,
        mockserver,
        pgsql,
        default_pa_headers,
        get_default_estimate_request,
):
    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc')
    def _cargo_pricing(request):
        return mockserver.make_response(
            json={'code': 'cant_construct_route', 'message': 'some message'},
            status=400,
        )

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=get_default_estimate_request(),
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'estimations': [
            {
                'error': {'code': 'bad_request'},
                'taxi_tariff': 'express',
                'type': 'failed',
            },
            {
                'error': {'code': 'bad_request'},
                'taxi_tariff': 'cargo',
                'type': 'failed',
            },
        ],
    }

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
    SELECT count(*)
    FROM cargo_c2c.offers
        """,
    )
    assert list(cursor) == [(0,)]


async def test_tariff_more_than_once(
        taxi_cargo_c2c, default_pa_headers, get_default_estimate_request,
):
    request = get_default_estimate_request()
    request['taxi_tariffs'] = [
        {'taxi_tariff': 'cargo'},
        {'taxi_tariff': 'cargo'},
    ]
    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 400


async def test_draft(
        taxi_cargo_c2c, pgsql, default_pa_headers, get_default_draft_request,
):
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/draft',
        json=get_default_draft_request(),
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
    SELECT offer_id, additional_delivery_description, pa_auth_context
    FROM cargo_c2c.orders
        """,
    )

    draft = get_default_draft_request()

    for point in draft['additional_delivery_description']['route_points']:
        point['contact']['phone_pd_id'] = '+79999999999_id'
        del point['contact']['phone']

    assert list(cursor) == [
        (
            'some id',
            draft['additional_delivery_description'],
            DRAFT_PA_AUTH_CONTEXT,
        ),
    ]


def _make_def_estimate_result(tariff):
    return {
        'currency': 'RUB',
        'offer_id': matching.uuid_string,
        'price': '200.999',
        'taxi_tariff': tariff,
        'type': 'succeed',
        'decision': 'order_allowed',
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_paid_supply_v2(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_estimate_request,
        mockserver,
        pgsql,
        mock_driver_eta,
):
    @mockserver.json_handler('/cargo-pricing/v2/taxi/add-paid-supply')
    def _paid_supply(request):
        assert request.json == {
            'calculations': [
                {
                    'calc_id': (
                        'cargo-pricing/v1/01234567890123456789012345678912'
                    ),
                    'expectations': {
                        'meters_to_arrive': 7067,
                        'seconds_to_arrive': 778,
                    },
                },
            ],
        }
        return {
            'calculations': [
                {
                    'calc_id': (
                        'cargo-pricing/v1/01234567890123456789012345678912'
                    ),
                    'result': {
                        'calc_id': (
                            'cargo-pricing/v1/01234567890123456789012345678912'
                        ),
                        'prices': {
                            'total_price': '259.999',
                            'paid_supply_price': '59.01',
                        },
                        'details': {
                            'algorithm': {
                                'pricing_case': 'paid_cancel_in_driving',
                            },
                            'currency': {'code': 'RUB'},
                            'services': [],
                            'waypoints': [],
                        },
                        'cancel_options': {
                            'paid_cancel_in_driving': {
                                'cancel_price': '59.01',
                                'free_cancel_timeout': 300,
                            },
                        },
                        'diagnostics': {},
                    },
                },
            ],
        }

    mock_driver_eta.mock_v2_eta_expected_request = {
        'airport': False,
        'classes': [
            {'class_name': 'cargo', 'is_extended_radius': True},
            {'class_name': 'express', 'is_extended_radius': True},
        ],
        'intent': 'eta',
        'payment_method': 'card',
        'provide_candidates': False,
        'requirements_by_classes': [
            {'classes': ['cargo'], 'requirements': {'a': '123', 'b': 123}},
            {'classes': ['express'], 'requirements': {'a': '123', 'b': 123}},
        ],
        'route_points': [[55.0, 55.0], [56.0, 56.0]],
        'zone_id': 'moscow',
        'future_offer_id': matching.uuid_string,
    }
    v2_response = copy.deepcopy(mock_driver_eta.v2_response)
    v2_response['classes']['express']['paid_supply_enabled'] = True
    mock_driver_eta.v2_response = v2_response

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=get_default_estimate_request(),
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'estimations': [
            {
                'currency': 'RUB',
                'offer_id': matching.uuid_string,
                'taxi_tariff': 'express',
                'price': '259.999',
                'paid_supply_price': '59.01',
                'paid_cancel_in_driving': {
                    'cancel_price': '59.01',
                    'free_cancel_timeout': 300,
                },
                'type': 'succeed',
                'decision': 'paid_supply_enabled',
            },
            _make_def_estimate_result('cargo'),
        ],
    }

    assert mock_driver_eta.mock_v2_eta.times_called == 1
    assert _paid_supply.times_called == 1

    driver_eta_request_link_id = mock_driver_eta.mock_v2_eta_expected_request[
        'future_offer_id'
    ]

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        f"""
    SELECT estimate_response, expectations, driver_eta_request_link_id
    FROM cargo_c2c.offers
        """,
    )
    assert list(cursor) == [
        (
            {
                'type': '',
                'currency': 'RUB',
                'offer_id': matching.uuid_string,
                'taxi_tariff': 'express',
                'price': '259.999',
                'paid_supply_price': '59.01',
                'paid_cancel_in_driving': {
                    'cancel_price': '59.01',
                    'free_cancel_timeout': 300,
                },
                'decision': 'paid_supply_enabled',
            },
            {'meters_to_arrive': 7067, 'seconds_to_arrive': 778},
            driver_eta_request_link_id,
        ),
        (
            {
                'type': '',
                'price': '200.999',
                'currency': 'RUB',
                'offer_id': matching.uuid_string,
                'taxi_tariff': 'cargo',
                'decision': 'order_allowed',
            },
            {'meters_to_arrive': 7067, 'seconds_to_arrive': 778},
            driver_eta_request_link_id,
        ),
    ]


@pytest.mark.experiments3(filename='experiment.json')
async def test_original_price(
        taxi_cargo_c2c,
        pgsql,
        default_pa_headers,
        get_default_estimate_request,
        mock_driver_eta,
        mock_cargo_pricing,
):
    mock_cargo_pricing.expected_v2_calc_request = {
        'calc_requests': [
            {
                'clients': [{'user_id': 'some_user_id'}],
                'homezone': 'moscow',
                'is_usage_confirmed': False,
                'payment_info': {
                    'coupon': 'lolita4747',
                    'method_id': 'card-123',
                    'type': 'card',
                },
                'price_for': 'client',
                'tariff_class': 'cargo',
                'taxi_requirements': {'a': '123', 'b': 123},
                'waypoints': [
                    {
                        'due': '2020-01-01T00:00:00+00:00',
                        'position': [55.0, 55.0],
                        'type': 'pickup',
                    },
                    {'position': [56.0, 56.0], 'type': 'dropoff'},
                ],
                'calc_strikeout_price': True,
                'discounts_enabled': True,
            },
            {
                'clients': [{'user_id': 'some_user_id'}],
                'homezone': 'moscow',
                'is_usage_confirmed': False,
                'payment_info': {
                    'coupon': 'lolita4747',
                    'method_id': 'card-123',
                    'type': 'card',
                },
                'price_for': 'client',
                'tariff_class': 'express',
                'waypoints': [
                    {
                        'due': '2020-01-01T00:00:00+00:00',
                        'position': [55.0, 55.0],
                        'type': 'pickup',
                    },
                    {'position': [56.0, 56.0], 'type': 'dropoff'},
                ],
                'calc_strikeout_price': True,
                'discounts_enabled': True,
            },
        ],
    }

    for _, calc in mock_cargo_pricing.v2_calc_response_data.items():
        calc['result']['prices']['strikeout_price'] = '300.999'

    request = get_default_estimate_request()
    del request['taxi_tariffs'][1]['taxi_requirements']
    request['delivery_description']['payment_info']['coupon'] = 'lolita4747'

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    assert mock_cargo_pricing.v2_calc_mock.times_called == 1
    resp = response.json()

    estimations = [
        _make_def_estimate_result('express'),
        _make_def_estimate_result('cargo'),
    ]
    estimations[0]['original_price'] = '300.999'
    estimations[1]['original_price'] = '300.999'
    assert resp == {'estimations': estimations}


async def test_original_price_no_experiment(
        taxi_cargo_c2c,
        pgsql,
        default_pa_headers,
        get_default_estimate_request,
        mock_driver_eta,
        mock_cargo_pricing,
):
    mock_cargo_pricing.expected_v2_calc_request = {
        'calc_requests': [
            {
                'clients': [{'user_id': 'some_user_id'}],
                'homezone': 'moscow',
                'is_usage_confirmed': False,
                'payment_info': {'method_id': 'card-123', 'type': 'card'},
                'price_for': 'client',
                'tariff_class': 'cargo',
                'taxi_requirements': {'a': '123', 'b': 123},
                'waypoints': [
                    {
                        'due': '2020-01-01T00:00:00+00:00',
                        'position': [55.0, 55.0],
                        'type': 'pickup',
                    },
                    {'position': [56.0, 56.0], 'type': 'dropoff'},
                ],
                'discounts_enabled': False,
            },
            {
                'clients': [{'user_id': 'some_user_id'}],
                'homezone': 'moscow',
                'is_usage_confirmed': False,
                'payment_info': {'method_id': 'card-123', 'type': 'card'},
                'price_for': 'client',
                'tariff_class': 'express',
                'taxi_requirements': {'a': '123', 'b': 123},
                'waypoints': [
                    {
                        'due': '2020-01-01T00:00:00+00:00',
                        'position': [55.0, 55.0],
                        'type': 'pickup',
                    },
                    {'position': [56.0, 56.0], 'type': 'dropoff'},
                ],
                'discounts_enabled': False,
            },
        ],
    }

    request = get_default_estimate_request()
    request['delivery_description']['payment_info']['coupon'] = 'lolita4747'

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert mock_cargo_pricing.v2_calc_mock.times_called == 1


async def test_driver_eta_unavalable(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_estimate_request,
        mockserver,
        pgsql,
):
    @mockserver.json_handler('/driver-eta/driver-eta/v2/eta')
    def _v2_eta(request):
        return mockserver.make_response(status=500)

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=get_default_estimate_request(),
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'estimations': [
            {
                'currency': 'RUB',
                'decision': 'no_cars_order_enabled',
                'offer_id': matching.uuid_string,
                'price': '200.999',
                'taxi_tariff': 'express',
                'type': 'succeed',
            },
            {
                'currency': 'RUB',
                'decision': 'no_cars_order_enabled',
                'offer_id': matching.uuid_string,
                'price': '200.999',
                'taxi_tariff': 'cargo',
                'type': 'succeed',
            },
        ],
    }

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        f"""
    SELECT expectations, driver_eta_request_link_id
    FROM cargo_c2c.offers
        """,
    )
    assert list(cursor) == [(None, None), (None, None)]


@pytest.mark.experiments3(filename='experiment.json')
async def test_cargocorp(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_estimate_request,
        mockserver,
):
    @mockserver.json_handler(
        '/cargo-finance/internal/cargo-finance/payment-methods/v1',
    )
    def _payment_methods(request):
        assert request.json == {'yandex_uid': 'yandex_uid'}
        return {
            'methods': [
                {
                    'id': 'cargocorp-1234',
                    'display': {
                        'type': 'some_type',
                        'image_tag': 'image_tag',
                        'title': 'title',
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

    request = get_default_estimate_request()
    request['delivery_description']['payment_info']['type'] = 'cargocorp'
    request['delivery_description']['payment_info']['id'] = 'cargocorp-1234'
    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200


@pytest.mark.experiments3(filename='experiment.json')
async def test_cargocorp_unavailable(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_estimate_request,
        mockserver,
):
    @mockserver.json_handler(
        '/cargo-finance/internal/cargo-finance/payment-methods/v1',
    )
    def _payment_methods(request):
        return {'methods': []}

    request = get_default_estimate_request()
    request['delivery_description']['payment_info']['type'] = 'cargocorp'
    request['delivery_description']['payment_info']['id'] = 'cargocorp-1234'
    print(request)
    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 400
    assert response.json() == {'code': 'payment_method_unavailable'}


async def test_combo_express_estimation(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_estimate_request,
        mock_cargo_pricing,
):
    mock_cargo_pricing.expected_v2_calc_request = {
        'calc_requests': [
            {
                'clients': [{'user_id': 'some_user_id'}],
                'homezone': 'moscow',
                'is_usage_confirmed': False,
                'payment_info': {'method_id': 'card-123', 'type': 'card'},
                'price_for': 'client',
                'tariff_class': 'cargo',
                'taxi_requirements': {'a': '123', 'b': 123},
                'waypoints': [
                    {
                        'due': '2020-01-01T00:00:00+00:00',
                        'position': [55.0, 55.0],
                        'type': 'pickup',
                    },
                    {'position': [56.0, 56.0], 'type': 'dropoff'},
                ],
                'discounts_enabled': False,
            },
            {
                'clients': [{'user_id': 'some_user_id'}],
                'homezone': 'moscow',
                'is_usage_confirmed': False,
                'payment_info': {'method_id': 'card-123', 'type': 'card'},
                'price_for': 'client',
                'tariff_class': 'express',
                'taxi_requirements': {'a': '123', 'b': 123},
                'waypoints': [
                    {
                        'due': '2020-01-01T00:00:00+00:00',
                        'position': [55.0, 55.0],
                        'type': 'pickup',
                    },
                    {'position': [56.0, 56.0], 'type': 'dropoff'},
                ],
                'discounts_enabled': False,
                'calculate_combo_prices': True,
            },
        ],
    }

    mock_cargo_pricing.v2_calc_response_data['express']['result'][
        'alternative_options_calcs'
    ] = (
        [
            {
                'type': 'combo',
                'alternative_price': '85.0000',
                'calc_id': 'cargo-pricing/v1/12345678912345678901234567890123',
            },
        ]
    )

    estimate_request = get_default_estimate_request()
    estimate_request['taxi_tariffs'][1]['alternative_option'] = {
        'type': 'combo',
    }

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=estimate_request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    assert response.json()['estimations'][1] == {
        'alternative_option': {'type': 'combo'},
        'currency': 'RUB',
        'decision': 'order_allowed',
        'offer_id': matching.uuid_string,
        'price': '85',
        'taxi_tariff': 'express',
        'type': 'succeed',
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_estimate_validation_distance(
        taxi_cargo_c2c,
        config_estimate_result_validation,
        default_pa_headers,
        get_default_estimate_request,
        mock_cargo_pricing,
):
    mock_cargo_pricing.v2_calc_response_data['express']['result']['details'][
        'trip_details'
    ] = {'total_distance_meter': '2000', 'total_time_second': '2'}

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=get_default_estimate_request(),
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    assert response.json() == {
        'estimations': [
            {
                'error': {'code': 'bad_request'},
                'taxi_tariff': 'express',
                'type': 'failed',
            },
            _make_def_estimate_result('cargo'),
        ],
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_estimate_validation_time(
        taxi_cargo_c2c,
        config_estimate_result_validation,
        default_pa_headers,
        get_default_estimate_request,
        mock_cargo_pricing,
):
    mock_cargo_pricing.v2_calc_response_data['cargo']['result']['details'][
        'trip_details'
    ] = {'total_distance_meter': '20', 'total_time_second': '920'}

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=get_default_estimate_request(),
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    assert response.json() == {
        'estimations': [
            _make_def_estimate_result('express'),
            {
                'error': {'code': 'bad_request'},
                'taxi_tariff': 'cargo',
                'type': 'failed',
            },
        ],
    }


@pytest.mark.config(
    CARGO_C2C_NDD_TARIFF_SETTINGS={
        'enabled': False,
        'package_size_mapping': [],
        'minimal_order_price': '350.000',
    },
)
async def test_ndd_disabled(
        taxi_cargo_c2c, default_pa_headers, get_default_ndd_estimate_request,
):
    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=get_default_ndd_estimate_request(),
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'estimations': [
            {
                'error': {'code': 'bad_request'},
                'taxi_tariff': 'ndd',
                'type': 'failed',
            },
        ],
    }


@pytest.mark.config(
    CARGO_C2C_NDD_TARIFF_SETTINGS={
        'enabled': True,
        'package_size_mapping': [],
        'minimal_order_price': '350.000',
        'ytpp_zone_names': ['delivery_ndd_zone'],
        'allowed_routes': {'moscow': ['moscow']},
    },
)
async def test_ndd_empty_package_size(
        taxi_cargo_c2c, default_pa_headers, get_default_ndd_estimate_request,
):
    request = get_default_ndd_estimate_request()
    request['taxi_tariffs'] = [{'taxi_tariff': 'ndd'}]
    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'estimations': [
            {
                'currency': 'RUB',
                'decision': 'minimal_price_offer',
                'offer_id': 'minimal_offer_stub',
                'price': '350',
                'taxi_tariff': 'ndd',
                'type': 'succeed',
            },
        ],
    }


@pytest.mark.config(
    CARGO_C2C_NDD_TARIFF_SETTINGS={
        'enabled': True,
        'package_size_mapping': [],
        'minimal_order_price': '350.000',
        'ytpp_zone_names': ['delivery_ndd_zone'],
        'allowed_routes': {'moscow': ['moscow']},
    },
)
async def test_ndd_no_package_size_in_config(
        taxi_cargo_c2c, default_pa_headers, get_default_ndd_estimate_request,
):
    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=get_default_ndd_estimate_request(),
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'estimations': [
            {
                'error': {'code': 'bad_request'},
                'taxi_tariff': 'ndd',
                'type': 'failed',
            },
        ],
    }


async def test_ndd_no_source_point_uri(
        taxi_cargo_c2c, default_pa_headers, get_default_ndd_estimate_request,
):
    request = get_default_ndd_estimate_request()
    request['delivery_description']['route_points'][0]['uri'] = 'another_uri'
    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'estimations': [
            {
                'error': {'code': 'dropoff_point_not_selected'},
                'taxi_tariff': 'ndd',
                'type': 'failed',
            },
        ],
    }


async def test_estimate_with_ndd(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_ndd_estimate_request,
        mockserver,
):
    @mockserver.json_handler(
        '/logistic-platform-uservices/api/c2c/platform/offers/create',
    )
    def _offers_create(request):
        assert request.json == {
            'info': {'operator_request_id': matching.AnyString()},
            'source': {
                'platform_station': {'platform_id': 'source_station_id'},
            },
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

    request = get_default_ndd_estimate_request()
    request['taxi_tariffs'].append(
        {'taxi_tariff': 'cargo', 'taxi_requirements': {'a': '123', 'b': 123}},
    )
    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    ndd_offer_id = response.json()['estimations'][1]['offer_id']
    assert ndd_offer_id.startswith('logistic-platform/')
    assert response.json() == {
        'estimations': [
            {
                'currency': 'RUB',
                'decision': 'order_allowed',
                'offer_id': matching.uuid_string,
                'price': '200.999',
                'taxi_tariff': 'cargo',
                'type': 'succeed',
            },
            {
                'currency': 'RUB',
                'decision': 'order_allowed',
                'offer_id': ndd_offer_id,
                'price': '239',
                'taxi_tariff': 'ndd',
                'type': 'succeed',
            },
        ],
    }


@pytest.mark.experiments3(filename='offers_encryption_enabled.json')
async def test_encrypted_offers(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_estimate_request,
        aes_decrypt,
        pgsql,
):
    request = get_default_estimate_request()

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    encrypted = response.json()['estimations'][0]['offer_id']
    decrypted = json.loads(aes_decrypt(encrypted))
    assert decrypted == {
        'offer_id': matching.uuid_string,
        'calc_id': matching.any_string,
        'estimate_response': {
            'type': '',
            'offer_id': matching.uuid_string,
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
            'application': 'iphone',
        },
        'expectations': {'seconds_to_arrive': 778, 'meters_to_arrive': 7067},
        'driver_eta_request_link_id': matching.uuid_string,
    }
    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
    SELECT count(*)
    FROM cargo_c2c.offers
        """,
    )
    assert list(cursor) == [(0,)]


@pytest.mark.experiments3(filename='offers_encryption_enabled.json')
async def test_encryption_does_not_affect_errors(
        taxi_cargo_c2c,
        mockserver,
        pgsql,
        default_pa_headers,
        get_default_estimate_request,
):
    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc')
    def _cargo_pricing(request):
        return mockserver.make_response(
            json={'code': 'cant_construct_route', 'message': 'some message'},
            status=400,
        )

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=get_default_estimate_request(),
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.json() == {
        'estimations': [
            {
                'error': {'code': 'bad_request'},
                'taxi_tariff': 'express',
                'type': 'failed',
            },
            {
                'error': {'code': 'bad_request'},
                'taxi_tariff': 'cargo',
                'type': 'failed',
            },
        ],
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_personal_wallet_success(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_estimate_request,
        mock_cargo_pricing,
        mockserver,
):
    request = get_default_estimate_request()
    request['delivery_description']['payment_info']['complements'] = [
        {
            'type': 'personal_wallet',
            'payment_method_id': 'w/7c4cbe75-9d33-5406-8830-258aeaa7f922',
        },
    ]

    mock_cargo_pricing.expected_v2_calc_request = {
        'calc_requests': [
            {
                'clients': [{'user_id': 'some_user_id'}],
                'homezone': 'moscow',
                'is_usage_confirmed': False,
                'payment_info': {
                    'method_id': 'card-123',
                    'type': 'card',
                    'complements': {
                        'personal_wallet': {
                            'balance': '204',
                            'method_id': (
                                'w/7c4cbe75-9d33-5406-8830-258aeaa7f922'
                            ),
                        },
                    },
                },
                'price_for': 'client',
                'tariff_class': 'cargo',
                'taxi_requirements': {'a': '123', 'b': 123},
                'waypoints': [
                    {
                        'due': '2020-01-01T00:00:00+00:00',
                        'position': [55.0, 55.0],
                        'type': 'pickup',
                    },
                    {'position': [56.0, 56.0], 'type': 'dropoff'},
                ],
                'calc_strikeout_price': True,
                'discounts_enabled': True,
            },
            {
                'clients': [{'user_id': 'some_user_id'}],
                'homezone': 'moscow',
                'is_usage_confirmed': False,
                'payment_info': {
                    'method_id': 'card-123',
                    'type': 'card',
                    'complements': {
                        'personal_wallet': {
                            'balance': '204',
                            'method_id': (
                                'w/7c4cbe75-9d33-5406-8830-258aeaa7f922'
                            ),
                        },
                    },
                },
                'price_for': 'client',
                'tariff_class': 'express',
                'taxi_requirements': {'a': '123', 'b': 123},
                'waypoints': [
                    {
                        'due': '2020-01-01T00:00:00+00:00',
                        'position': [55.0, 55.0],
                        'type': 'pickup',
                    },
                    {'position': [56.0, 56.0], 'type': 'dropoff'},
                ],
                'calc_strikeout_price': True,
                'discounts_enabled': True,
            },
        ],
    }

    @mockserver.json_handler('/plus-wallet/v1/balances')
    def _plus_wallet_mock(request):
        assert request.query['yandex_uid'] == 'yandex_uid'
        assert request.query['currencies'] == 'RUB'
        return {
            'balances': [
                {
                    'balance': '204.0000',
                    'currency': 'RUB',
                    'wallet_id': 'w/7c4cbe75-9d33-5406-8830-258aeaa7f922',
                },
            ],
        }

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert _plus_wallet_mock.times_called == 1


@pytest.mark.experiments3(filename='experiment.json')
async def test_personal_wallet_empty(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_estimate_request,
        mock_cargo_pricing,
        mockserver,
):
    request = get_default_estimate_request()
    request['delivery_description']['payment_info']['complements'] = [
        {
            'type': 'personal_wallet',
            'payment_method_id': 'w/7c4cbe75-9d33-5406-8830-258aeaa7f922',
        },
    ]

    mock_cargo_pricing.expected_v2_calc_request = {
        'calc_requests': [
            {
                'clients': [{'user_id': 'some_user_id'}],
                'homezone': 'moscow',
                'is_usage_confirmed': False,
                'payment_info': {'method_id': 'card-123', 'type': 'card'},
                'price_for': 'client',
                'tariff_class': 'cargo',
                'taxi_requirements': {'a': '123', 'b': 123},
                'waypoints': [
                    {
                        'due': '2020-01-01T00:00:00+00:00',
                        'position': [55.0, 55.0],
                        'type': 'pickup',
                    },
                    {'position': [56.0, 56.0], 'type': 'dropoff'},
                ],
                'calc_strikeout_price': True,
                'discounts_enabled': True,
            },
            {
                'clients': [{'user_id': 'some_user_id'}],
                'homezone': 'moscow',
                'is_usage_confirmed': False,
                'payment_info': {'method_id': 'card-123', 'type': 'card'},
                'price_for': 'client',
                'tariff_class': 'express',
                'taxi_requirements': {'a': '123', 'b': 123},
                'waypoints': [
                    {
                        'due': '2020-01-01T00:00:00+00:00',
                        'position': [55.0, 55.0],
                        'type': 'pickup',
                    },
                    {'position': [56.0, 56.0], 'type': 'dropoff'},
                ],
                'calc_strikeout_price': True,
                'discounts_enabled': True,
            },
        ],
    }

    @mockserver.json_handler('/plus-wallet/v1/balances')
    def _plus_wallet_mock(request):
        assert request.query['yandex_uid'] == 'yandex_uid'
        assert request.query['currencies'] == 'RUB'
        return {
            'balances': [
                {
                    'balance': '0.0000',
                    'currency': 'RUB',
                    'wallet_id': 'w/7c4cbe75-9d33-5406-8830-258aeaa7f922',
                },
            ],
        }

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert _plus_wallet_mock.times_called == 1
