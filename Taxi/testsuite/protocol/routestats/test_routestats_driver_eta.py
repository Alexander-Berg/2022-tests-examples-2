import json

import pytest


@pytest.mark.parametrize('do_pass_tariff_requirements', (True, False))
@pytest.mark.parametrize(
    'tariffs_without_drivers',
    (
        pytest.param([]),
        pytest.param(['econom']),
        pytest.param(['econom', 'business']),
    ),
)
@pytest.mark.parametrize('driver_eta_success', (True, False))
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ROUTESTATS_PRICE_PROMO_SUGGEST_CLASSES={
        'econom': ['business', 'comfortplus'],
        'business': ['comfortplus'],
    },
    DRIVER_ETA_CLIENT_QOS={'__default__': {'attemps': 1, 'timeout-ms': 200}},
)
@pytest.mark.experiments3(
    name='routestats_parallel_driver_eta',
    consumers=['protocol/routestats'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'e.g. Moscow popular tariffs',
            'value': {
                'enabled': True,
                'split_by_tariffs': [['econom', 'comfortplus']],
            },
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.user_experiments('fixed_price', 'routestats_fixed_price_time')
def test_parallel_driver_eta_requests(
        local_services_base,
        local_services_fixed_price,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        do_pass_tariff_requirements,
        tariffs_without_drivers,
        driver_eta_success,
):
    driver_eta_calls = []

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        data = json.loads(request.get_data())
        driver_eta_calls.append(data['classes'])

        if not driver_eta_success:
            return mockserver.make_response('', 500)

        retval = load_json('driver_eta.json')
        classes_to_remove = set()
        for class_name, class_info in retval['classes'].items():
            if class_name not in data['classes']:
                classes_to_remove.add(class_name)
            elif class_name in tariffs_without_drivers:
                class_info['found'] = False
                del class_info['estimated_distance']
                del class_info['estimated_time']

        for class_name in classes_to_remove:
            retval['classes'].pop(class_name)

        assert len(retval['classes']) == len(data['classes'])
        return retval

    request = load_json('request.json')
    if not do_pass_tariff_requirements:
        request.pop('tariff_requirements')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    assert mock_driver_eta.times_called == 2
    # One request was for popular tariffs
    assert ['econom', 'comfortplus'] in driver_eta_calls

    for tariff in response.json()['service_levels']:
        assert 'title' not in tariff

        if driver_eta_success:
            if tariff['class'] in tariffs_without_drivers:
                assert 'estimated_waiting' not in tariff
                assert tariff['tariff_unavailable'] == {
                    'code': 'no_free_cars_nearby',
                    'message': 'No available cars',
                }
            else:
                assert 'estimated_waiting' in tariff
                assert 'tariff_unavailable' not in tariff
        else:
            assert 'estimated_waiting' not in tariff
            assert 'tariff_unavailable' not in tariff


@pytest.mark.config(
    DRIVER_ETA_CLIENT_QOS={'__default__': {'attemps': 1, 'timeout-ms': 200}},
)
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.parametrize(
    ('driver_eta_response_status',),
    (
        pytest.param(200, id='eta_response_success'),
        pytest.param(500, id='eta_response_error'),
    ),
)
@pytest.mark.parametrize('driver_eta_skip_error_enabled', (False, True))
def test_driver_eta_error(
        local_services_fixed_price,
        taxi_protocol,
        pricing_data_preparer,
        mockserver,
        load_json,
        config,
        driver_eta_response_status,
        driver_eta_skip_error_enabled,
):
    # prepare driver-eta response
    driver_eta_response = load_json('driver_eta.json')
    del driver_eta_response['classes']['minivan']  # make no cars for minivan
    waiting_time_by_class = {
        class_name: data['estimated_time']
        for class_name, data in driver_eta_response['classes'].items()
    }

    config.set_values(
        {'DRIVER_ETA_SKIP_ERROR_ENABLED': driver_eta_skip_error_enabled},
    )

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        response = ''
        if driver_eta_response_status == 200:
            response = json.dumps(driver_eta_response)
        return mockserver.make_response(response, driver_eta_response_status)

    response = taxi_protocol.post('3.0/routestats', load_json('request.json'))

    assert response.status_code == 200
    assert mock_driver_eta.times_called == 1

    for tariff in response.json()['service_levels']:
        if driver_eta_response_status == 200:
            assert tariff.get('estimated_waiting', {}).get(
                'seconds',
            ) == waiting_time_by_class.get(tariff['class'])
        else:
            assert 'estimated_waiting' not in tariff
            assert 'title' not in tariff


DRIVER_ETA_QOS = {'attempts': 1, 'timeout-ms': 200}


@pytest.mark.config(
    DYNAMIC_TIMEOUT_NETWORK_SETTINGS={'__default__': {'lag_ms': 150}},
)
@pytest.mark.parametrize('expected_timeout', [50])
@pytest.mark.parametrize('is_lightweight', (True, False))
@pytest.mark.experiments3(
    name='routestats_eta_dynamic_timeout',
    consumers=['protocol/routestats'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Enabled for all',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.user_experiments('no_cars_order_available')
def test_driver_eta_request_with_timeout(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        mockserver,
        load_json,
        config,
        expected_timeout,
        is_lightweight,
):
    if is_lightweight:
        config.set(
            DRIVER_ETA_CLIENT_QOS={
                '/eta:routestats-lightweight': DRIVER_ETA_QOS,
            },
        )
    else:
        config.set(
            DRIVER_ETA_CLIENT_QOS={'/eta:routestats-primary': DRIVER_ETA_QOS},
        )

    local_services.set_driver_eta_request_expected_args(
        {'timeout_ms': str(expected_timeout)},
    )  # qos - lag (200 - 150)
    local_services.set_driver_eta_expected_times_called(1)

    req = load_json('request.json')
    req['is_lightweight'] = is_lightweight
    response = taxi_protocol.post('3.0/routestats', req)

    assert response.status_code == 200
    for sl in response.json()['service_levels']:
        if not is_lightweight:
            assert sl.get('estimated_waiting') is not None, sl


@pytest.mark.user_experiments('no_cars_order_available')
def test_driver_eta_request_with_auth_context(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        mockserver,
        load_json,
):
    local_services.set_driver_eta_request_expected_headers(
        {
            'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
            'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
        },
    )
    req = load_json('request.json')
    req['is_lightweight'] = True
    response = taxi_protocol.post('3.0/routestats', req)
    assert response.status_code == 200
