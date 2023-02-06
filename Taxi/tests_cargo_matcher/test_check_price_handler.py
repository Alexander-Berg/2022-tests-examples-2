import copy

import pytest

from . import conftest


CORP_CLIENT_ID = 'corp_client_id_12312312312312312'
HEADERS = {
    'Accept-Language': 'ru',
    'X-B2B-Client-Id': CORP_CLIENT_ID,
    'X-Cargo-Api-Prefix': '/b2b/cargo/integration/',
}

VAT20 = pytest.param(
    1.2,
    marks=pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_b2b_check_price_use_vat',
        consumers=['cargo-matcher/estimate'],
        clauses=[],
        default_value={'enabled': True},
    ),
)

CHECK_PRICE_REQUEST = {
    'items': [
        {
            'size': {'length': 0.3, 'width': 0.3, 'height': 0.5},
            'weight': 7,
            'quantity': 1,
        },
    ],
    'route_points': [
        {'coordinates': [37.1, 55.1]},
        {'coordinates': [37.2, 55.3]},
        {'coordinates': [37.3, 55.4]},
    ],
}

EXPECTED_USER_AGENT_PARAMETRIZE = (
    pytest.param(
        None, marks=[pytest.mark.config(CARGO_TARIFF_CLASS_TO_USER_AGENT={})],
    ),
    pytest.param(
        'express_execution',
        marks=[
            pytest.mark.config(
                CARGO_TARIFF_CLASS_TO_USER_AGENT={
                    'express': 'express_execution',
                },
            ),
        ],
    ),
)


@pytest.fixture(name='call_check_price')
def _call_check_price(taxi_cargo_matcher):
    async def _wrapper(request=None, headers=None):
        request = request if request else CHECK_PRICE_REQUEST
        headers = headers if headers else HEADERS
        response = await taxi_cargo_matcher.post(
            '/api/integration/v1/check-price', json=request, headers=headers,
        )
        return response

    return _wrapper


@pytest.fixture(name='mock_cargo_pricing_check_price')
def _mock_cargo_pricing_check_price(mockserver, default_pricing_response):
    class Context:
        request = None
        mock = None
        response = default_pricing_response

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v1/taxi/check-price')
    def _mock(request, *args, **kwargs):
        ctx.request = request.json
        return ctx.response

    ctx.mock = _mock

    return ctx


async def test_one_point_success(
        mockserver, call_check_price, mock_int_api_estimate,
):
    mock_int_api_estimate['response'] = conftest.get_default_estimate_response(
        taxi_class='express',
    )
    request = copy.deepcopy(CHECK_PRICE_REQUEST)
    request['route_points'] = request['route_points'][:1]
    response = await call_check_price(request=request)
    assert response.status_code == 200


@pytest.mark.config(
    CARGO_MATCHER_ENABLE_CHECK_PRICE_PUMPKIN={
        'enabled': True,
        'minimal_price': '139',
    },
)
async def test_pumpkin_enabled(mockserver, call_check_price):
    request = copy.deepcopy(CHECK_PRICE_REQUEST)
    request['route_points'] = request['route_points'][:1]
    response = await call_check_price(request=request)
    assert response.status_code == 200
    assert response.json()['price'] == '139'


async def test_without_b2b_id(
        mockserver, call_check_price, mock_int_api_estimate,
):
    mock_int_api_estimate['response'] = conftest.get_default_estimate_response(
        taxi_class='express',
    )
    request = copy.deepcopy(CHECK_PRICE_REQUEST)
    request['route_points'] = request['route_points'][:1]
    headers = copy.deepcopy(HEADERS)
    headers.pop('X-B2B-Client-Id', None)
    response = await call_check_price(request=request, headers=headers)
    assert response.status_code == 200


async def test_without_items(
        mockserver, call_check_price, mock_int_api_estimate,
):
    mock_int_api_estimate['response'] = conftest.get_default_estimate_response(
        taxi_class='express',
    )
    request = copy.deepcopy(CHECK_PRICE_REQUEST)
    del request['items']

    response = await call_check_price(request=request)
    assert response.status_code == 200


@pytest.mark.config(CARGO_TYPE_LIMITS=conftest.get_default_cargo_type_limits())
async def test_cargo_type_replacement(
        mockserver,
        exp3_pricing_enabled,
        call_check_price,
        mock_int_api_estimate,
        mock_cargo_pricing_check_price,
        exp3_work_mode_new_way,
):
    mock_int_api_estimate['response'] = conftest.get_default_estimate_response(
        taxi_class='cargo',
    )
    request = copy.deepcopy(CHECK_PRICE_REQUEST)
    request['requirements'] = {'taxi_class': 'cargo', 'cargo_type': 'van'}
    response = await call_check_price(request=request)
    assert response.status_code == 200
    assert (
        'cargo_type'
        not in mock_cargo_pricing_check_price.request['taxi_requirements']
    )
    assert (
        mock_cargo_pricing_check_price.request['taxi_requirements'][
            'cargo_type_int'
        ]
        == 1
    )


@pytest.mark.parametrize('price_multiplier', (1, VAT20))
@pytest.mark.parametrize(
    'expected_user_agent', EXPECTED_USER_AGENT_PARAMETRIZE,
)
async def test_success(
        mockserver,
        call_check_price,
        exp3_pricing_disabled,
        get_currency_rules,
        price_multiplier,
        expected_user_agent,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        if expected_user_agent:
            assert request.headers['User-Agent'] == expected_user_agent
        assert request.json == {
            'sourceid': 'cargo',
            'selected_class': 'express',
            'payment': {
                'payment_method_id': 'corp-' + CORP_CLIENT_ID,
                'type': 'corp',
            },
            'requirements': {'door_to_door': True},
            'route': [[37.1, 55.1], [37.2, 55.3], [37.3, 55.4]],
        }
        return {
            'is_fixed_price': True,
            'currency_rules': get_currency_rules,
            'service_levels': [{'class': 'express', 'price_raw': 999.01}],
        }

    response = await call_check_price()
    assert response.status_code == 200, response.json()
    assert response.json() == {
        'price': f'{round(999.01 * price_multiplier, 2)}',  # 1198.81
        'requirements': {'taxi_class': 'express'},
        'zone_id': 'moscow',
        'currency_rules': {
            'code': 'RUB',
            'sign': '₽',
            'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
            'text': 'руб.',
        },
    }


@pytest.mark.parametrize('price_multiplier', (1, VAT20))
async def test_success_with_cargo_pricing(
        call_check_price,
        exp3_pricing_enabled,
        mock_int_api_profile,
        price_multiplier,
        mock_cargo_pricing_check_price,
):
    response = await call_check_price()
    assert response.status_code == 200, response.json()
    assert response.json() == {
        'price': f'{123.45 * price_multiplier}',
        'requirements': {'taxi_class': 'express'},
        'zone_id': 'moscow',
        'distance_meters': 1000.0,
        'eta': 0.2,
        'currency_rules': {
            'code': 'RUB',
            'sign': 'RUB',
            'template': 'RUB',
            'text': 'RUB',
        },
    }

    assert mock_cargo_pricing_check_price.mock.times_called == 1
    assert mock_cargo_pricing_check_price.request == {
        'price_for': 'client',
        'homezone': 'moscow',
        'payment_info': {
            'type': 'corp',
            'method_id': 'corp-' + CORP_CLIENT_ID,
        },
        'clients': [{'corp_client_id': 'corp_client_id_12312312312312312'}],
        'tariff_class': 'express',
        'taxi_requirements': {'door_to_door': True},
        'waypoints': [
            {'type': 'pickup', 'position': [37.1, 55.1]},
            {'type': 'dropoff', 'position': [37.2, 55.3]},
            {'type': 'dropoff', 'position': [37.3, 55.4]},
        ],
    }


def _get_request_with_requirements(requirements):
    request = copy.deepcopy(CHECK_PRICE_REQUEST)
    request['requirements'] = requirements
    return request


async def test_success_with_cargo_pricing_dynamic_requirements(
        call_check_price,
        exp3_pricing_enabled,
        mock_int_api_profile,
        config_dynamic_requirements,
        mock_cargo_pricing_check_price,
):
    request = _get_request_with_requirements(
        requirements={'dynamic_requirement': 12, 'unknown_requirement': True},
    )
    response = await call_check_price(request=request)
    assert response.status_code == 200, response.json()
    # no filling requirements in response
    assert response.json()['requirements'] == {'taxi_class': 'express'}

    assert mock_cargo_pricing_check_price.mock.times_called == 1
    assert mock_cargo_pricing_check_price.request['taxi_requirements'] == {
        'door_to_door': True,
        'dynamic_requirement': 12,
    }


async def test_success_with_cargo_pricing_dynamic_requirements_no_config(
        call_check_price,
        exp3_pricing_enabled,
        mock_int_api_profile,
        mock_cargo_pricing_check_price,
):
    request = _get_request_with_requirements(
        requirements={'dynamic_requirement': 12},
    )
    response = await call_check_price(request=request)
    assert response.status_code == 200, response.json()
    assert response.json()['requirements'] == {'taxi_class': 'express'}

    assert mock_cargo_pricing_check_price.mock.times_called == 1
    assert mock_cargo_pricing_check_price.request['taxi_requirements'] == {
        'door_to_door': True,
    }


async def test_with_cargo_pricing_requirements_from_options(
        call_check_price,
        exp3_pricing_enabled,
        mock_int_api_profile,
        mock_cargo_pricing_check_price,
        config_dynamic_requirements,
        conf_exp3_requirements_from_options,
):
    await conf_exp3_requirements_from_options(
        requirement='dynamic_requirement',
    )
    request = _get_request_with_requirements(
        requirements={'cargo_options': ['auto_courier']},
    )
    response = await call_check_price(request=request)
    assert response.status_code == 200, response.json()
    # no filling requirements in response
    assert response.json()['requirements'] == {'taxi_class': 'express'}

    assert mock_cargo_pricing_check_price.mock.times_called == 1
    assert mock_cargo_pricing_check_price.request['taxi_requirements'] == {
        'door_to_door': True,
        'dynamic_requirement': True,
    }


async def test_success_with_cargo_pricing_switchable_requirements(
        call_check_price,
        exp3_pricing_enabled,
        mock_int_api_profile,
        config_dynamic_requirements,
        mock_cargo_pricing_check_price,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['api', 'corp_cabinet'])
    request = _get_request_with_requirements(
        requirements={'dynamic_requirement': True},
    )
    response = await call_check_price(request=request)
    assert response.status_code == 200, response.json()
    # no filling requirements in response
    assert response.json()['requirements'] == {'taxi_class': 'express'}

    assert mock_cargo_pricing_check_price.mock.times_called == 1
    assert mock_cargo_pricing_check_price.request['taxi_requirements'] == {
        'door_to_door': True,
        'dynamic_requirement': True,
    }


async def test_success_with_cargo_pricing_switchable_requirements_disabled(
        call_check_price,
        exp3_pricing_enabled,
        mock_int_api_profile,
        config_dynamic_requirements,
        mock_cargo_pricing_check_price,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=[])
    request = _get_request_with_requirements(
        requirements={'dynamic_requirement': True},
    )
    response = await call_check_price(request=request)
    assert response.status_code == 200, response.json()
    # no filling requirements in response
    assert response.json()['requirements'] == {'taxi_class': 'express'}

    assert mock_cargo_pricing_check_price.mock.times_called == 1
    assert mock_cargo_pricing_check_price.request['taxi_requirements'] == {
        'door_to_door': True,
    }


async def test_cant_construct_route_cargo_pricing(
        mockserver,
        call_check_price,
        exp3_pricing_enabled,
        mock_int_api_profile,
        mock_cargo_pricing_check_price,
):
    mock_cargo_pricing_check_price.response = mockserver.make_response(
        json={
            'code': 'cant_construct_route',
            'message': 'Requested route is insoluble',
        },
        status=400,
    )

    response = await call_check_price()
    assert response.status_code == 409
    assert response.json() == {
        'code': 'estimating.cant_construct_route',
        'message': 'estimating.cant_construct_route',
    }


async def test_tariff_not_found(
        mockserver,
        call_check_price,
        exp3_pricing_enabled,
        mock_int_api_profile,
        mock_cargo_pricing_check_price,
):
    mock_cargo_pricing_check_price.response = mockserver.make_response(
        json={
            'code': 'tariff_not_found',
            'message': 'Requested tariff not found',
        },
        status=400,
    )

    response = await call_check_price()
    assert response.status_code == 409
    assert response.json() == {
        'code': 'estimating.tariff.no_tariff_plan',
        'message': 'estimating.tariff.no_tariff_plan',
    }


async def test_bad_requirements(
        mockserver,
        call_check_price,
        exp3_pricing_enabled,
        mock_int_api_profile,
        mock_cargo_pricing_check_price,
):
    mock_cargo_pricing_check_price.response = mockserver.make_response(
        json={
            'code': 'bad_requirements',
            'message': 'Select for non-select requirement',
        },
        status=400,
    )

    response = await call_check_price()
    assert response.status_code == 409
    assert response.json() == {
        'code': 'estimating.requirement_unavailable',
        'message': 'estimating.requirement_unavailable',
    }


@pytest.mark.translations(
    cargo={
        'estimating.too_large_item': {'ru': 'Слишком больштие габариты груза'},
    },
)
async def test_item_not_fit(exp3_pricing_disabled, call_check_price):
    request = copy.deepcopy(CHECK_PRICE_REQUEST)
    request['items'][0]['size']['length'] = 100
    response = await call_check_price(request=request)
    assert response.status_code == 409
    assert response.json() == {
        'code': 'estimating.too_large_item',
        'message': 'Слишком больштие габариты груза',
    }


async def test_check_price_estimate_validation_distance(
        call_check_price,
        exp3_pricing_enabled,
        mock_int_api_profile,
        mock_cargo_pricing_check_price,
        config_estimate_result_validation,
):
    mock_cargo_pricing_check_price.response['details'][
        'total_distance'
    ] = '2000'

    response = await call_check_price()
    assert response.status_code == 409
    assert response.json() == {
        'code': 'estimating.route_too_long',
        'message': 'estimating.route_too_long',
    }


@pytest.mark.translations(
    cargo={'estimating.route_too_long': {'ru': 'Слишком длинно'}},
)
async def test_check_price_estimate_validation_time(
        call_check_price,
        exp3_pricing_enabled,
        mock_int_api_profile,
        mock_cargo_pricing_check_price,
        config_estimate_result_validation,
):
    mock_cargo_pricing_check_price.response['details']['total_time'] = '920'

    response = await call_check_price()
    assert response.status_code == 409
    assert response.json() == {
        'code': 'estimating.route_too_long',
        'message': 'Слишком длинно',
    }


async def test_check_price_same_day(
        mockserver, call_check_price, taxi_config, sdd_tariff='night',
):
    taxi_config.set_values(
        {
            'CARGO_SDD_TAXI_TARIFF_SETTINGS': {
                'name': sdd_tariff,
                'remove_in_tariffs': True,
                'remove_in_admin_tariffs': True,
            },
        },
    )

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def mock_estimate(request):
        assert request.json['selected_class'] == sdd_tariff
        assert request.json['requirements']['door_to_door']
        context = {
            'response': conftest.get_default_estimate_response(
                taxi_class=sdd_tariff,
            ),
        }
        return context['response']

    req = copy.deepcopy(CHECK_PRICE_REQUEST)
    same_day_data = {
        'same_day_data': {
            'delivery_interval': {
                'from': '2022-03-02T12:00:00+00:00',
                'to': '2022-03-02T16:00:00+00:00',
            },
        },
    }

    req['requirements'] = same_day_data
    response = await call_check_price(request=req)
    assert response.json()['requirements'] == same_day_data
    assert response.status_code == 200

    assert mock_estimate.times_called == 1


async def test_empty_coordinates_and_address(call_check_price):
    request = copy.deepcopy(CHECK_PRICE_REQUEST)
    del request['route_points'][1]['coordinates']
    response = await call_check_price(request)

    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'Необходимо передать координаты или топоним точки',
    }


@pytest.mark.parametrize(
    'yamaps_precision, config_precision, code',
    [
        ('NUMBER', 'Number', 200),
        ('RANGE', 'Number', 400),
        ('NUMBER', 'Range', 200),
    ],
)
async def test_run_geocoder(
        taxi_config,
        taxi_cargo_matcher,
        mockserver,
        call_check_price,
        yamaps,
        load_json,
        yamaps_precision,
        config_precision,
        code,
):
    taxi_config.set_values(
        {'CARGO_CLAIMS_GEOCODER_PRECISION': {'precision': config_precision}},
    )
    await taxi_cargo_matcher.invalidate_caches()

    yamaps_response = load_json('yamaps_response.json')
    yamaps_response['geocoder']['precision'] = yamaps_precision
    coordinates = yamaps_response['geometry']

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def mock_estimate(req):
        assert req.json['route'][1] == coordinates
        context = {
            'response': conftest.get_default_estimate_response(
                taxi_class='express',
            ),
        }
        return context['response']

    request = copy.deepcopy(CHECK_PRICE_REQUEST)
    del request['route_points'][1]['coordinates']
    request['route_points'][1]['fullname'] = 'fullname'

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects_callback(req):
        return [yamaps_response]

    response = await call_check_price(request)
    assert response.status_code == code

    if code == 200:
        assert mock_estimate.times_called == 1


async def test_undefined_address(call_check_price, yamaps):
    request = copy.deepcopy(CHECK_PRICE_REQUEST)
    del request['route_points'][1]['coordinates']
    request['route_points'][1]['fullname'] = 'abracadabra'

    response = await call_check_price(request)
    assert response.status_code == 400
    assert (
        response.json()['message']
        == 'Не удалось преобразовать адрес abracadabra в координаты: '
        'проверьте корректность адреса или попробуйте'
        ' указать координаты вручную'
    )
