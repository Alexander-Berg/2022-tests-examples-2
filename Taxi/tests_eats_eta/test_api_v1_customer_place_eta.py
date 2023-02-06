import json
from urllib import parse as urlparse

import pytest

from . import utils


def _get_query_params(place_type='default', request_type='default'):
    params = dict(
        service_name='test',
        request_id='test_request_id',
        user_id='1184610',
        device_id='BC5B7039-40C3-46F5-9D10-2B539DC0B730',
        place_type=place_type,
        request_type=request_type,
    )
    return params


@pytest.mark.redis_store(
    [
        'set',
        utils.make_redis_key_with_cart(
            {'place_id': 321075, 'user_id': '1184610'},
        ),
        json.dumps(
            {
                'place_id': 321075,
                'user_id': '1184610',
                'brand_id': '93333',
                'total_time': 100,
                'cooking_time': 30,
                'delivery_time': 70,
                'boundaries': {'min': 90, 'max': 120},
            },
        ),
    ],
    [
        'set',
        utils.make_redis_key_no_cart(
            {'place_id': 321075, 'user_id': '1184610'},
        ),
        json.dumps(
            {
                'place_id': 321075,
                'user_id': '1184610',
                'brand_id': '93333',
                'total_time': 80,
                'cooking_time': 10,
                'delivery_time': 70,
                'boundaries': {'min': 70, 'max': 100},
            },
        ),
    ],
)
@pytest.mark.experiments3()
async def test_cart_in_redis(
        taxi_eats_eta, mockserver, load_json, redis_store,
):
    eta_request = load_json('request_with_cart.json')
    eta_response = load_json('response.json')

    @mockserver.json_handler('umlaas-eats/umlaas-eats/v1/eta')
    def umlass_eats_v1_eta(request):
        assert len(request.json['requested_times']) == 1
        no_cart_boundaries = request.json['requested_times'][0].get(
            'prediction_no_cart',
        )
        with_cart_boundaries = request.json['requested_times'][0].get(
            'prediction_with_cart',
        )
        assert no_cart_boundaries
        assert with_cart_boundaries
        assert no_cart_boundaries['min'] == 70
        assert no_cart_boundaries['max'] == 100
        assert with_cart_boundaries['min'] == 90
        assert with_cart_boundaries['max'] == 120
        return eta_response

    params = urlparse.urlencode(_get_query_params())
    response = await taxi_eats_eta.post(
        f'/api/v1/customer/place/eta?{params}', json=eta_request,
    )

    assert umlass_eats_v1_eta.times_called == 1
    assert response.status_code == 200
    assert response.json() == eta_response

    key = utils.make_redis_key_with_cart(
        {'place_id': 321075, 'user_id': '1184610'},
    )
    redis_data = json.loads(redis_store.get(key))
    assert redis_data == eta_response['predicted_times'][0]['times']


@pytest.mark.experiments3()
async def test_cart_empty_redis(
        taxi_eats_eta, mockserver, load_json, redis_store,
):
    eta_request = load_json('request_with_cart.json')
    eta_response = load_json('response.json')

    @mockserver.json_handler('umlaas-eats/umlaas-eats/v1/eta')
    def umlass_eats_v1_eta(request):
        assert len(request.json['requested_times']) == 1
        assert 'prediction_no_cart' not in request.json['requested_times'][0]
        assert 'prediction_with_cart' not in request.json['requested_times'][0]
        return eta_response

    params = urlparse.urlencode(_get_query_params())
    response = await taxi_eats_eta.post(
        f'/api/v1/customer/place/eta?{params}', json=eta_request,
    )

    assert umlass_eats_v1_eta.times_called == 1
    assert response.status_code == 200
    assert response.json() == eta_response

    key = utils.make_redis_key_with_cart(
        {'place_id': 321075, 'user_id': '1184610'},
    )
    redis_data = json.loads(redis_store.get(key))
    assert redis_data == eta_response['predicted_times'][0]['times']


@pytest.mark.redis_store(
    [
        'set',
        utils.make_redis_key_no_cart(
            {'place_id': 321075, 'user_id': '1184610'},
        ),
        json.dumps(
            {
                'place_id': 321075,
                'user_id': '1184610',
                'brand_id': '93333',
                'total_time': 80,
                'cooking_time': 10,
                'delivery_time': 70,
                'boundaries': {'min': 70, 'max': 100},
            },
        ),
    ],
)
@pytest.mark.experiments3()
async def test_no_cart_in_redis(taxi_eats_eta, mockserver, load_json):
    eta_request = load_json('request_no_cart.json')
    eta_response = load_json('response.json')

    @mockserver.json_handler('umlaas-eats/umlaas-eats/v1/eta')
    def umlass_eats_v1_eta(_):
        return eta_response

    params = urlparse.urlencode(_get_query_params())
    response = await taxi_eats_eta.post(
        f'/api/v1/customer/place/eta?{params}', json=eta_request,
    )

    assert umlass_eats_v1_eta.times_called == 0
    assert response.status_code == 200
    predicted_times = response.json()['predicted_times']
    assert len(predicted_times) == 1
    times = predicted_times[0]['times']
    assert times['total_time'] == 80
    assert times['cooking_time'] == 10
    assert times['delivery_time'] == 70


@pytest.mark.redis_store(
    [
        'set',
        utils.make_redis_key_no_cart(
            {'place_id': 321075, 'user_id': '1184610'},
        ),
        {
            '$json': {
                'place_id': 321075,
                'user_id': '1184610',
                'brand_id': '93333',
                'total_time': 80,
                'cooking_time': 10,
                'delivery_time': 70,
                'promise_min': 70,
                'promise_max': 100,
            },
        },
    ],
)
@pytest.mark.experiments3()
async def test_no_user_id(taxi_eats_eta, mockserver, load_json):
    eta_request = load_json('request_no_cart.json')
    eta_response = load_json('response.json')

    @mockserver.json_handler('umlaas-eats/umlaas-eats/v1/eta')
    def umlass_eats_v1_eta(_):
        return eta_response

    params = _get_query_params()
    del params['user_id']
    params = urlparse.urlencode(params)
    response = await taxi_eats_eta.post(
        f'/api/v1/customer/place/eta?{params}', json=eta_request,
    )

    assert umlass_eats_v1_eta.times_called == 1
    assert response.status_code == 200
    assert response.json() == eta_response


@pytest.mark.experiments3()
async def test_no_cart_empty_redis(
        taxi_eats_eta, mockserver, load_json, redis_store,
):
    eta_request = load_json('request_no_cart.json')
    eta_response = load_json('response.json')

    @mockserver.json_handler('umlaas-eats/umlaas-eats/v1/eta')
    def umlass_eats_v1_eta(_):
        return eta_response

    params = urlparse.urlencode(_get_query_params())
    response = await taxi_eats_eta.post(
        f'/api/v1/customer/place/eta?{params}', json=eta_request,
    )

    assert umlass_eats_v1_eta.times_called == 1
    assert response.status_code == 200
    assert response.json() == eta_response

    key = utils.make_redis_key_no_cart(
        {'place_id': 321075, 'user_id': '1184610'},
    )
    redis_data = json.loads(redis_store.get(key))
    assert redis_data == eta_response['predicted_times'][0]['times']


@pytest.mark.redis_store(
    [
        'set',
        utils.make_redis_key_no_cart(
            {'place_id': 55555, 'user_id': '1184610'},
        ),
        json.dumps(
            {
                'place_id': 55555,
                'user_id': '1184610',
                'brand_id': '93333',
                'total_time': 80,
                'cooking_time': 10,
                'delivery_time': 70,
                'boundaries': {'min': 70, 'max': 100},
            },
        ),
    ],
)
@pytest.mark.experiments3()
async def test_multiple_places_in_request(
        taxi_eats_eta, mockserver, load_json, redis_store,
):
    eta_request = load_json('request_multiple_place_ids.json')
    eta_response = load_json('response_multiple_place_ids.json')

    @mockserver.json_handler('umlaas-eats/umlaas-eats/v1/eta')
    def umlass_eats_v1_eta(_):
        return eta_response

    params = urlparse.urlencode(_get_query_params())
    response = await taxi_eats_eta.post(
        f'/api/v1/customer/place/eta?{params}', json=eta_request,
    )

    assert umlass_eats_v1_eta.times_called == 1
    assert response.status_code == 200

    response_json = response.json()
    expected_json = load_json('multiple_place_ids_expected_response.json')

    for json_object in [response_json, expected_json]:
        json_object['predicted_times'].sort(key=lambda x: x['id'])

    assert response_json == expected_json
