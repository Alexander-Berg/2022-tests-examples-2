# pylint: disable=C0302
import json
from urllib import parse as urlparse
from tests_umlaas_eats import experiments

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
        consumers=[CONSUMER, experiments.CONSUMER_CATALOG_V1],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=value,
    )


# shortcut for data in catalog storage
PLACE2BRAND = {
    3621: {'brand': 3179, 'is_ff': False},
    76511: {'brand': 20369, 'is_ff': False},
    56622: {'brand': -100, 'is_ff': False},
    36575: {'brand': -200, 'is_ff': False},
    24938: {'brand': 11787, 'is_ff': False},
    44419: {'brand': -100, 'is_ff': False},
    11271: {'brand': -300, 'is_ff': False},
    24968: {'brand': 1693, 'is_ff': False},
    3265: {'brand': 2777, 'is_ff': False},
    10479: {'brand': 8577, 'is_ff': False},
    10465: {'brand': 8577, 'is_ff': False},
}

# create slug requests identical to catalog requests
def create_slug_request(catalog_place, catalog_time, catalog_loc):
    return {
        'predicting_at': catalog_time,
        'requested_times': [
            {
                'default_times': {
                    'boundaries': {
                        'max': catalog_place['eta_minutes_max'],
                        'min': catalog_place['eta_minutes_min'],
                    },
                    'cooking_time': 0,
                    'delivery_time': catalog_place['time_to_delivery'],
                    'total_time': 0,
                },
                'id': catalog_place['id'],
                'place': {
                    'average_preparation_time': catalog_place[
                        'average_preparation_time'
                    ],
                    'average_user_rating': catalog_place[
                        'average_user_rating'
                    ],
                    'brand_id': PLACE2BRAND[catalog_place['id']]['brand'],
                    'courier_type': catalog_place.get(
                        'courier_type', 'pedestrian',
                    ),
                    'delivery_type': catalog_place['delivery_type'],
                    'id': catalog_place['id'],
                    'is_fast_food': PLACE2BRAND[catalog_place['id']]['is_ff'],
                    'location': catalog_place['location'],
                    'place_increment': catalog_place['place_increment'],
                    'price_category': catalog_place.get('price_category'),
                    'region_delivery_time_offset': catalog_place[
                        'delivery_time_offset'
                    ],
                    'shown_rating': catalog_place.get('shown_rating'),
                    'time_to_delivery': catalog_place['time_to_delivery'],
                    'zone_id': 1592965,
                },
            },
        ],
        'server_time': catalog_time,
        'user_location': catalog_loc,
    }


@exp3_decorator(
    name='eats_eta_ml',
    value={
        'tag': 'eta_test',
        'enabled': True,
        'custom_brands': [
            {
                'id': 11787,
                'max_delta': 100,
                'min_delta': 100,
                'shift': -5,
                'shift_cooking_time': 10,
            },
        ],
        'region_taxi_shifts': [{'region_id': 1, 'taxi_shift': -10}],
        'catalog_model': 'linear',
        'slug_model': 'linear',
        'shift_total_time': 5,
        'shift_cooking_time': 10,
        'shift_delivery_time': 15,
        'shift_const_cooking_time': 20,
        'shift_taxi_delivery_time': 25,
        'taxi_routing_enabled': True,
    },
)
@exp3_decorator(
    name='eats_retail_eta_ml',
    value={
        'tag': 'eta_test',
        'enabled': True,
        'region_taxi_shifts': [{'region_id': 1, 'taxi_shift': -10}],
        'catalog_model': 'linear',
        'slug_model': 'linear',
        'shift_total_time': 5,
        'shift_cooking_time': 10,
        'shift_delivery_time': 15,
        'shift_const_cooking_time': 20,
        'shift_taxi_delivery_time': 25,
        'taxi_routing_enabled': True,
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
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_eta_consistency(
        taxi_umlaas_eats, catalog_v1, load_json, mockserver,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    @mockserver.json_handler('/eats-eta/v1/eta')
    def mock_eats_eta(request):
        return {
            'etas': [
                {'time': 1800, 'distance': 15}
                for _ in range(len(request.json['sources']))
            ],
        }

    request = load_json('request.json')
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    # all the times without lavka
    times = {
        place['id']: (
            place['predicted_times']['min'],
            place['predicted_times']['max'],
        )
        for place in data['result']
        if place['id'] != 76511
    }

    params = get_query_params(request_type='slug')

    catalog_time = request['ranking_at']
    catalog_loc = request['location']
    slug_preds = {}

    for place in request['places']:
        # remove places ignored by catalog (2) and lavka (1)
        if place['id'] in (10479, 44419, 76511):
            continue
        slug_request = create_slug_request(place, catalog_time, catalog_loc)
        response = await taxi_umlaas_eats.post(
            f'{URL}?{urlparse.urlencode(params)}',
            data=json.dumps(slug_request),
        )

        assert response.status == 200

        data = response.json()

        predicted_times = data['predicted_times'][0]['times']
        slug_preds[place['id']] = (
            predicted_times['boundaries']['min'],
            predicted_times['boundaries']['max'],
        )

    assert times == slug_preds
