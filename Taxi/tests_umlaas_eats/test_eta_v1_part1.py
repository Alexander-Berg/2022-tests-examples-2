# pylint: disable=C0302
import datetime
import json
from urllib import parse as urlparse

import pytest


URL = '/umlaas-eats/v1/eta'
EXP_USER_ID = '1184610'
EXP_DEVICE_ID = 'BC5B7039-40C3-46F5-9D10-2B539DC0B730'
CONSUMER = 'umlaas-eats-eta'


@pytest.fixture(name='grocery_eta')
def _grocery_eta(mockserver):
    @mockserver.json_handler(
        '/umlaas-grocery-eta/internal/umlaas-grocery-eta/v1/delivery-eta',
    )
    def _umlaas_grocery_eta(request):
        return {
            'total_time': 0,
            'cooking_time': 0,
            'delivery_time': 0,
            'promise': {'min': 10 * 60, 'max': 20 * 60},
        }


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


async def test_grocery_default_with_headers(
        taxi_umlaas_eats, load, grocery_eta,
):
    request_body = load('grocery_request.json')
    params = get_query_params(place_type='lavka')
    del params['user_id']
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}',
        data=request_body,
        headers={
            'X-YaTaxi-User': (
                'some_other=other_value,eats_user_id='
                + f'{EXP_USER_ID},some_other=other_value'
            ),
        },
    )
    assert response.status == 200

    predicted_times = response.json()['predicted_times']
    assert predicted_times
    assert len(predicted_times) == len(
        json.loads(request_body)['requested_times'],
    )


async def test_eats_default(taxi_umlaas_eats, load):
    request_body = load('eats_request.json')
    params = get_query_params()
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )
    assert response.status == 200
    data = json.loads(response.text)

    for predicted_times in data['predicted_times']:
        assert predicted_times['times']['total_time'] >= 0
        assert predicted_times['times']['cooking_time'] >= 0
        assert predicted_times['times']['delivery_time'] >= 0
        assert predicted_times['times']['boundaries']['min'] >= 0
        assert predicted_times['times']['boundaries']['max'] >= 0

    assert len(data['predicted_times']) == len(
        json.loads(request_body)['requested_times'],
    )


async def test_eats_request_validation(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    del request_body['requested_times'][0]['place']['average_user_rating']
    params = get_query_params()
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 400
    data = json.loads(response.text)
    assert data['message'] == 'no average_user_rating '


CUSTOM_BRAND_SHIFT = 5


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
        'predictor_main_component': 'taken',
    },
)
@exp3_decorator(
    name='umlaas_eats_custom_eta_setting',
    value={
        'tag': 'custom_eta_setting',
        'custom_brands': [],
        'custom_places': [
            {
                'id': 321075,
                'min_delta_cooking_time': 0,
                'max_delta_cooking_time': 100,
                'shift_total_time': CUSTOM_BRAND_SHIFT,
            },
        ],
    },
)
async def test_eats_ml(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params()
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)

    default_times = request_body['requested_times'][0]['default_times']
    assert (
        default_times['delivery_time']
        == data['predicted_times'][0]['times']['delivery_time']
    )
    assert (
        data['predicted_times'][0]['times']['delivery_time']
        + data['predicted_times'][0]['times']['cooking_time']
        + CUSTOM_BRAND_SHIFT
        == data['predicted_times'][0]['times']['total_time']
    )

    assert data['predicted_times'][0]['times']['cooking_time'] == 10
    assert data['predicted_times'][0]['times']['delivery_time'] == 18
    # be aware of rounding to 5
    assert (
        data['predicted_times'][0]['times']['boundaries']['min']
        == 30 + CUSTOM_BRAND_SHIFT
    )


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 5,
        'shift_cooking_time': 2,
        'custom_brands': [],
        'shift_const_cooking_time': 1,
        'proxy_umlaas_eats': True,
        'ready_predictor_enabled': True,
        'predictor_main_component': 'taken',
    },
)
async def test_eats_ml_slug(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params(request_type='slug')
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)

    default_times = request_body['requested_times'][0]['default_times']
    assert (
        default_times['delivery_time']
        == data['predicted_times'][0]['times']['delivery_time']
    )
    assert (
        data['predicted_times'][0]['times']['delivery_time']
        + data['predicted_times'][0]['times']['cooking_time']
        == data['predicted_times'][0]['times']['total_time']
    )
    assert (
        data['predicted_times'][0]['times']['cooking_time']
        == 21.033333333333335 + 1
    )
    assert data['predicted_times'][0]['times']['delivery_time'] == 18
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 40


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
        'couriers_candidates_parameters': {
            'enabled': True,
            'catalog_enabled': True,
            'slug_enabled': True,
            'using_type': 'average',
            'dropoff_add': 300,
            'take_add': 100,
            'tempo': 1000,
            'eda_couriers_penalty': 0,
            'other_lavka_couriers_penalty': 0,
            'shop_couriers_penalty': 900,
            'to_place_statuses': ['created', 'accepted', 'arrived_to_source'],
            'probability_of_batch': 0.5,
            'top_to_account': 3,
            'global_limit': 1800,
            'extra_time': 30,
        },
        'ready_predictor_enabled': True,
        'predictor_main_component': 'taken',
    },
)
async def test_eats_ml_with_heuristic(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params()
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)

    default_times = request_body['requested_times'][0]['default_times']
    assert (
        default_times['delivery_time']
        != data['predicted_times'][0]['times']['delivery_time']
    )
    assert (
        data['predicted_times'][0]['times']['delivery_time']
        + data['predicted_times'][0]['times']['cooking_time']
        == data['predicted_times'][0]['times']['total_time']
    )
    assert data['predicted_times'][0]['times']['cooking_time'] == 10
    assert (
        data['predicted_times'][0]['times']['delivery_time']
        == 26.116666666666667
    )
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 40


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
        'ready_predictor_enabled': False,
        'total_predictor_enabled': False,
        'predictor_main_component': 'taken',
        'region_offset': -10,
    },
)
async def test_eats_ml_total_model(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params()
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)

    default_times = request_body['requested_times'][0]['default_times']
    assert (
        default_times['delivery_time']
        == data['predicted_times'][0]['times']['delivery_time']
    )
    assert (
        data['predicted_times'][0]['times']['delivery_time']
        + data['predicted_times'][0]['times']['cooking_time']
        == data['predicted_times'][0]['times']['total_time']
    )
    assert data['predicted_times'][0]['times']['cooking_time'] == 10
    assert data['predicted_times'][0]['times']['delivery_time'] == 18
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 20


async def test_grocery_eta_ml_model(taxi_umlaas_eats, load_json, grocery_eta):
    request_body = load_json('grocery_request.json')
    params = get_query_params(place_type='lavka')

    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data)

    await taxi_umlaas_eats.enable_testpoints()

    for predicted_times in data['predicted_times']:
        boundary_max = predicted_times['times']['boundaries']['max']
        boundary_min = predicted_times['times']['boundaries']['min']
        assert boundary_max - boundary_min == 10


@exp3_decorator(
    name='eats_retail_eta_ml',
    value={
        'tag': 'eta_retail_ml',
        'slug': 'const',
        'enabled': True,
        'retail_model_enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'predictor_main_component': 'taken',
    },
)
async def test_eats_retail_ml(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params(place_type='shop')

    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)

    default_times = request_body['requested_times'][0]['default_times']
    assert (
        default_times['delivery_time']
        == data['predicted_times'][0]['times']['delivery_time']
    )
    assert (
        data['predicted_times'][0]['times']['delivery_time']
        + data['predicted_times'][0]['times']['cooking_time']
        == data['predicted_times'][0]['times']['total_time']
    )
    assert data['predicted_times'][0]['times']['cooking_time'] == 10
    assert data['predicted_times'][0]['times']['delivery_time'] == 18
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 30


@pytest.mark.config(
    EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': ['93333']},
)
@exp3_decorator(
    name='eats_retail_eta_ml',
    value={
        'tag': 'eta_retail_ml',
        'slug': 'const',
        'enabled': True,
        'retail_model_enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'predictor_main_component': 'none',
        'slots_params': {'shift': 7, 'const_shift': 3},
    },
)
async def test_eats_retail_ml_slots_checkout(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    # let's make order asap with respect to 'now()'
    request_body['predicting_at'] = (
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=5)
    ).isoformat()
    params = get_query_params(place_type='shop', request_type='checkout')

    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)

    assert data['predicted_times'][0]['times']['cooking_time'] == 10
    assert data['predicted_times'][0]['times']['delivery_time'] == 18
    # total_time = time_to_slot + delivery_time + shift
    assert data['predicted_times'][0]['times']['total_time'] == 15 + 18 + 7


@exp3_decorator(
    name='eats_retail_eta_ml',
    value={
        'tag': 'eta_retail_ml',
        'slug': 'const',
        'enabled': True,
        'retail_model_enabled': True,
        'taxi_routing_enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'region_taxi_shifts': [
            {'region_id': 321, 'taxi_shift': 10},
            {'region_id': 123, 'taxi_shift': 5},
        ],
        'shift_const_cooking_time': 0,
        'predictor_main_component': 'none',
    },
)
async def test_custom_region_shifts_checkout(
        taxi_umlaas_eats, load_json, mockserver,
):
    @mockserver.json_handler('/eats-eta/v1/eta')
    def _mock_eats_eta(request):
        assert len(request.json['sources']) == 1
        return {'etas': [{'time': 17 * 60, 'distance': 6600}]}

    request_body = load_json('eats_request.json')
    # request_body['requested_times'][0]['id'] = 919191
    request_body['requested_times'][0]['place']['courier_type'] = 'yandex_taxi'
    params = get_query_params(place_type='shop', request_type='checkout')

    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)

    assert data['predicted_times'][0]['times']['cooking_time'] == 10
    assert data['predicted_times'][0]['times']['delivery_time'] == 17 + 5
    assert data['predicted_times'][0]['times']['total_time'] == 10 + 17 + 5


@exp3_decorator(
    name='eats_retail_eta_ml',
    value={
        'tag': 'eta_retail_ml',
        'slug': 'const',
        'enabled': True,
        'retail_model_enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'predictor_main_component': 'taken',
        'rounding_params': {
            'multiple_params': [{'threshold': 15, 'closest_value': 15}],
        },
    },
)
async def test_eats_rounding(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params(place_type='shop')

    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)
    # Total time should be rounded to 30-45 min interval:
    # 29 -> 30 -> 30-45
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 30
    assert data['predicted_times'][0]['times']['boundaries']['max'] == 45


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'predictor_main_component': None,
    },
)
async def test_eats_eta_resource_versioning_rest_default(
        taxi_umlaas_eats, testpoint, load,
):
    @testpoint('eats-eta-resource-versioning')
    def _tp(data):
        pass

    # send any request to activate testpoint
    request_body = load('eats_request.json')
    params = get_query_params()
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )

    assert response.status == 200

    await taxi_umlaas_eats.enable_testpoints()
    tp_response = await _tp.wait_call()

    # default restaurant models and statistics
    data = tp_response['data']
    assert data['loaded_model_resources'] == 'eats_eta_models 0'
    assert data['loaded_static_resources'] == 'eats_eta_statistics 0'


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'predictor_main_component': None,
        'static_resource_version_min': '1',
    },
)
async def test_eats_eta_resource_versioning_rest_other_version(
        taxi_umlaas_eats, testpoint, load,
):
    @testpoint('eats-eta-resource-versioning')
    def _tp(data):
        pass

    # send any request to activate testpoint
    request_body = load('eats_request.json')
    params = get_query_params()
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )

    assert response.status == 200

    await taxi_umlaas_eats.enable_testpoints()
    tp_response = await _tp.wait_call()

    # custom versions from exp
    data = tp_response['data']
    assert data['loaded_model_resources'] == 'eats_eta_models 0'
    assert data['loaded_static_resources'] == 'eats_eta_statistics 1'


@exp3_decorator(
    name='eats_retail_eta_ml',
    value={
        'tag': 'eta_retail_ml',
        'slug': 'const',
        'enabled': True,
        'retail_model_enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'predictor_main_component': 'taken',
        'model_version_min': 'courier_features',
        'static_resource_version_min': '1',  # no such version
    },
)
async def test_eats_eta_resource_versioning_retail_incorrect_version(
        taxi_umlaas_eats, testpoint, load_json,
):
    @testpoint('eats-eta-resource-versioning')
    def _tp(data):
        pass

    # send any request to activate testpoint
    request_body = load_json('eats_request.json')
    params = get_query_params(place_type='shop')

    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200

    await taxi_umlaas_eats.enable_testpoints()
    tp_response = await _tp.wait_call()

    # default model in case of fail, but custom static resources
    data = tp_response['data']
    assert (
        data['loaded_model_resources']
        == 'eats_retail_eta_models courier_features'
    )
    assert data['loaded_static_resources'] == 'eats_retail_eta_statistics 0'


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 5,
        'shift_cooking_time': 2,
        'custom_brands': [],
        'shift_const_cooking_time': 1,
        'proxy_umlaas_eats': True,
        'ready_predictor_enabled': True,
        'predictor_main_component': 'taken',
    },
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'brand': {
                'id': 93333,
                'name': 'noname',
                'picture_scale_type': 'aspect_fit',
                'slug': 'noname',
            },
            'business': 'restaurant',
            'features': {
                'fast_food': False,
                'ignore_surge': False,
                'supports_preordering': True,
            },
            'id': 321075,
            'slug': 'slug0',
            'location': {'geo_point': [37.54232, 55.791714]},
            'new_rating': {'rating': 4.76, 'show': True},
            'price_category': {'id': 1, 'name': '$', 'value': 1},
            'rating': {'admin': 1, 'count': 200, 'shown': 4.8, 'users': 4.76},
            'revision_id': 1000,
            'sorting': {'popular': 0, 'weight': 100},
            'timing': {
                'average_preparation': 0,
                'extra_preparation': 0,
                'preparation': 0,
            },
            'type': 'native',
            'updated_at': '2021-07-29T20:45:23+03:00',
        },
    ],
)
async def test_eats_catalog_storage_cache(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request_for_cache.json')
    params = get_query_params(request_type='slug')
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )

    assert response.status == 200

    data = response.json()

    predicted_times = data['predicted_times'][0]['times']
    default_times = request_body['requested_times'][0]['default_times']

    assert default_times['delivery_time'] == predicted_times['delivery_time']
    assert (
        predicted_times['delivery_time'] + predicted_times['cooking_time']
        == predicted_times['total_time']
    )
    assert predicted_times['cooking_time'] == 21.033333333333335 + 1
    assert predicted_times['delivery_time'] == 18
    assert predicted_times['boundaries']['min'] == 40


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
async def test_eats_eta_linear_slug_checkout(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params(request_type='slug')
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )

    assert response.status == 200

    data = response.json()

    predicted_times = data['predicted_times'][0]['times']
    default_times = request_body['requested_times'][0]['default_times']

    assert (
        predicted_times['delivery_time']
        == default_times['delivery_time']
        == 18
    )
    assert predicted_times['cooking_time'] == 21.033333333333335
    assert predicted_times['total_time'] == 37.923780905067105
    assert predicted_times['boundaries']['min'] == 40
    assert predicted_times['boundaries']['max'] == 60

    params = get_query_params(request_type='default')
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )

    assert response.status == 200

    data = response.json()

    predicted_times = data['predicted_times'][0]['times']
    default_times = request_body['requested_times'][0]['default_times']

    assert (
        predicted_times['delivery_time']
        == default_times['delivery_time']
        == 18
    )
    assert predicted_times['cooking_time'] == 10
    assert predicted_times['total_time'] == 37.923780905067105
    assert predicted_times['boundaries']['min'] == 40
    assert predicted_times['boundaries']['max'] == 60


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml/default',
        'slug': 'const',
        'enabled': True,
        'custom_brands': [],
        'shift_total_time': 4.8,
        'model_version_min': '0',
        'shift_cooking_time': -2,
        'shift_delivery_time': 0,
        'ready_predictor_enabled': True,
        'total_predictor_enabled': True,
        'predictor_main_component': 'none',
        'shift_const_cooking_time': 0,
        'shift_taxi_delivery_time': 10,
    },
)
@exp3_decorator(name='eats_eta_exploration', value={})
async def test_eats_ml_exploration_empty_exp(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params()
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert data


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml/default',
        'slug': 'const',
        'enabled': True,
        'custom_brands': [],
        'shift_total_time': 4.8,
        'model_version_min': '0',
        'shift_cooking_time': -2,
        'shift_delivery_time': 0,
        'ready_predictor_enabled': True,
        'total_predictor_enabled': True,
        'predictor_main_component': 'none',
        'shift_const_cooking_time': 0,
        'shift_taxi_delivery_time': 10,
    },
)
@exp3_decorator(
    name='eats_eta_exploration',
    value={
        'cooking_noise': {
            'enabled': True,
            'salt': '',
            'distribution_type': 'uniform',
            'min': -5,
            'max': 5,
        },
        'delivery_noise': {},
        'total_noise': {},
    },
)
async def test_eats_ml_exploration(taxi_umlaas_eats, load_json):
    request_body = load_json('eats_request.json')
    params = get_query_params()
    response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert data['predicted_times'][0]['times']['total_time'] == 14.8
    assert data['predicted_times'][0]['times']['delivery_time'] == 18
    assert (
        data['predicted_times'][0]['times']['cooking_time'] == 5.26716228
    )  # = 8.0+-2.73283772
