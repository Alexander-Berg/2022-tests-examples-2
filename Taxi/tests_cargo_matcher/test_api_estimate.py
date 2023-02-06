import pytest


CORP_CLIENT_ID = 'corp_client_id_12312312312312312'
HEADERS = {'Accept-Language': 'ru', 'X-B2B-Client-Id': CORP_CLIENT_ID}


def _get_b2b_estimate_request():
    return {
        'request': {
            'items': [
                {
                    'size': {'length': 0.3, 'width': 0.3, 'height': 0.5},
                    'weight': 7,
                    'quantity': 1,
                    'dropoff_point': 18,
                    'pickup_point': 17,
                },
                {
                    'weight': 3,
                    'quantity': 2,
                    'dropoff_point': 19,
                    'pickup_point': 17,
                },
            ],
            'route_points': [
                {
                    'coordinates': [37.1, 55.1],
                    'type': 'pickup',
                    'id': 17,
                    'contact': {'phone': '+70009999991', 'name': 'Petya'},
                },
                {
                    'coordinates': [37.2, 55.3],
                    'type': 'dropoff',
                    'id': 18,
                    'contact': {'phone': '+70009999992', 'name': 'Vasya'},
                },
                {
                    'coordinates': [37.3, 55.4],
                    'type': 'dropoff',
                    'id': 19,
                    'contact': {'phone': '+70009999993', 'name': 'Vasya'},
                },
            ],
        },
    }


@pytest.fixture(name='call_api_v1_estimate')
def _call_api_v1_estimate(taxi_cargo_matcher, exp3_enabled):
    async def _wrapper(request=None):
        request = request if request else _get_b2b_estimate_request()

        response = await taxi_cargo_matcher.post(
            '/api/integration/v1/estimate', json=request, headers=HEADERS,
        )

        return response

    return _wrapper


def _get_expected_estimate_result():
    return {
        'price': {
            'currency_code': 'RUB',
            'offer': {
                'offer_id': 'cargo-pricing/v1/123456',
                'price': {'total': '123.45'},
            },
        },
        'trip': {'distance_meters': 1000.0, 'eta': 0.2, 'zone_id': 'moscow'},
        'vehicle': {
            'taxi_class': 'express',
            'taxi_requirements': {'door_to_door': True},
        },
    }


async def test_happy_path(
        call_api_v1_estimate, mock_cargo_pricing, mock_v1_profile,
):
    response = await call_api_v1_estimate()
    assert response.status_code == 200
    assert response.json() == _get_expected_estimate_result()


async def test_api_v1_estimate_estimated_distance_validation(
        call_api_v1_estimate,
        mock_cargo_pricing,
        mock_v1_profile,
        config_estimate_result_validation,
):
    mock_cargo_pricing.response['details']['total_distance'] = '2000'
    response = await call_api_v1_estimate()
    assert response.status_code == 409
    assert response.json() == {
        'code': 'estimating_failed',
        'message': 'estimating.route_too_long',
    }


@pytest.mark.translations(
    cargo={'estimating.route_too_long': {'ru': 'Слишком длинно'}},
)
async def test_api_v1_estimate_estimated_time_validation(
        call_api_v1_estimate,
        mock_cargo_pricing,
        mock_v1_profile,
        config_estimate_result_validation,
):
    mock_cargo_pricing.response['details']['total_time'] = '920'
    response = await call_api_v1_estimate()
    assert response.status_code == 409
    assert response.json() == {
        'code': 'estimating_failed',
        'message': 'estimating.route_too_long',
    }


async def test_empty_coordinates_and_address(
        call_api_v1_estimate, mock_cargo_pricing, mock_v1_profile,
):
    request = _get_b2b_estimate_request()
    del request['request']['route_points'][2]['coordinates']
    response = await call_api_v1_estimate(request=request)
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'Необходимо передать координаты или топоним точки',
    }


async def test_undefined_address(
        call_api_v1_estimate, mock_cargo_pricing, mock_v1_profile, yamaps,
):
    request = _get_b2b_estimate_request()
    del request['request']['route_points'][2]['coordinates']
    request['request']['route_points'][2]['fullname'] = 'abracadabra'

    response = await call_api_v1_estimate(request=request)
    assert response.status_code == 400
    assert (
        response.json()['message']
        == 'Не удалось преобразовать адрес abracadabra в координаты: '
        'проверьте корректность адреса или попробуйте'
        ' указать координаты вручную'
    )


async def test_run_geocoder(
        call_api_v1_estimate,
        yamaps,
        load_json,
        mock_cargo_pricing,
        mock_v1_profile,
):
    yamaps_response = load_json('yamaps_response.json')
    coordinates = yamaps_response['geometry']

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects_callback(req):
        return [yamaps_response]

    request = _get_b2b_estimate_request()
    del request['request']['route_points'][2]['coordinates']
    request['request']['route_points'][2]['fullname'] = 'abracadabra'

    response = await call_api_v1_estimate(request=request)
    assert response.json() == _get_expected_estimate_result()
    assert (
        mock_cargo_pricing.request['waypoints'][2]['position'] == coordinates
    )
