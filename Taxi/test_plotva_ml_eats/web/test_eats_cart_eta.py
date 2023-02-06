import json

import pytest

from plotva_ml_eats.api import eats_cart_eta_v1
from plotva_ml_eats.common import eats_cart_eta as eta_utils

BASE_PATH = '/eats/cart_eta'
PING_PATH = BASE_PATH + '/ping'
V1_PATH = BASE_PATH + '/v1'

EXP_USER_ID = '1184610'
EXP_DEVICE_ID = 'BC5B7039-40C3-46F5-9D10-2B539DC0B730'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=V1_PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'eats_cart_eta_models'}),
    pytest.mark.download_ml_resource(
        attrs={'type': 'eats_cart_eta_statistics'},
    ),
]


def exp3_decorator(name, value):
    return pytest.mark.client_experiments3(
        consumer=eats_cart_eta_v1.EXPERIMENT_CONSUMER,
        args=[
            {'name': 'user_id', 'type': 'string', 'value': EXP_USER_ID},
            {'name': 'device_id', 'type': 'string', 'value': EXP_DEVICE_ID},
        ],
        experiment_name=name,
        value=value,
    )


async def test_ping(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200


@exp3_decorator(
    name=eta_utils.EXP3_NAME_LAVKA,
    value={
        'cooking_time': 1,
        'delivery_time': 1,
        'eta_max': 25,
        'eta_min': 10,
        'total_time': 1,
        'ml_enabled': True,
        'taxi_routing_enabled': True,
        'shift_taxi_delivery_time': 10,
    },
)
async def test_v1_lavka_ml(web_app_client, load, mockserver):
    @mockserver.json_handler('/eats-eta/v1/eta')
    def _mock_eats_eta(request):
        assert request.json == {
            'destination': [37.587571, 55.734042],
            'sources': [[37.655975, 55.73843]],
            'type': 'taxi',
        }
        return {'etas': [{'time': 42 * 60, 'distance': 11200}]}

    request_body = load('dummy_lavka_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'food_eta',
            'request_id': '-',
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'place_type': 'lavka',
        },
    )
    assert response.status == 200
    data = json.loads(await response.text())

    assert data['predicted_times'][0]['times']['total_time'] < 10
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 5
    assert data['predicted_times'][0]['times']['boundaries']['max'] == 15

    assert data['predicted_times'][1]['times']['delivery_time'] == 52
    assert data['predicted_times'][1]['times']['boundaries']['min'] == 50
    assert data['predicted_times'][1]['times']['boundaries']['max'] == 60

    assert len(data['predicted_times']) == len(
        json.loads(request_body)['requested_times'],
    )


@exp3_decorator(
    name=eta_utils.EXP3_NAME_LAVKA,
    value={
        'cooking_time': 1,
        'delivery_time': 1,
        'eta_max': 25,
        'eta_min': 10,
        'total_time': 1,
        'ml_enabled': True,
        'taxi_routing_enabled': True,
        'shift_taxi_delivery_time': 10,
    },
)
async def test_v1_lavka_ml_with_headers(web_app_client, load, mockserver):
    @mockserver.json_handler('/eats-eta/v1/eta')
    def _mock_eats_eta(request):
        assert request.json == {
            'destination': [37.587571, 55.734042],
            'sources': [[37.655975, 55.73843]],
            'type': 'taxi',
        }
        return {'etas': [{'time': 42 * 60, 'distance': 11200}]}

    request_body = load('dummy_lavka_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        headers={
            'X-YaTaxi-User': (
                'some_other=other_value,eats_user_id='
                + f'{EXP_USER_ID},some_other=other_value'
            ),
        },
        params={
            'service_name': 'food_eta',
            'request_id': '-',
            'device_id': EXP_DEVICE_ID,
            'place_type': 'lavka',
        },
    )
    assert response.status == 200
    data = json.loads(await response.text())

    assert data['predicted_times'][0]['times']['total_time'] < 10
    assert data['predicted_times'][0]['times']['boundaries']['min'] == 5
    assert data['predicted_times'][0]['times']['boundaries']['max'] == 15

    assert data['predicted_times'][1]['times']['delivery_time'] == 52
    assert data['predicted_times'][1]['times']['boundaries']['min'] == 50
    assert data['predicted_times'][1]['times']['boundaries']['max'] == 60

    assert len(data['predicted_times']) == len(
        json.loads(request_body)['requested_times'],
    )


@exp3_decorator(
    name=eta_utils.EXP3_NAME_ETA_ML,
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [
            {'id': 3529, 'max_delta': 5, 'min_delta': 100},
            {'id': 21053, 'max_delta': 5, 'min_delta': 100},
            {'id': 27983, 'max_delta': 5, 'min_delta': 100},
        ],
        'shift_const_cooking_time': 0,
        'taxi_routing_enabled': True,
        'shift_taxi_delivery_time': 10,
    },
)
async def test_ml_usage(web_app_client, load, mockserver):
    @mockserver.json_handler('/eats-eta/v1/eta')
    def _mock_eats_eta(request):
        assert request.json == {
            'destination': [0.0, 0.0],
            'sources': [[37.881749, 55.753676]],
            'type': 'taxi',
        }
        return {'etas': [{'time': 42 * 60, 'distance': 12200}]}

    request_body = load('dummy_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'food_eta',
            'request_id': '-',
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'place_type': 'default',
        },
    )
    assert response.status == 200
    data = json.loads(await response.text())

    assert data['provider'] == eats_cart_eta_v1.PROVIDER_ML
    assert data['predicted_times'][0]['times']['total_time'] > 10
    assert data['predicted_times'][0]['times']['delivery_time'] == 20
    assert data['predicted_times'][1]['times']['delivery_time'] == 52
    assert (
        data['predicted_times'][0]['times']['boundaries']['min']
        < data['predicted_times'][1]['times']['boundaries']['min']
    )
    for predicted_times in data['predicted_times']:
        assert (
            predicted_times['times']['boundaries']['min']
            <= predicted_times['times']['boundaries']['max']
        )


@exp3_decorator(
    name=eta_utils.EXP3_NAME_LAVKA,
    value={
        'cooking_time': 1,
        'delivery_time': 1,
        'eta_max': 25,
        'eta_min': 10,
        'total_time': 1,
    },
)
@exp3_decorator(
    name=eta_utils.EXP3_NAME_ETA_ML,
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': False,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [
            {'id': 3529, 'max_delta': 5, 'min_delta': 100},
            {'id': 21053, 'max_delta': 5, 'min_delta': 100},
            {'id': 27983, 'max_delta': 5, 'min_delta': 100},
        ],
        'shift_const_cooking_time': 0,
    },
)
async def test_proxy_times_usage(web_app_client, load):
    request_body = load('dummy_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'food_eta',
            'request_id': '-',
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'place_type': 'default',
        },
    )
    assert response.status == 200
    data = json.loads(await response.text())

    assert data['provider'] == eats_cart_eta_v1.PROVIDER_PROXY
    for predicted_times in data['predicted_times']:
        assert (
            predicted_times['times']['boundaries']['min']
            <= predicted_times['times']['boundaries']['max']
        )


@exp3_decorator(
    name=eta_utils.EXP3_NAME_LAVKA,
    value={
        'cooking_time': 1,
        'delivery_time': 1,
        'eta_max': 25,
        'eta_min': 10,
        'total_time': 1,
    },
)
@exp3_decorator(
    name=eta_utils.EXP3_NAME_ETA_ML,
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [
            {'id': 3529, 'max_delta': 0, 'min_delta': 0},
            {'id': 21053, 'max_delta': 0, 'min_delta': 0},
            {'id': 27983, 'max_delta': 0, 'min_delta': 0},
        ],
        'shift_const_cooking_time': 0,
    },
)
async def test_privileged_brand_ids(web_app_client, load):
    request_body = load('privileged_brand_id_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'food_eta',
            'request_id': '-',
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'place_type': 'default',
        },
    )
    data = json.loads(await response.text())

    assert response.status == 200

    average_preparation_time = json.loads(request_body)['requested_times'][0][
        'place'
    ]['average_preparation_time']

    for predicted_times in data['predicted_times']:
        assert (
            predicted_times['times']['cooking_time']
            == average_preparation_time
        )
    for predicted_times in data['predicted_times']:
        assert (
            predicted_times['times']['boundaries']['min']
            <= predicted_times['times']['boundaries']['max']
        )


@exp3_decorator(
    name=eta_utils.EXP3_NAME_ETA_ML,
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'shift_delivery_time': 10,
        'custom_brands': [
            {'id': 3529, 'max_delta': 5, 'min_delta': 100},
            {'id': 21053, 'max_delta': 5, 'min_delta': 100},
            {'id': 27983, 'max_delta': 5, 'min_delta': 100},
        ],
        'shift_const_cooking_time': 0,
        'taxi_routing_enabled': True,
        'shift_taxi_delivery_time': 10,
    },
)
async def test_ml_usage_with_increase(web_app_client, load, mockserver):
    @mockserver.json_handler('/eats-eta/v1/eta')
    def _mock_eats_eta(request):
        assert request.json == {
            'destination': [0.0, 0.0],
            'sources': [[37.881749, 55.753676]],
            'type': 'taxi',
        }
        return {'etas': [{'time': 42 * 60, 'distance': 12200}]}

    request_body = load('dummy_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'food_eta',
            'request_id': '-',
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'place_type': 'default',
        },
    )
    assert response.status == 200
    data = json.loads(await response.text())

    assert data['provider'] == eats_cart_eta_v1.PROVIDER_ML
    assert data['predicted_times'][0]['times']['total_time'] > 10
    assert data['predicted_times'][0]['times']['delivery_time'] == 30
    assert data['predicted_times'][1]['times']['delivery_time'] == 62
    assert (
        data['predicted_times'][0]['times']['boundaries']['min']
        < data['predicted_times'][1]['times']['boundaries']['min']
    )


@exp3_decorator(
    name=eta_utils.EXP3_NAME_LAVKA,
    value={
        'cooking_time': 1,
        'delivery_time': 1,
        'eta_max': 25,
        'eta_min': 10,
        'total_time': 1,
        'ml_enabled': True,
        'proxy_umlaas_eats': True,
    },
)
async def test_proxy_umlaas_eats(web_app_client, load, mockserver):
    request_body = load('dummy_lavka_request.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eta')
    def _mock_eta(request):
        assert json.dumps(request.json, sort_keys=True) == json.dumps(
            json.loads(request_body), sort_keys=True,
        )
        return {
            'provider': 'umlaas-eats',
            'exp_list': [],
            'request_id': 'kdjfalkdjf',
            'predicted_times': [
                {
                    'id': 0,
                    'times': {
                        'total_time': 33,
                        'delivery_time': 10,
                        'cooking_time': 23,
                        'boundaries': {'min': 30, 'max': 40},
                    },
                },
                {
                    'id': 1,
                    'times': {
                        'total_time': 22,
                        'delivery_time': 10,
                        'cooking_time': 12,
                        'boundaries': {'min': 15, 'max': 25},
                    },
                },
            ],
        }

    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'food_eta',
            'request_id': '-',
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'place_type': 'lavka',
        },
    )
    assert response.status == 200
    data = json.loads(await response.text())

    assert data['provider'] == 'umlaas-eats'
    assert data['predicted_times'][0]['times']['total_time'] == 33
    assert data['predicted_times'][1]['times']['total_time'] == 22


@exp3_decorator(
    name=eta_utils.EXP3_NAME_ETA_ML,
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
        'couriers_candidates_parameters': {
            'enabled': True,
            'using_type': 'max',
            'dropoff_add': 300,
            'take_add': 100,
            'tempo': 550,
            'eda_couriers_penalty': 1000,
            'other_lavka_couriers_penalty': 500,
            'shop_couriers_penalty': 2000,
            'to_place_statuses': ['created', 'accepted', 'arrived_to_source'],
            'probability_of_batch': 0.5,
            'top_to_account': 3,
            'global_limit': 1800,
        },
    },
)
async def test_heuristic_by_umlaas_eats(web_app_client, load, mockserver):
    request_body = load('dummy_request.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eta')
    def _mock_eta(request):
        assert json.dumps(request.json, sort_keys=True) != json.dumps(
            json.loads(request_body), sort_keys=True,
        )
        return {
            'provider': 'umlaas-eats',
            'exp_list': [],
            'request_id': 'kdjfalkdjf',
            'predicted_times': [
                {
                    'id': 0,
                    'times': {
                        'total_time': 33,
                        'delivery_time': 10,
                        'cooking_time': 23,
                        'boundaries': {'min': 30, 'max': 40},
                    },
                },
                {
                    'id': 1,
                    'times': {
                        'total_time': 22,
                        'delivery_time': 10,
                        'cooking_time': 12,
                        'boundaries': {'min': 15, 'max': 25},
                    },
                },
            ],
        }

    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'food_eta',
            'request_id': '-',
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'place_type': 'default',
        },
    )
    assert response.status == 200
    data = json.loads(await response.text())

    assert data['provider'] == 'umlaas-eats'
    assert data['predicted_times'][0]['times']['total_time'] == 33
    assert data['predicted_times'][1]['times']['total_time'] == 22
