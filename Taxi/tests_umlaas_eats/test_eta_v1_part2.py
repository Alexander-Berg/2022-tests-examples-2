# pylint: disable=C0302
import json
from urllib import parse as urlparse

import pytest

URL = '/umlaas-eats/v1/eta'
EXP_USER_ID = '1184610'
EXP_DEVICE_ID = 'BC5B7039-40C3-46F5-9D10-2B539DC0B730'
CONSUMER = 'umlaas-eats-eta'


def get_query_params(place_type='default', request_type='default'):
    params = dict(
        service_name='test',
        request_id='test_request_id',
        user_id=EXP_USER_ID,
        device_id=EXP_DEVICE_ID,
        place_type=place_type,
        request_type=request_type,
    )
    return params


def exp3_decorator(name, value):
    return pytest.mark.experiments3(
        name=name,
        consumers=[CONSUMER],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=value,
    )


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'retail_model_enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'shift_const_cooking_time': 0,
        'predictor_main_component': 'none',
        'boundary_shifts': {
            'type_catalog': {'min': 0, 'max': 0},
            'type_slug': {'min': -3, 'max': 1},
            'type_default': {'min': -2, 'max': 2},
            'type_checkout': {'min': -1, 'max': 3},
        },
    },
)
async def test_boundaries_shift(taxi_umlaas_eats, load_json):
    # 40-60 is a default for slug, 30-50 for default and checkout
    request_body = load_json('eats_request.json')

    params = get_query_params(request_type='slug')
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 40 - 3
    assert data['predicted_times'][0]['times']['boundaries']['max'] == 60 + 1

    params = get_query_params(request_type='default')
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 30 - 2
    assert data['predicted_times'][0]['times']['boundaries']['max'] == 50 + 2

    params = get_query_params(request_type='checkout')
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 30 - 1
    assert data['predicted_times'][0]['times']['boundaries']['max'] == 50 + 3


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'retail_model_enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'shift_const_cooking_time': 0,
        'predictor_main_component': 'none',
        'boundary_shifts': {
            'type_catalog': {'min': 0, 'max': 0},
            'type_slug': {'min': -3, 'max': 1},
            'type_default': {'min': -2, 'max': 2},
            'type_checkout': {'min': -40, 'max': 3},
        },
    },
)
async def test_boundaries_shift_possible_bugs(taxi_umlaas_eats, load_json):
    # 40-60 is a default for slug, 30-50 for default and checkout
    request_body = load_json('eats_request.json')

    params = get_query_params(request_type='checkout')
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)
    # 29 -> 30 -> (30, 50) -> (-10, 53) -> (10, 73)
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 10
    assert data['predicted_times'][0]['times']['boundaries']['max'] == 73


@pytest.mark.experiments3(
    name='umlaas_eats_delivery_class',
    consumers=['umlaas-eats-delivery-class'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Fast delivery',
            'predicate': {
                'init': {
                    'arg_name': 'delivery_class',
                    'arg_type': 'string',
                    'value': 'fast',
                },
                'type': 'eq',
            },
            'enabled': True,
            'value': {'promice_add': -300},
        },
        {
            'title': 'Regular delivery',
            'predicate': {
                'init': {
                    'arg_name': 'delivery_class',
                    'arg_type': 'string',
                    'value': 'regular',
                },
                'type': 'eq',
            },
            'enabled': True,
            'value': {'promice_add': 180},
        },
        {
            'title': 'Slow delivery',
            'predicate': {
                'init': {
                    'arg_name': 'delivery_class',
                    'arg_type': 'string',
                    'value': 'slow',
                },
                'type': 'eq',
            },
            'enabled': True,
            'value': {'promice_add': 300},
        },
    ],
    default_value={'promice_add': -100},  # should not be used
    is_config=True,
)
@exp3_decorator(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'retail_model_enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'shift_const_cooking_time': 0,
        'predictor_main_component': 'none',
    },
)
async def test_delivery_class(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')

    # regular
    params = get_query_params(request_type='checkout')
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 30 + 3
    assert data['predicted_times'][0]['times']['boundaries']['max'] == 50 + 3

    # fast
    request_body['requested_times'][0]['place']['delivery_class'] = 'fast'
    params = get_query_params(request_type='checkout')
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 30 - 5
    assert data['predicted_times'][0]['times']['boundaries']['max'] == 50 - 5

    # slow
    request_body['requested_times'][0]['place']['delivery_class'] = 'slow'
    params = get_query_params(request_type='checkout')
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 30 + 5
    assert data['predicted_times'][0]['times']['boundaries']['max'] == 50 + 5


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': True,
        'ready_predictor_enabled': True,
        'slug_model': 'linear',
        'cart_model': 'linear',
        'change_eta_for_cart_items': True,
    },
)
@pytest.mark.experiments3(
    name='umlaas_eats_eta_cart_impact',
    consumers=['umlaas-eats-eta-cart-impact'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'enabled': True,
        'num_nonaffecting_items': 3,
        'num_items_for_change': 2,
    },
)
@exp3_decorator(
    name='umlaas_eats_catalog_linear_model',
    value={
        'enabled': True,
        'model_coefficients': [
            36.3359,  # const
            4.4970,  # delivery
            3.1916,  # delivery ** 2
            -1.1451,  # delivery ** 0.5
            2.6867,  # cooking this round hour of day
            2.9591,  # cooking this day of week
            -2.8298,  # fast food and rating
            -3.6305,  # non fast food and rating
        ],
        'scaler_means': [
            0.0,
            21.1785,
            522.8603,
            4.5004,
            23.9363,
            23.7005,
            2.3352,
            2.2766,
        ],
        'scaler_scales': [
            1.0,
            8.6216,
            431.1709,
            0.9619,
            6.4042,
            6.3776,
            2.2667,
            2.3633,
        ],
        'min_prediction_value': 10,
        'max_prediction_value': 180,
    },
)
async def test_eta_cart_impact(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params(request_type='default')

    cart = request_body['requested_times'][0]['cart'][:]
    responses = []

    for i in range(1, len(cart) + 1):
        request_body['requested_times'][0]['cart'] = cart[:i]
        response = await taxi_umlaas_eats.post(
            f'{URL}?{urlparse.urlencode(params)}',
            data=json.dumps(request_body),
        )
        assert response.status == 200
        responses.append(
            json.loads(response.text)['predicted_times'][0]['times'][
                'boundaries'
            ],
        )

    assert responses == [
        {'min': 40, 'max': 60},
        {'min': 40, 'max': 60},
        {'min': 40, 'max': 60},
        {'min': 45, 'max': 65},
        {'min': 45, 'max': 65},
        {'min': 50, 'max': 70},
    ]


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': True,
        'ready_predictor_enabled': True,
        'slug_model': 'linear',
        'cart_model': 'cached',
        'change_eta_for_cart_items': True,
    },
)
@pytest.mark.experiments3(
    name='umlaas_eats_eta_cart_impact',
    consumers=['umlaas-eats-eta-cart-impact'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'enabled': True,
        'num_nonaffecting_items': 3,
        'num_items_for_change': 2,
    },
)
@exp3_decorator(
    name='umlaas_eats_catalog_linear_model',
    value={
        'enabled': True,
        'model_coefficients': [
            36.3359,  # const
            4.4970,  # delivery
            3.1916,  # delivery ** 2
            -1.1451,  # delivery ** 0.5
            2.6867,  # cooking this round hour of day
            2.9591,  # cooking this day of week
            -2.8298,  # fast food and rating
            -3.6305,  # non fast food and rating
        ],
        'scaler_means': [
            0.0,
            21.1785,
            522.8603,
            4.5004,
            23.9363,
            23.7005,
            2.3352,
            2.2766,
        ],
        'scaler_scales': [
            1.0,
            8.6216,
            431.1709,
            0.9619,
            6.4042,
            6.3776,
            2.2667,
            2.3633,
        ],
        'min_prediction_value': 10,
        'max_prediction_value': 180,
    },
)
async def test_eta_cart_impact_with_cached_times(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params(request_type='default')

    cart = request_body['requested_times'][0]['cart'][:]
    responses = []

    for i in range(1, len(cart) + 1):
        request_body['requested_times'][0]['cart'] = cart[:i]
        response = await taxi_umlaas_eats.post(
            f'{URL}?{urlparse.urlencode(params)}',
            data=json.dumps(request_body),
        )
        assert response.status == 200
        responses.append(
            json.loads(response.text)['predicted_times'][0]['times'][
                'boundaries'
            ],
        )

    assert responses == [
        {'min': 35, 'max': 45},
        {'min': 35, 'max': 45},
        {'min': 35, 'max': 45},
        {'min': 40, 'max': 50},
        {'min': 40, 'max': 50},
        {'min': 45, 'max': 55},
    ]

    del request_body['requested_times'][0]['prediction_no_cart']
    responses = []

    for i in range(1, len(cart) + 1):
        request_body['requested_times'][0]['cart'] = cart[:i]
        response = await taxi_umlaas_eats.post(
            f'{URL}?{urlparse.urlencode(params)}',
            data=json.dumps(request_body),
        )
        assert response.status == 200
        responses.append(
            json.loads(response.text)['predicted_times'][0]['times'][
                'boundaries'
            ],
        )

    assert responses == [
        {'min': 40, 'max': 60},
        {'min': 40, 'max': 60},
        {'min': 40, 'max': 60},
        {'min': 45, 'max': 65},
        {'min': 45, 'max': 65},
        {'min': 50, 'max': 70},
    ]


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': True,
        'ready_predictor_enabled': True,
        'slug_model': 'linear',
        'cart_model': 'linear',
    },
)
@exp3_decorator(
    name='umlaas_eats_catalog_linear_model',
    value={
        'enabled': True,
        'model_coefficients': [
            36.3359,  # const
            4.4970,  # delivery
            3.1916,  # delivery ** 2
            -1.1451,  # delivery ** 0.5
            2.6867,  # cooking this round hour of day
            2.9591,  # cooking this day of week
            -2.8298,  # fast food and rating
            -3.6305,  # non fast food and rating
        ],
        'scaler_means': [
            0.0,
            21.1785,
            522.8603,
            4.5004,
            23.9363,
            23.7005,
            2.3352,
            2.2766,
        ],
        'scaler_scales': [
            1.0,
            8.6216,
            431.1709,
            0.9619,
            6.4042,
            6.3776,
            2.2667,
            2.3633,
        ],
        'min_prediction_value': 10,
        'max_prediction_value': 180,
    },
)
@exp3_decorator(
    name='umlaas_eats_custom_eta_setting',
    value={
        'custom_brands': [],
        'custom_places': [{'id': 321075, 'max_total_time': 20}],
    },
)
async def test_custom_eta_limits(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params(request_type='default')

    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )

    assert response.status == 200
    assert (
        json.loads(response.text)['predicted_times'][0]['times']['total_time']
        == 20
    )
