import copy

import pytest


SEARCH_PARAMS_OVERRIDE = {
    'order_id': 'order_id_1',
    'max_time': 120,
    'max_candidates': 10,
    'allow_filtered': {
        'filters': ['excluded', 'time_limit', 'cargo_limits'],
        'special_requirements': ['cargo_eds'],
    },
    'tariffs': [{'name': 'econom'}],
}


@pytest.fixture(name='mock_driver_profiles')
def _mock_driver_profiles(mockserver):
    def _wrapper(expected_request: dict = None, response: dict = None):
        @mockserver.json_handler(
            '/driver-profiles/v1/driver/profiles/proxy-retrieve',
        )
        def _mock(request):
            if expected_request:
                assert request.json == expected_request
            if response is None:
                return {
                    'profiles': [
                        {
                            'park_driver_profile_id': (
                                '7f74df331eb04ad78bc2ff25ff88a8f2_'
                                '172313ddc0174a0797b631f3539d8a85'
                            ),
                            'data': {
                                'phone_pd_ids': [],
                                'full_name': {
                                    'first_name': 'Курьер',
                                    'last_name': 'Курьерский',
                                },
                                'car_id': 'carid2',
                            },
                        },
                        {
                            'park_driver_profile_id': (
                                'a3608f8f7ee84e0b9c21862beef7e48d_'
                                'b2d6ab89e9ca4154819cdf37e954083c'
                            ),
                            'data': {
                                'phone_pd_ids': [{'pd_id': 'phone_pd_id1'}],
                                'full_name': {
                                    'first_name': 'Водитель',
                                    'middle_name': 'Безотчества',
                                    'last_name': 'Водителевский',
                                },
                                'car_id': 'carid1',
                            },
                        },
                    ],
                }
            return response

        return _mock

    return _wrapper


@pytest.fixture(name='mock_driver_rating')
def _mock_driver_rating(mockserver):
    def _wrapper(expected_request: dict = None, response: dict = None):
        @mockserver.json_handler(
            '/driver-ratings/v2/driver/rating/batch-retrieve',
        )
        def _mock(request):
            assert request.headers['X-Ya-Service-Name'] == 'manual-dispatch'
            if expected_request:
                assert request.json == expected_request
            if response is None:
                return {
                    'ratings': [
                        {
                            'unique_driver_id': '5b05603de6c22ea265465520',
                            'rating': '4.500',
                        },
                        {
                            'unique_driver_id': '5b056296e6c22ea26548c934',
                            'rating': '4.9',
                        },
                    ],
                }
            return response

        return _mock

    return _wrapper


@pytest.fixture(name='mock_fleet_vehicles')
def _mock_fleet_vehicles(mockserver):
    def _wrapper(expected_request: dict = None, response: dict = None):
        @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
        def _mock(request):
            if expected_request:
                request.json['id_in_set'] = sorted(request.json['id_in_set'])
                assert request.json == expected_request
            if response is None:
                return {
                    'vehicles': [
                        {
                            'data': {
                                'brand': 'Hyundai',
                                'model': 'Solaris',
                                'number_normalized': (
                                    'C0URIER5D9D3C70259D4A65890B814B88CD03DD'
                                ),
                            },
                            'park_id_car_id': (
                                '7f74df331eb04ad78bc2ff25ff88a8f2_carid2'
                            ),
                            'revision': '0_1598519908_357',
                        },
                        {
                            'data': {
                                'brand': 'Hyundai',
                                'model': 'Solaris',
                                'number_normalized': 'Y999YY99',
                            },
                            'park_id_car_id': (
                                'a3608f8f7ee84e0b9c21862beef7e48d_carid1'
                            ),
                            'revision': '0_1598519908_357',
                        },
                    ],
                }
            return response

        return _mock

    return _wrapper


@pytest.fixture(name='mock_contractor_transport')
def _mock_contractor_transport(mockserver):
    def _wrapper(expected_request: dict = None, response: dict = None):
        @mockserver.json_handler(
            '/contractor-transport/v1/transport-active/'
            'retrieve-by-contractor-id',
        )
        def _mock(request):
            if expected_request:
                request.json['id_in_set'] = sorted(request.json['id_in_set'])
                assert request.json == expected_request
            if response is None:
                return {
                    'contractors_transport': [
                        {
                            'contractor_id': (
                                'a3608f8f7ee84e0b9c21862beef7e48d'
                                '_b2d6ab89e9ca4154819cdf37e954083c'
                            ),
                            'transport_active': {
                                'type': 'car',
                                'vehicle_id': 'carid1',
                            },
                            'revision': '1601225131_11',
                        },
                        {
                            'contractor_id': (
                                '7f74df331eb04ad78bc2ff25ff88a8f2'
                                '_172313ddc0174a0797b631f3539d8a85'
                            ),
                            'transport_active': {'type': 'pedestrian'},
                            'revision': '1599654709_9',
                        },
                    ],
                }
            return response

        return _mock

    return _wrapper


@pytest.fixture(name='mock_candidates_orders_search')
def _mock_candidates_orders_search(mockserver):
    def _wrapper(response: dict, expected_request: dict = None):
        @mockserver.json_handler('/candidates/order-search')
        def _mock(request):
            if expected_request:
                assert request.json == expected_request
            return response

        return _mock

    return _wrapper


@pytest.fixture(name='mock_candidates_orders_satisfy')
def _mock_candidates_orders_satisfy(mockserver):
    def _wrapper(response: dict, expected_request: dict = None):
        @mockserver.json_handler('/candidates/order-satisfy')
        def _mock(request):
            if expected_request:
                assert request.json == expected_request
            return response

        return _mock

    return _wrapper


def get_order_search_request(search_params):
    search_params = copy.deepcopy(search_params)
    search_params['max_route_time'] = SEARCH_PARAMS_OVERRIDE['max_time']
    search_params['max_route_distance'] = 10000
    search_params['timeout'] = 1500

    search_params.pop('class_limits', None)
    search_params['limit'] = SEARCH_PARAMS_OVERRIDE['max_candidates']

    search_params.pop('excluded_ids', None)
    search_params.pop('excluded_license_ids', None)
    search_params.pop('excluded_car_numbers', None)

    search_params['order']['virtual_tariffs'][0]['class'] = 'econom'
    search_params['order']['virtual_tariffs'][0]['special_requirements'] = [
        {'id': 'cargo_multipoints'},
    ]
    search_params['requirements'].pop('cargo_type', None)
    search_params['allowed_classes'] = ['econom']
    return search_params


def get_order_satisfy_request(search_params, order_search_response):
    search_params = copy.deepcopy(search_params)
    search_params['allowed_classes'] = ['econom']
    search_params['driver_ids'] = [
        {'dbid': x['dbid'], 'uuid': x['uuid']}
        for x in order_search_response['candidates']
    ]
    return search_params


async def test_candidates(
        taxi_manual_dispatch,
        create_order,
        load_json,
        headers,
        mockserver,
        mock_driver_profiles,
        mock_driver_rating,
        mock_fleet_vehicles,
        mock_contractor_transport,
        mock_candidates_orders_satisfy,
        mock_candidates_orders_search,
):
    search_params = load_json('search_params.json')
    order_search_response = load_json('order_search_response.json')

    candidates_orders_search = mock_candidates_orders_search(
        response=order_search_response,
        expected_request=get_order_search_request(search_params),
    )
    candidates_orders_satisfy = mock_candidates_orders_satisfy(
        response=load_json('order_satisfy_response.json'),
        expected_request=get_order_satisfy_request(
            search_params, order_search_response,
        ),
    )
    driver_profiles = mock_driver_profiles(
        expected_request={
            'id_in_set': [
                '7f74df331eb04ad78bc2ff25ff88a8f2_'
                '172313ddc0174a0797b631f3539d8a85',
                'a3608f8f7ee84e0b9c21862beef7e48d'
                '_b2d6ab89e9ca4154819cdf37e954083c',
            ],
            'projection': [
                'data.phone_pd_ids',
                'data.full_name',
                'data.car_id',
            ],
        },
    )
    fleet_vehicles = mock_fleet_vehicles(
        expected_request={
            'id_in_set': [
                '7f74df331eb04ad78bc2ff25ff88a8f2_carid2',
                'a3608f8f7ee84e0b9c21862beef7e48d_carid1',
            ],
            'projection': ['data.brand', 'data.model'],
        },
    )
    contractor_transport = mock_contractor_transport(
        expected_request={
            'id_in_set': [
                '7f74df331eb04ad78bc2ff25ff88a8f2_'
                '172313ddc0174a0797b631f3539d8a85',
                'a3608f8f7ee84e0b9c21862beef7e48d'
                '_b2d6ab89e9ca4154819cdf37e954083c',
            ],
        },
    )
    driver_rating = mock_driver_rating(
        expected_request={
            'unique_driver_ids': [
                '5b05603de6c22ea265465520',
                '5b056296e6c22ea26548c934',
            ],
        },
    )

    create_order(order_id='order_id_1', search_params=search_params)

    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/candidates',
        json=SEARCH_PARAMS_OVERRIDE,
        headers=headers,
    )
    assert response.status_code == 200
    assert candidates_orders_search.times_called == 1
    assert candidates_orders_satisfy.times_called == 1
    assert driver_rating.times_called == 1
    assert driver_profiles.times_called == 1
    assert fleet_vehicles.times_called == 1
    assert contractor_transport.times_called == 1
    assert response.json()['polling_delay_ms'] == 30000
    assert response.json()['drivers'] == [
        {
            'name': 'Курьер Курьерский',
            'route_info': {'time': 2921, 'distance': 16436},
            'rating': 4.9,
            'park_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
            'uuid': '172313ddc0174a0797b631f3539d8a85',
            'point': [37.815984, 55.811257],
            'classes': ['econom'],
            'unique_driver_id': '5b056296e6c22ea26548c934',
            'is_satisfied': False,
            'filtered_by': {
                'filters': [
                    {'name': 'cargo_limits', 'detail': 'no cargo space'},
                    {
                        'name': 'special_requirements',
                        'detail': 'missing requirements: cargo not allowed',
                    },
                ],
            },
        },
        {
            'name': 'Водитель Безотчества Водителевский',
            'route_info': {'time': 1166, 'distance': 9194},
            'rating': 4.5,
            'point': [37.537514, 55.737717],
            'phone_pd_id': 'phone_pd_id1',
            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'uuid': 'b2d6ab89e9ca4154819cdf37e954083c',
            'classes': ['econom'],
            'unique_driver_id': '5b05603de6c22ea265465520',
            'is_satisfied': False,
            'filtered_by': {
                'filters': [
                    {'name': 'cargo_limits', 'detail': 'no cargo space'},
                    {'name': 'excluded', 'detail': 'rejected the order'},
                ],
            },
            'car': {'brand': 'Hyundai', 'model': 'Solaris'},
        },
    ]


@pytest.mark.parametrize(
    'order_allowed_classes, support_search_tariffs, '
    'order_search_calls_count, result_drivers_classes',
    [
        (
            # Order has eda classes. Search eda couriers
            ['courier', 'express', 'eda', 'lavka'],
            None,
            2,
            ['eda', 'courier'],
        ),
        (
            # Order has not eda classes. Do not search eda couriers
            ['courier', 'express'],
            None,
            1,
            ['courier'],
        ),
        (
            # Order has not eda classes.
            # Do not search eda couriers even if tariff has in search params
            ['courier', 'express'],
            [{'name': 'eda'}],
            1,
            ['courier'],
        ),
    ],
)
async def test_eda_candidates(
        taxi_manual_dispatch,
        create_order,
        load_json,
        headers,
        mockserver,
        mock_driver_profiles,
        mock_driver_rating,
        mock_fleet_vehicles,
        mock_contractor_transport,
        order_allowed_classes,
        support_search_tariffs,
        order_search_calls_count,
        result_drivers_classes,
):
    order_search_iteration = 0
    order_satisfy_iteration = 0

    @mockserver.json_handler('/candidates/order-search')
    def mock_orders_search(request):
        nonlocal order_search_iteration
        order_search_iteration += 1
        if order_search_iteration == 1:
            assert (
                request.json['allowed_classes'] == support_search_tariffs
                or order_allowed_classes
            )
            response = load_json('order_search_response_courier.json')
        else:
            assert request.json['allowed_classes'] == ['eda', 'lavka']
            assert request.json['order']['source'] == 'eats'
            assert request.json['eats_shift'] == {
                'only_active': True,
                'shift_required': True,
            }
            assert 'payment' not in request.json
            assert request.json['order']['request']['destinations'] == []
            response = load_json('order_search_response_eda.json')
        return response

    @mockserver.json_handler('/candidates/order-satisfy')
    def mock_orders_satisfy(request):
        nonlocal order_satisfy_iteration
        order_satisfy_iteration += 1
        if order_satisfy_iteration == 1:
            assert (
                request.json['allowed_classes']
                == search_params['allowed_classes']
                or order_allowed_classes
            )
            response = load_json('order_satisfy_response_courier.json')
        else:
            assert request.json['allowed_classes'] == ['eda', 'lavka']
            assert request.json['order']['source'] == 'eats'
            assert request.json['eats_shift'] == {
                'only_active': True,
                'shift_required': True,
            }
            assert 'payment' not in request.json
            assert request.json['order']['request']['destinations'] == []
            response = load_json('order_satisfy_response_eda.json')
        return response

    mock_driver_profiles()
    mock_fleet_vehicles()
    mock_contractor_transport()
    mock_driver_rating()

    search_params = load_json('search_params.json')
    search_params['allowed_classes'] = order_allowed_classes
    create_order(order_id='order_id_1', search_params=search_params)

    request_search_params = copy.deepcopy(SEARCH_PARAMS_OVERRIDE)
    if support_search_tariffs is None:
        del request_search_params['tariffs']
    else:
        request_search_params['tariffs'] = support_search_tariffs
    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/candidates', json=request_search_params, headers=headers,
    )
    assert response.status_code == 200
    assert mock_orders_search.times_called == order_search_calls_count
    assert mock_orders_satisfy.times_called == order_search_calls_count

    drivers_classes = [
        driver['classes'][0] for driver in response.json()['drivers']
    ]
    assert drivers_classes == result_drivers_classes


async def test_409(taxi_manual_dispatch, create_order, headers):
    create_order(search_params=None, order_id='order_id_1')
    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/candidates',
        json=SEARCH_PARAMS_OVERRIDE,
        headers=headers,
    )
    assert response.status_code == 409


async def test_404(taxi_manual_dispatch, headers):
    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/candidates',
        json=SEARCH_PARAMS_OVERRIDE,
        headers=headers,
    )
    assert response.status_code == 404


PIN_PARAMS = {'order_id': 'order_id_1', 'park_id': 'foo', 'driver_id': 'bar'}


async def test_pin_409(taxi_manual_dispatch, create_order, headers):
    create_order(search_params=None, order_id='order_id_1')
    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/pin-candidate', json=PIN_PARAMS, headers=headers,
    )
    assert response.status_code == 409


async def test_pin_404(taxi_manual_dispatch, headers):
    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/pin-candidate', json=PIN_PARAMS, headers=headers,
    )
    assert response.status_code == 404


async def test_pin_success(
        taxi_manual_dispatch,
        create_order,
        load_json,
        mock_driver_profiles,
        mock_candidates_orders_satisfy,
        mock_candidates_orders_search,
        mock_fleet_vehicles,
        mock_contractor_transport,
        mock_driver_rating,
        headers,
):
    search_params = load_json('search_params.json')
    order_search_response = {'candidates': []}
    candidates_orders_search = mock_candidates_orders_search(
        response=order_search_response,
        expected_request=get_order_search_request(search_params),
    )

    order_satisfy_response = load_json('order_satisfy_response.json')
    order_satisfy_response['candidates'] = order_satisfy_response[
        'candidates'
    ][:1]
    candidates_orders_satisfy = mock_candidates_orders_satisfy(
        response=order_satisfy_response,
    )

    fleet_vehicles = mock_fleet_vehicles(
        expected_request={
            'id_in_set': ['7f74df331eb04ad78bc2ff25ff88a8f2_carid2'],
            'projection': ['data.brand', 'data.model'],
        },
        response={
            'vehicles': [
                {
                    'data': {
                        'brand': 'Hyundai',
                        'model': 'Solaris',
                        'number_normalized': (
                            'C0URIER5D9D3C70259D4A65890B814B88CD03DD'
                        ),
                    },
                    'park_id_car_id': (
                        '7f74df331eb04ad78bc2ff25ff88a8f2_carid2'
                    ),
                    'revision': '0_1598519908_357',
                },
            ],
        },
    )
    contractor_transport = mock_contractor_transport(
        expected_request={
            'id_in_set': [
                '7f74df331eb04ad78bc2ff25ff88a8f2_'
                '172313ddc0174a0797b631f3539d8a85',
            ],
        },
        response={
            'contractors_transport': [
                {
                    'contractor_id': (
                        'a3608f8f7ee84e0b9c21862beef7e48d'
                        '_b2d6ab89e9ca4154819cdf37e954083c'
                    ),
                    'transport_active': {
                        'type': 'car',
                        'vehicle_id': 'carid1',
                    },
                    'revision': '1601225131_11',
                },
            ],
        },
    )
    driver_rating = mock_driver_rating(
        expected_request={'unique_driver_ids': ['5b056296e6c22ea26548c934']},
        response={
            'ratings': [
                {
                    'unique_driver_id': '5b056296e6c22ea26548c934',
                    'rating': '4.9',
                },
            ],
        },
    )
    driver_profiles = mock_driver_profiles(
        response={
            'profiles': [
                {
                    'park_driver_profile_id': (
                        '7f74df331eb04ad78bc2ff25ff88a8f2_'
                        '172313ddc0174a0797b631f3539d8a85'
                    ),
                    'data': {
                        'phone_pd_ids': [],
                        'full_name': {
                            'first_name': 'Курьер',
                            'last_name': 'Курьерский',
                        },
                        'car_id': 'carid2',
                        'park_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
                        'uuid': '172313ddc0174a0797b631f3539d8a85',
                    },
                },
            ],
        },
    )

    create_order(order_id='order_id_1', search_params=search_params)

    pin_params = PIN_PARAMS
    pin_params['park_id'] = order_satisfy_response['candidates'][0]['dbid']
    pin_params['driver_id'] = order_satisfy_response['candidates'][0]['uuid']

    pin_response = await taxi_manual_dispatch.post(
        '/v1/dispatch/pin-candidate', json=pin_params, headers=headers,
    )
    assert pin_response.status_code == 200
    assert driver_profiles.times_called == 1
    assert candidates_orders_satisfy.times_called == 1

    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/candidates',
        json=SEARCH_PARAMS_OVERRIDE,
        headers=headers,
    )
    assert response.status_code == 200
    assert candidates_orders_search.times_called == 1
    assert candidates_orders_satisfy.times_called == 2
    assert driver_rating.times_called == 1
    assert driver_profiles.times_called == 2
    assert fleet_vehicles.times_called == 1
    assert contractor_transport.times_called == 1
    assert response.json()['polling_delay_ms'] == 30000
    assert response.json()['drivers'] == [
        {
            'name': 'Курьер Курьерский',
            'rating': 4.9,
            'route_info': {'time': 2921, 'distance': 16436},
            'park_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
            'uuid': '172313ddc0174a0797b631f3539d8a85',
            'point': [37.815984, 55.811257],
            'classes': ['econom'],
            'unique_driver_id': '5b056296e6c22ea26548c934',
            'is_satisfied': False,
            'filtered_by': {
                'filters': [
                    {'name': 'cargo_limits', 'detail': 'no cargo space'},
                    {
                        'name': 'special_requirements',
                        'detail': 'missing requirements: cargo not allowed',
                    },
                ],
            },
            'is_manual': True,
        },
    ]
