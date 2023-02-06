import pytest
# pylint: disable=import-error
from yamaps_tools import driving as yamaps_driving  # noqa: F401 C5521

from tests_umlaas_grocery_eta import consts


URL = '/internal/umlaas-grocery-eta/v1/delivery-eta'
CONSUMER = 'umlaas-grocery-eta/delivery-eta'


def exp3_decorator(value):
    return pytest.mark.experiments3(
        name='grocery_eta',
        consumers=[CONSUMER],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        is_config=True,
        default_value=value,
    )


def exp3_without_external(ml_resource):
    return exp3_decorator(
        {
            'ml_model': {
                'ml_model_resource_name': ml_resource,
                'sources': {},
                'cooking_time': {'lower_bound': 6, 'upper_bound': 60},
                'delivery_time': {'upper_bound': 60},
                'total_time': {'upper_bound': 100500, 'window_width': 10},
            },
        },
    )


@pytest.mark.parametrize(
    'transport_type,expected_eta',
    [
        pytest.param(
            'pedestrian',
            6 * consts.MINUTE,
            marks=exp3_without_external(
                'grocery_eta_pedestrian_zone_resources_v2',
            ),
        ),
        pytest.param(
            'yandex_taxi',
            6 * consts.MINUTE,
            marks=exp3_without_external(
                'grocery_eta_yandex_taxi_zone_resources_v2',
            ),
        ),
    ],
)
async def test_delivery_eta_ml_model_without_sources(
        taxi_umlaas_grocery_eta, grocery_depots, transport_type, expected_eta,
):
    grocery_depots.add_depot(consts.DEPOT_ID, auto_add_zone=False)
    response = await taxi_umlaas_grocery_eta.post(
        URL,
        json={
            'depot_id': str(consts.DEPOT_ID),
            'transport_type': transport_type,
            'user_location': consts.USER_LOCATION,
        },
        params={'offer_id': '1abc1', 'request_type': 'checkout'},
    )
    assert response.status == 200
    data = response.json()
    assert data == {
        'cooking_time': expected_eta,
        'promise': {'min': 0, 'max': 10 * consts.MINUTE},
        'delivery_time': 0,
        'total_time': expected_eta + 0,  # + delivery_time
    }
    assert (
        data['promise']['min'] <= data['total_time'] <= data['promise']['max']
    )


def exp3_all_sources(ml_resource, extra_statistics=True):
    return exp3_decorator(
        {
            'ml_model': {
                'ml_model_resource_name': ml_resource,
                'sources': {
                    'routing_enabled': True,
                    'depot_statistics_enabled': True,
                    'extra_depot_statistics_enabled': extra_statistics,
                    'depot_state_enabled': True,
                    'shift_info_enabled': True,
                },
                'cooking_time': {'lower_bound': 6, 'upper_bound': 60},
                'delivery_time': {'upper_bound': 60},
                'total_time': {'upper_bound': 100500, 'window_width': 10},
            },
        },
    )


@pytest.mark.now(consts.TIMESTAMP)
@pytest.mark.parametrize(
    'transport_type,delivery_time',
    [
        pytest.param(
            'pedestrian',
            0,  # mocked weights always return 0
            marks=exp3_all_sources('grocery_eta_pedestrian_zone_resources_v2'),
        ),
        pytest.param(
            'yandex_taxi',
            27 * consts.MINUTE,  # uses taxi router response only not model
            marks=exp3_all_sources(
                'grocery_eta_yandex_taxi_zone_resources_v2',
            ),
        ),
    ],
)
async def test_delivery_eta_ml_model_external_data(
        taxi_umlaas_grocery_eta,
        grocery_depots,
        testpoint,
        transport_type,
        delivery_time,
        maps_router,
        grocery_routing,
):
    @testpoint('delivery-eta-ml-request')
    def delivery_eta_ml_request(ml_request):
        pass

    grocery_depots.add_depot(consts.DEPOT_ID, auto_add_zone=False)
    await taxi_umlaas_grocery_eta.enable_testpoints()
    response = await taxi_umlaas_grocery_eta.post(
        URL,
        json={
            'depot_id': str(consts.DEPOT_ID),
            'transport_type': transport_type,
            'user_location': consts.USER_LOCATION,
        },
        params={'offer_id': '1abc1', 'request_type': 'checkout'},
    )
    assert response.status == 200
    data = response.json()
    expected_cooking_time = 6 * consts.MINUTE
    assert data['cooking_time'] == expected_cooking_time
    assert data['delivery_time'] == delivery_time
    assert data['total_time'] == expected_cooking_time + delivery_time
    assert (
        data['promise']['min'] <= data['total_time'] <= data['promise']['max']
    )

    assert delivery_eta_ml_request.times_called == 1

    if transport_type == 'pedestrian':
        assert grocery_routing.times_called == 1
    elif transport_type == 'yandex_taxi':
        assert maps_router.times_called == 1

    ml_request = (await delivery_eta_ml_request.wait_call())['ml_request']
    assert ml_request, 'error retrieving ML request'

    expected_request_keys = list(
        sorted(
            [
                'request_id',
                'predicting_at',
                'request_type',
                'user_info',
                'place_info',
                'courier_type',
            ]
            + [
                'delivery_time',
                'depot_statistics',
                'depot_state',
                'shifts',
            ],  # external data
        ),
    )
    assert sorted(ml_request.keys()) == expected_request_keys
    for key in expected_request_keys:
        assert ml_request[key], key  # external source data is not empty

    assert len(ml_request['depot_statistics']) == 8
    depot_stats = ml_request['depot_statistics']['previous_halfhour']
    assert depot_stats['average_between_pickup_ms'] == 1290
    assert depot_stats['average_between_matched_ms'] == 1383
    assert depot_stats['average_assembling_ms'] == 4956
    assert depot_stats['average_between_assembling_ms'] == 3594
    assert depot_stats['average_time_ms'] == 8765
    assert depot_stats['average_cooking_time_ms'] == 100500


@pytest.mark.now(consts.TIMESTAMP)
@exp3_all_sources('grocery_eta_pedestrian_zone_resources_v2')
async def test_delivery_eta_ml_client_routing_429(
        taxi_umlaas_grocery_eta, grocery_depots, testpoint, mockserver,
):
    @mockserver.handler('/maps-router/v2/summary')
    def get_route(request):
        return mockserver.make_response(
            status=429, content_type='application/x-protobuf',
        )

    @testpoint('delivery-eta-ml-request')
    def delivery_eta_ml_request(ml_request):
        pass

    grocery_depots.add_depot(consts.DEPOT_ID, auto_add_zone=False)
    await taxi_umlaas_grocery_eta.enable_testpoints()
    response = await taxi_umlaas_grocery_eta.post(
        URL,
        json={
            'depot_id': str(consts.DEPOT_ID),
            'transport_type': 'yandex_taxi',
            'user_location': consts.USER_LOCATION,
        },
        params={'offer_id': '1abc1', 'request_type': 'checkout'},
    )
    assert response.status == 200
    assert delivery_eta_ml_request.times_called == 1
    assert get_route.times_called == 1
    ml_request = (await delivery_eta_ml_request.wait_call())['ml_request']
    assert ml_request, 'error retrieving ML request'

    expected_request_keys = list(
        sorted(
            [
                'request_id',
                'predicting_at',
                'request_type',
                'user_info',
                'place_info',
                'courier_type',
            ]
            + [
                # 'delivery_time' нет, потомучто карты ответили 429
                'depot_statistics',
                'depot_state',
                'shifts',
            ],  # external data
        ),
    )
    assert sorted(ml_request.keys()) == expected_request_keys


@pytest.mark.now(consts.TIMESTAMP)
@exp3_all_sources(
    'grocery_eta_pedestrian_zone_resources_v2', extra_statistics=False,
)
async def test_delivery_eta_ml_model_less_statistics(
        taxi_umlaas_grocery_eta, grocery_depots, testpoint, grocery_routing,
):
    @testpoint('delivery-eta-ml-request')
    def delivery_eta_ml_request(ml_request):
        pass

    grocery_depots.add_depot(consts.DEPOT_ID, auto_add_zone=False)
    await taxi_umlaas_grocery_eta.enable_testpoints()
    response = await taxi_umlaas_grocery_eta.post(
        URL,
        json={
            'depot_id': str(consts.DEPOT_ID),
            'transport_type': 'pedestrian',
            'user_location': consts.USER_LOCATION,
        },
        params={'offer_id': '1abc1', 'request_type': 'checkout'},
    )
    assert response.status == 200
    assert delivery_eta_ml_request.times_called == 1
    ml_request = (await delivery_eta_ml_request.wait_call())['ml_request']
    assert ml_request, 'error retrieving ML request'
    assert len(ml_request['depot_statistics']) == 4


@pytest.mark.now(consts.TIMESTAMP)
@exp3_all_sources('grocery_eta_pedestrian_zone_resources_v2')
async def test_delivery_eta_ml_model_shifts_depot_state(
        taxi_umlaas_grocery_eta, grocery_depots, testpoint, grocery_routing,
):
    @testpoint('delivery-eta-ml-request')
    def delivery_eta_ml_request(ml_request):
        pass

    grocery_depots.add_depot(consts.DEPOT_ID, auto_add_zone=False)
    await taxi_umlaas_grocery_eta.enable_testpoints()
    response = await taxi_umlaas_grocery_eta.post(
        URL,
        json={
            'depot_id': str(consts.DEPOT_ID),
            'transport_type': 'pedestrian',
            'user_location': consts.USER_LOCATION,
        },
        params={'offer_id': '1abc1', 'request_type': 'checkout'},
    )
    assert response.status == 200
    assert delivery_eta_ml_request.times_called == 1
    ml_request = (await delivery_eta_ml_request.wait_call())['ml_request']
    assert ml_request, 'error retrieving ML request'

    shifts = ml_request['shifts']
    depot_state = ml_request['depot_state']

    assert len(shifts) == 2
    assert (
        shifts[0]['performer_id'] == '420'
        or shifts[1]['performer_id'] == '420'
    )
    shift_420 = shifts[0] if shifts[0]['performer_id'] == '420' else shifts[1]
    assert shift_420['shift_status'] == 'in_progress'
    assert shift_420['shift_type'] == 'wms'

    assert len(depot_state['orders']) == 1
    assert depot_state['orders'][0]['order_id'] == '10'
    assert depot_state['orders'][0]['order_status'] == 'delivering'
    assert depot_state['orders'][0]['dispatch_status'] == 'delivering'
    assert len(depot_state['performers']) == 2
    assert (
        depot_state['performers'][0]['performer_id'] == '420'
        or depot_state['performers'][1]['performer_id'] == '420'
    )
    performer_420 = (
        depot_state['performers'][0]
        if depot_state['performers'][0]['performer_id'] == '420'
        else depot_state['performers'][1]
    )
    assert performer_420['transport_type'] == 'bicycle'
    assert performer_420['grocery_shift_id'] == '228'
    assert performer_420['performer_status'] == 'deliver'


@exp3_without_external('grocery_eta_yandex_taxi_zone_resources_v2')
async def test_delivery_eta_passes_user_orders_completed_kwarg(
        taxi_umlaas_grocery_eta, grocery_depots, experiments3,
):
    exp3_recorder = experiments3.record_match_tries('grocery_eta')
    grocery_depots.add_depot(consts.DEPOT_ID, auto_add_zone=False)
    response = await taxi_umlaas_grocery_eta.post(
        URL,
        json={
            'depot_id': str(consts.DEPOT_ID),
            'transport_type': 'pedestrian',
            'user_location': consts.USER_LOCATION,
            'user_orders_completed': 2,
        },
        params={'offer_id': '1abc1', 'request_type': 'checkout'},
    )
    assert response.status == 200
    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)

    assert match_tries[0].kwargs['user_orders_completed'] == 2


# TODO: upload log to YT test?
