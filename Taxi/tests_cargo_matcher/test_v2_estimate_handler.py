import pytest

from . import conftest


def _get_estimate_request():
    return {
        'client': {'corp_client_id': 'corp_client_id_12312312312312312'},
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


@pytest.fixture(name='call_v2_estimate')
def _call_v2_estimate(taxi_cargo_matcher):
    async def _wrapper(request=None):
        request = request if request else _get_estimate_request()

        response = await taxi_cargo_matcher.post(
            '/v2/estimate', json=request, headers={'Accept-Language': 'ru'},
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


async def test_success_estimate_result(
        exp3_enabled, call_v2_estimate, mock_cargo_pricing, mock_v1_profile,
):
    response = await call_v2_estimate()
    assert response.status_code == 200
    assert response.json() == _get_expected_estimate_result()


def _get_estimate_request_with_requirements(requirements):
    request = _get_estimate_request()
    request['request']['taxi_class'] = 'express'
    request['request']['requirements'] = requirements
    return request


async def test_success_estimate_result_with_requirements(
        exp3_enabled, call_v2_estimate, mock_cargo_pricing, mock_v1_profile,
):
    request = _get_estimate_request_with_requirements(
        requirements={'skip_door_to_door': True, 'pro_courier': True},
    )

    response = await call_v2_estimate(request=request)
    assert response.status_code == 200

    expected_result = _get_expected_estimate_result()
    expected_result['vehicle']['taxi_requirements'] = {'pro_courier': 1}
    assert response.json() == expected_result


async def test_success_estimate_result_with_dynamic_requirements(
        exp3_enabled,
        call_v2_estimate,
        mock_cargo_pricing,
        mock_v1_profile,
        config_dynamic_requirements,
):
    request = _get_estimate_request_with_requirements(
        requirements={
            'skip_door_to_door': True,
            'dynamic_requirement': '100',
            'unknown_dynamic_requirement': '200',
        },
    )

    response = await call_v2_estimate(request=request)
    assert response.status_code == 200

    expected_result = _get_expected_estimate_result()
    expected_result['vehicle']['taxi_requirements'] = {
        'dynamic_requirement': '100',
    }
    assert response.json() == expected_result


async def test_success_estimate_result_with_dynamic_requirements_disabled(
        exp3_enabled,
        call_v2_estimate,
        mock_cargo_pricing,
        mock_v1_profile,
        set_dynamic_requirements_config,
):
    await set_dynamic_requirements_config(dynamic_requirements=[])

    request = _get_estimate_request_with_requirements(
        requirements={'skip_door_to_door': True, 'dynamic_requirement': '100'},
    )

    response = await call_v2_estimate(request=request)
    assert response.status_code == 200

    expected_result = _get_expected_estimate_result()
    expected_result['vehicle'].pop('taxi_requirements')
    assert response.json() == expected_result


async def test_success_estimate_result_requirements_from_options(
        exp3_enabled,
        call_v2_estimate,
        mock_cargo_pricing,
        mock_v1_profile,
        conf_exp3_requirements_from_options,
        config_dynamic_requirements,
):
    await conf_exp3_requirements_from_options(
        requirement='dynamic_requirement',
    )
    request = _get_estimate_request_with_requirements(
        requirements={'skip_door_to_door': True},
    )
    request['request']['cargo_options'] = ['auto_courier']

    response = await call_v2_estimate(request=request)
    assert response.status_code == 200

    expected_result = _get_expected_estimate_result()
    expected_result['vehicle']['taxi_requirements'] = {
        'dynamic_requirement': True,
    }
    assert response.json() == expected_result


async def test_success_estimate_with_switchable_requirements(
        exp3_enabled,
        call_v2_estimate,
        mock_cargo_pricing,
        mock_v1_profile,
        config_dynamic_requirements,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['api'])
    request = _get_estimate_request_with_requirements(
        requirements={
            'skip_door_to_door': True,
            'dynamic_requirement': True,
            'unknown_dynamic_requirement': '200',
        },
    )

    response = await call_v2_estimate(request=request)
    assert response.status_code == 200

    expected_result = _get_expected_estimate_result()
    expected_result['vehicle']['taxi_requirements'] = {
        'dynamic_requirement': True,
    }
    assert response.json() == expected_result


async def test_success_estimate_with_disabled_switchable_requirements(
        exp3_enabled,
        call_v2_estimate,
        mock_cargo_pricing,
        mock_v1_profile,
        config_dynamic_requirements,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=[])
    request = _get_estimate_request_with_requirements(
        requirements={'skip_door_to_door': True, 'dynamic_requirement': True},
    )

    response = await call_v2_estimate(request=request)
    assert response.status_code == 200

    expected_result = _get_expected_estimate_result()
    expected_result['vehicle'].pop('taxi_requirements')
    assert response.json() == expected_result


@pytest.mark.config(
    CARGO_MATCHER_CARS=[
        {
            'taxi_class': 'cargo',
            'cargo_type': 'lcv_m',
            'length_cm': 30,
            'width_cm': 30,
            'height_cm': 30,
            'carrying_capacity_kg': 10,
            'max_loaders': 2,
            'enabled': True,
        },
    ],
)
async def test_success_estimate_result_with_unconfigured_class(
        exp3_enabled, call_v2_estimate, mock_cargo_pricing, mock_v1_profile,
):
    request = _get_estimate_request()
    request['request']['taxi_class'] = 'express'
    response = await call_v2_estimate(request=request)
    assert response.status_code == 200
    assert response.json() == _get_expected_estimate_result()


async def test_profile_request(
        exp3_enabled, call_v2_estimate, mock_cargo_pricing, mock_v1_profile,
):
    response = await call_v2_estimate()
    assert response.status_code == 200

    assert mock_v1_profile.request == {
        'sourceid': 'cargo',
        'name': 'Petya',
        'user': {'personal_phone_id': '1ebc244580cd48759e5d1764b759f9d1'},
    }


async def test_cargo_pricing_request(
        exp3_enabled, call_v2_estimate, mock_cargo_pricing, mock_v1_profile,
):
    response = await call_v2_estimate()
    assert response.status_code == 200

    prising_request = mock_cargo_pricing.request
    idempotency_token = prising_request.pop('idempotency_token')
    assert len(idempotency_token) > 32
    external_ref = prising_request.pop('external_ref')
    assert len(external_ref) > 32

    assert prising_request == {
        'cargo_items': [
            {
                'dropoff_point_id': '18',
                'pickup_point_id': '17',
                'quantity': 1,
                'size': {'height': 0.5, 'length': 0.3, 'width': 0.3},
                'weight': 7.0,
            },
            {
                'dropoff_point_id': '19',
                'pickup_point_id': '17',
                'quantity': 2,
                'size': {'height': 0.0, 'length': 0.0, 'width': 0.0},
                'weight': 3.0,
            },
        ],
        'clients': [
            {
                'corp_client_id': 'corp_client_id_12312312312312312',
                'user_id': 'taxi_user_id_1',
            },
        ],
        'homezone': 'moscow',
        'is_usage_confirmed': False,
        'payment_info': {
            'method_id': 'corp-corp_client_id_12312312312312312',
            'type': 'corp',
        },
        'price_for': 'client',
        'tariff_class': 'express',
        'taxi_requirements': {'door_to_door': True},
        'waypoints': [
            {'id': '17', 'position': [37.1, 55.1], 'type': 'pickup'},
            {'id': '18', 'position': [37.2, 55.3], 'type': 'dropoff'},
            {'id': '19', 'position': [37.3, 55.4], 'type': 'dropoff'},
        ],
    }


@pytest.mark.config(CARGO_TYPE_LIMITS=conftest.get_default_cargo_type_limits())
async def test_cargo_pricing_request_with_requirements(
        exp3_enabled, call_v2_estimate, mock_cargo_pricing, mock_v1_profile,
):
    request = _get_estimate_request()
    request['request']['taxi_class'] = 'cargo'
    request['request']['requirements'] = {
        'cargo_type': 'lcv_m',
        'skip_door_to_door': True,
    }

    response = await call_v2_estimate(request=request)
    assert response.status_code == 200

    prising_request = mock_cargo_pricing.request
    assert prising_request['tariff_class'] == 'cargo'
    assert prising_request['taxi_requirements'] == {'cargo_type': 'lcv_m'}


async def test_cargo_pricing_request_with_requirements_pro_courier(
        exp3_enabled, call_v2_estimate, mock_cargo_pricing, mock_v1_profile,
):
    request = _get_estimate_request()
    request['request']['requirements'] = {
        'skip_door_to_door': True,
        'pro_courier': True,
    }

    response = await call_v2_estimate(request=request)
    assert response.status_code == 200

    prising_request = mock_cargo_pricing.request
    assert prising_request['tariff_class'] == 'express'
    assert prising_request['taxi_requirements'] == {'pro_courier': 1}


async def test_v2_estimate_estimated_distance_validation(
        exp3_enabled,
        call_v2_estimate,
        mock_cargo_pricing,
        mock_v1_profile,
        config_estimate_result_validation,
):
    mock_cargo_pricing.response['details']['total_distance'] = '2000'
    response = await call_v2_estimate()
    assert response.status_code == 409
    assert response.json() == {
        'code': 'estimating_failed',
        'message': 'estimating.route_too_long',
    }


@pytest.mark.translations(
    cargo={'estimating.route_too_long': {'ru': 'Слишком длинно'}},
)
async def test_v2_estimate_estimated_time_validation(
        exp3_enabled,
        call_v2_estimate,
        mock_cargo_pricing,
        mock_v1_profile,
        config_estimate_result_validation,
):
    mock_cargo_pricing.response['details']['total_time'] = '920'
    response = await call_v2_estimate()
    assert response.status_code == 409
    assert response.json() == {
        'code': 'estimating_failed',
        'message': 'estimating.route_too_long',
    }
