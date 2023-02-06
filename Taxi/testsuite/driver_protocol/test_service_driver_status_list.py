import pytest

from taxi_tests.utils import ordered_object

DRIVER_PROFILE_LIST_URL = '/parks/driver-profiles/list'
DRIVER_PROFILE_FIELDS = [
    'id',
    'driver_license',
    'last_name',
    'middle_name',
    'first_name',
    'phones',
    'work_rule_id',
]
CAR_FIELDS = ['model', 'brand', 'normalized_number', 'callsign']


def search_drivers(start=0, finish=7, extra_driver=None, extra_car=None):
    profiles = []
    for i in range(start, finish):
        num = str(999 + i)
        profile = {
            'driver_profile': {
                'id': 'driver' + num,
                'driver_license': {
                    'normalized_number': 'driver' + num + '_license',
                },
            },
        }
        if extra_driver is not None:
            for key, value in extra_driver.items():
                profile['driver_profile'][key] = value
        if extra_car is not None:
            profile['car'] = {}
            for key, value in extra_car.items():
                profile['car'][key] = value
        profiles.append(profile)
    return {'driver_profiles': profiles, 'parks': [{'id': 'some'}]}


def make_request(driver_ids):
    result = {
        'query': {'park': {'id': 'park66'}},
        'fields': {'driver_profile': DRIVER_PROFILE_FIELDS, 'car': CAR_FIELDS},
        'removed_drivers_mode': 'as_normal_driver',
    }
    if len(driver_ids):
        result['query']['park']['driver_profile'] = {'id': driver_ids}

    return result


def test_empty(taxi_driver_protocol, mockserver):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        return {}

    response = taxi_driver_protocol.post('service/driver/status/list')
    assert get.times_called == 0
    assert response.status_code == 400


@pytest.mark.redis_store(
    ['hset', 'park66:STATUS_DRIVERS', 'driver999', 2],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver999',
        '"2018-12-17T00:00:02.42538Z"',
    ],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1000',
        '"2018-12-17T00:00:00.42538Z"',
    ],
)
def test_empty_lists(taxi_driver_protocol, mockserver):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == make_request([])
        return search_drivers(0, 2)

    response = taxi_driver_protocol.post(
        'service/driver/status/list', {'park_id': 'park66'},
    )
    assert response.status_code == 200

    json_res = response.json()
    expected_response = {
        'statuses': [
            {
                'driver_id': 'driver999',
                'payment_type': 'none',
                'status': 'free',
                'status_updated_at': '2018-12-17T00:00:02.425380Z',
            },
            {
                'driver_id': 'driver1000',
                'payment_type': 'none',
                'status': 'offline',
                'status_updated_at': '2018-12-17T00:00:00.425380Z',
            },
        ],
    }
    ordered_object.assert_eq(json_res, expected_response, ['statuses'])


def test_wrong_json(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/driver/status/list', {'so_wrong': 'such_fail'},
    )
    assert response.status_code == 400


@pytest.mark.config(DRIVER_PAYMENT_TYPE_OPTION_ENABLED=True)
@pytest.mark.redis_store(
    ['hset', 'park66:STATUS_DRIVERS', 'driver999', 2],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver999',
        '"2018-12-17T00:00:02.42538Z"',
    ],
)
def test_single_valid_with_driver_profiles(taxi_driver_protocol, mockserver):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == make_request(['driver999'])
        return search_drivers()

    data = {
        'park_id': 'park66',
        'driver_profiles': [{'driver_id': 'driver999'}],
    }

    response = taxi_driver_protocol.post('service/driver/status/list', data)
    assert response.status_code == 200
    resp_json = response.json()

    assert resp_json == {
        'statuses': [
            {
                'driver_id': 'driver999',
                'payment_type': 'online',
                'status': 'free',
                'status_updated_at': '2018-12-17T00:00:02.425380Z',
            },
        ],
    }


def test_single_driver_park_mismatch_with_driver_profiles(
        taxi_driver_protocol, mockserver,
):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == make_request(['driver998'])
        return search_drivers()

    data = {
        'park_id': 'park66',
        'driver_profiles': [{'driver_id': 'driver998'}],
    }

    response = taxi_driver_protocol.post('service/driver/status/list', data)
    assert response.status_code == 200
    resp_json = response.json()

    assert resp_json == {
        'statuses': [{'driver_id': 'driver998', 'error': 'driver_not_found'}],
    }


@pytest.mark.redis_store(
    ['hset', 'park66:STATUS_DRIVERS', 'driver999', 2],
    ['sadd', 'park66:STATUS_DRIVERS:INTEGRATOR', 'driver999'],
)
def test_park_status_overlap_with_driver_profiles(
        taxi_driver_protocol, redis_store, mockserver,
):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == make_request(['driver999'])
        return search_drivers()

    data = {
        'park_id': 'park66',
        'driver_profiles': [{'driver_id': 'driver999'}],
    }

    response = taxi_driver_protocol.post('service/driver/status/list', data)
    assert response.status_code == 200
    resp_json = response.json()

    assert len(resp_json['statuses']) == 1
    assert resp_json['statuses'][0]['status'] == 'busy'

    # remove integrator order
    redis_store.srem('park66:STATUS_DRIVERS:INTEGRATOR', 'driver999')
    response = taxi_driver_protocol.post('service/driver/status/list', data)
    assert response.status_code == 200
    resp_json = response.json()

    assert len(resp_json['statuses']) == 1
    assert resp_json['statuses'][0]['status'] == 'free'


@pytest.mark.config(DRIVER_PAYMENT_TYPE_OPTION_ENABLED=True)
@pytest.mark.redis_store(
    ['hset', 'park66:STATUS_DRIVERS', 'driver999', 0],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver999',
        '"2018-12-17T00:00:00.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1000', 1],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1000',
        '"2018-12-17T00:00:01.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1001', 2],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1001',
        '"2018-12-17T00:00:02.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1002', 3],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1002',
        '"2018-12-17T00:00:03.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1003', 4],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1003',
        '"2018-12-17T00:00:04.42538Z"',
    ],
)
def test_multiple_with_driver_profiles(taxi_driver_protocol, mockserver):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == make_request(
            [
                'driver999',
                'driver1000',
                'driver1001',
                'driver1002',
                'driver1003',
            ],
        )
        return search_drivers()

    data = {
        'park_id': 'park66',
        'driver_profiles': [
            {'driver_id': 'driver999'},
            {'driver_id': 'driver1000'},
            {'driver_id': 'driver1001'},
            {'driver_id': 'driver1002'},
            {'driver_id': 'driver1003'},
        ],
    }

    response = taxi_driver_protocol.post('service/driver/status/list', data)
    assert response.status_code == 200
    resp_json = response.json()
    expected_response = {
        'statuses': [
            {
                'driver_id': 'driver999',
                'payment_type': 'online',
                'status': 'offline',
                'status_updated_at': '2018-12-17T00:00:00.425380Z',
            },
            {
                'driver_id': 'driver1000',
                'payment_type': 'cash',
                'status': 'busy',
                'status_updated_at': '2018-12-17T00:00:01.425380Z',
            },
            {
                'driver_id': 'driver1001',
                'payment_type': 'none',
                'status': 'free',
                'status_updated_at': '2018-12-17T00:00:02.425380Z',
            },
            {
                'driver_id': 'driver1002',
                'payment_type': 'cash',
                'status': 'in_order_free',
                'status_updated_at': '2018-12-17T00:00:03.425380Z',
            },
            {
                'driver_id': 'driver1003',
                'payment_type': 'none',
                'status': 'in_order_busy',
                'status_updated_at': '2018-12-17T00:00:04.425380Z',
            },
        ],
    }
    ordered_object.assert_eq(resp_json, expected_response, ['statuses'])


@pytest.mark.redis_store(
    ['hset', 'park65:STATUS_DRIVERS', 'driver998', 2],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver998',
        '"2018-12-17T00:00:02.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1000', 2],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1000',
        '"2018-12-17T00:00:02.42538Z"',
    ],
)
def test_multiple_driver_park_mismatch_with_driver_profiles(
        taxi_driver_protocol, mockserver,
):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == make_request(['driver998', 'driver1000'])
        return search_drivers()

    data = {
        'park_id': 'park66',
        'driver_profiles': [
            {'driver_id': 'driver998'},  # mismatch here
            {'driver_id': 'driver1000'},
        ],
    }

    response = taxi_driver_protocol.post('service/driver/status/list', data)
    assert response.status_code == 200
    resp_json = response.json()
    expected_response = {
        'statuses': [
            {'driver_id': 'driver998', 'error': 'driver_not_found'},
            {
                'driver_id': 'driver1000',
                'payment_type': 'none',
                'status': 'free',
                'status_updated_at': '2018-12-17T00:00:02.425380Z',
            },
        ],
    }
    ordered_object.assert_eq(resp_json, expected_response, ['statuses'])


@pytest.mark.config(DRIVER_PAYMENT_TYPE_OPTION_ENABLED=False)
@pytest.mark.redis_store(
    ['hset', 'park66:STATUS_DRIVERS', 'driver999', 0],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver999',
        '"2018-12-17T00:00:00.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1000', 1],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1000',
        '"2018-12-17T00:00:01.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1001', 2],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1001',
        '"2018-12-17T00:00:02.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1002', 3],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1002',
        '"2018-12-17T00:00:03.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1003', 4],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1003',
        '"2018-12-17T00:00:04.42538Z"',
    ],
)
@pytest.mark.parametrize(
    'request_body, driver_profiles_search_request,'
    'driver_profiles_search_response, expected_response',
    [
        (
            {'park_id': 'park66', 'statuses': ['free', 'in_order_free']},
            make_request(['driver1001', 'driver1002']),
            search_drivers(2, 4),
            {
                'statuses': [
                    {
                        'driver_id': 'driver1001',
                        'payment_type': 'none',
                        'status': 'free',
                        'status_updated_at': '2018-12-17T00:00:02.425380Z',
                    },
                    {
                        'driver_id': 'driver1002',
                        'payment_type': 'none',
                        'status': 'in_order_free',
                        'status_updated_at': '2018-12-17T00:00:03.425380Z',
                    },
                ],
            },
        ),
        (
            {'park_id': 'park66', 'statuses': ['offline', 'busy']},
            make_request([]),
            search_drivers(),
            {
                'statuses': [
                    {
                        'driver_id': 'driver999',
                        'payment_type': 'none',
                        'status': 'offline',
                        'status_updated_at': '2018-12-17T00:00:00.425380Z',
                    },
                    {
                        'driver_id': 'driver1000',
                        'payment_type': 'none',
                        'status': 'busy',
                        'status_updated_at': '2018-12-17T00:00:01.425380Z',
                    },
                    {
                        'driver_id': 'driver1004',
                        'payment_type': 'none',
                        'status': 'offline',
                    },
                    {
                        'driver_id': 'driver1005',
                        'payment_type': 'none',
                        'status': 'offline',
                    },
                ],
            },
        ),
    ],
)
def test_multiple_with_statuses_list(
        taxi_driver_protocol,
        mockserver,
        request_body,
        driver_profiles_search_request,
        driver_profiles_search_response,
        expected_response,
):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        ordered_object.assert_eq(
            request.json,
            driver_profiles_search_request,
            ['query.park.driver_profile.id'],
        )
        return driver_profiles_search_response

    response = taxi_driver_protocol.post(
        'service/driver/status/list', json=request_body,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), expected_response, ['statuses'])


@pytest.mark.config(DRIVER_PAYMENT_TYPE_OPTION_ENABLED=True)
@pytest.mark.redis_store(
    ['hset', 'park66:STATUS_DRIVERS', 'driver999', 0],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver999',
        '"2018-12-17T00:00:00.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1000', 1],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1000',
        '"2018-12-17T00:00:01.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1001', 2],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1001',
        '"2018-12-17T00:00:02.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1002', 3],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1002',
        '"2018-12-17T00:00:03.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1003', 4],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1003',
        '"2018-12-17T00:00:04.42538Z"',
    ],
)
@pytest.mark.parametrize(
    'driver_profiles_search_request, request_data, expected_response',
    [
        (
            make_request(['driver999', 'driver1003']),
            {
                'park_id': 'park66',
                'driver_profiles': [
                    {'driver_id': 'driver999'},
                    {'driver_id': 'driver1003'},
                ],
                'statuses': ['busy', 'free'],
            },
            {'statuses': []},
        ),
        (
            make_request(['driver999', 'driver1000', 'driver1001']),
            {
                'park_id': 'park66',
                'driver_profiles': [
                    {'driver_id': 'driver999'},
                    {'driver_id': 'driver1000'},
                    {'driver_id': 'driver1001'},
                ],
                'statuses': ['free'],
            },
            {
                'statuses': [
                    {
                        'driver_id': 'driver1001',
                        'payment_type': 'none',
                        'status': 'free',
                        'status_updated_at': '2018-12-17T00:00:02.425380Z',
                    },
                ],
            },
        ),
    ],
)
def test_multiple(
        taxi_driver_protocol,
        mockserver,
        driver_profiles_search_request,
        request_data,
        expected_response,
):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == driver_profiles_search_request
        return search_drivers()

    response = taxi_driver_protocol.post(
        'service/driver/status/list', request_data,
    )
    assert response.status_code == 200

    ordered_object.assert_eq(response.json(), expected_response, ['statuses'])


@pytest.mark.config(DRIVER_PAYMENT_TYPE_OPTION_ENABLED=False)
@pytest.mark.redis_store(
    ['hset', 'park66:STATUS_DRIVERS', 'driver999', 0],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver999',
        '"2018-12-17T00:00:00.42538Z"',
    ],
    ['hset', 'park66:STATUS_DRIVERS', 'driver1000', 1],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver1000',
        'invalid_datetime',
    ],
)
@pytest.mark.parametrize(
    'driver_profiles_search_response, request_data,' 'expected_response',
    [
        (
            make_request(['driver999', 'driver1000']),
            {
                'park_id': 'park66',
                'driver_profiles': [
                    {'driver_id': 'driver999'},
                    {'driver_id': 'driver1000'},
                ],
                'statuses': ['offline', 'busy'],
            },
            {
                'statuses': [
                    {
                        'driver_id': 'driver999',
                        'payment_type': 'none',
                        'status': 'offline',
                        'status_updated_at': '2018-12-17T00:00:00.425380Z',
                    },
                    {
                        'driver_id': 'driver1000',
                        'payment_type': 'none',
                        'status': 'busy',
                    },
                ],
            },
        ),
    ],
)
def test_invalid_data_in_redis(
        taxi_driver_protocol,
        mockserver,
        driver_profiles_search_response,
        request_data,
        expected_response,
):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == driver_profiles_search_response
        return search_drivers()

    response = taxi_driver_protocol.post(
        'service/driver/status/list', request_data,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


def make_response_with_extra_fields(extra_fields):
    status = {
        'driver_id': 'driver999',
        'payment_type': 'online',
        'status': 'free',
        'status_updated_at': '2018-12-17T00:00:02.425380Z',
    }
    for key, value in extra_fields.items():
        status[key] = value

    return {'statuses': [status]}


@pytest.mark.config(DRIVER_PAYMENT_TYPE_OPTION_ENABLED=True)
@pytest.mark.redis_store(
    ['hset', 'park66:STATUS_DRIVERS', 'driver999', 2],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver999',
        '"2018-12-17T00:00:02.42538Z"',
    ],
)
@pytest.mark.parametrize(
    'parks_response, expected_response',
    [
        (search_drivers(), make_response_with_extra_fields({})),
        (
            search_drivers(0, 7, {'last_name': 'last'}, None),
            make_response_with_extra_fields({'last_name': 'last'}),
        ),
        (
            search_drivers(0, 7, {'first_name': 'asd'}, None),
            make_response_with_extra_fields({'first_name': 'asd'}),
        ),
        (
            search_drivers(0, 7, {'middle_name': 'asd'}, None),
            make_response_with_extra_fields({'middle_name': 'asd'}),
        ),
        (
            search_drivers(0, 7, {'phones': []}, None),
            make_response_with_extra_fields({'phones': []}),
        ),
        (
            search_drivers(0, 7, {'phones': ['+123']}, None),
            make_response_with_extra_fields({'phones': ['+123']}),
        ),
        (
            search_drivers(0, 7, {'phones': ['+123', '+456']}, None),
            make_response_with_extra_fields({'phones': ['+123', '+456']}),
        ),
        (
            search_drivers(0, 7, None, {'brand': 'skoda'}),
            make_response_with_extra_fields({'car_brand': 'skoda'}),
        ),
        (
            search_drivers(0, 7, None, {'model': 'asd'}),
            make_response_with_extra_fields({'car_model': 'asd'}),
        ),
        (
            search_drivers(0, 7, None, {'normalized_number': 'asd'}),
            make_response_with_extra_fields({'car_number': 'asd'}),
        ),
        (
            search_drivers(0, 7, {'work_rule_id': 'asd'}, None),
            make_response_with_extra_fields({'work_rule_id': 'asd'}),
        ),
        (
            search_drivers(0, 7, None, {'callsign': 'asd'}),
            make_response_with_extra_fields({'car_callsign': 'asd'}),
        ),
    ],
)
def test_extra_fields(
        taxi_driver_protocol, mockserver, parks_response, expected_response,
):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == make_request(['driver999'])
        return parks_response

    data = {
        'park_id': 'park66',
        'driver_profiles': [{'driver_id': 'driver999'}],
    }

    response = taxi_driver_protocol.post('service/driver/status/list', data)
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.redis_store(
    ['sadd', 'park66:STATUS_DRIVERS:INTEGRATOR', 'driver999'],
)
@pytest.mark.parametrize(
    'server_status, expected_status', [(2, 'busy'), (3, 'in_order_free')],
)
def test_status_combining(
        taxi_driver_protocol,
        redis_store,
        mockserver,
        server_status,
        expected_status,
):
    redis_store.hset('park66:STATUS_DRIVERS', 'driver999', server_status)

    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == make_request(['driver999'])
        return search_drivers()

    data = {
        'park_id': 'park66',
        'driver_profiles': [{'driver_id': 'driver999'}],
    }

    response = taxi_driver_protocol.post('service/driver/status/list', data)
    assert response.status_code == 200
    resp_json = response.json()

    assert len(resp_json['statuses']) == 1
    assert resp_json['statuses'][0]['status'] == expected_status


def test_handle_empty_list(taxi_driver_protocol, mockserver):
    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == make_request([])
        return search_drivers(0, -1)

    response = taxi_driver_protocol.post(
        'service/driver/status/list', {'park_id': 'park66'},
    )
    assert response.status_code == 200

    expected_response = {'statuses': []}
    ordered_object.assert_eq(response.json(), expected_response, ['statuses'])


@pytest.mark.config(DRIVER_PAYMENT_TYPE_OPTION_ENABLED=True)
@pytest.mark.redis_store(
    ['hset', 'park66:STATUS_DRIVERS', 'driver999', 2],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:park66',
        'driver999',
        '"2018-12-17T00:00:02.42538Z"',
    ],
)
@pytest.mark.parametrize(
    'use_license_id,payment_type', [(False, 'online'), (True, 'cash')],
)
def test_payement_type_pd_id(
        taxi_driver_protocol, mockserver, config, use_license_id, payment_type,
):

    config.set_values(
        dict(DRIVER_PAYMENT_TYPES_PD_ID_USAGE={'__default__': use_license_id}),
    )

    @mockserver.json_handler(DRIVER_PROFILE_LIST_URL)
    def get(request):
        assert request.json == make_request(['driver999'])
        return search_drivers()

    data = {
        'park_id': 'park66',
        'driver_profiles': [{'driver_id': 'driver999'}],
    }

    response = taxi_driver_protocol.post('service/driver/status/list', data)
    assert response.status_code == 200
    resp_json = response.json()

    assert resp_json == {
        'statuses': [
            {
                'driver_id': 'driver999',
                'payment_type': payment_type,
                'status': 'free',
                'status_updated_at': '2018-12-17T00:00:02.425380Z',
            },
        ],
    }
