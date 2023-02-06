import copy
import json

import pytest

import tests_driver_orders_app_api.redis_helpers as rh


@pytest.mark.experiments3(filename='exp3_config_create_settings.json')
@pytest.mark.parametrize('taximeter_platform', ['ios', 'android'])
async def test_create_order(
        taxi_driver_orders_app_api,
        taxi_driver_orders_app_api_monitor,
        driver_profiles,
        fleet_parks,
        driver_orders_builder,
        redis_store,
        load_json,
        load,
        taximeter_platform,
        stq,
):
    await taxi_driver_orders_app_api.tests_control(reset_metrics=True)

    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}

    builder_setcar = json.loads(load('setcar.json'))
    driver_orders_builder.set_v2_setcar_resp(
        {'setcar': builder_setcar, 'setcar_push': {}},
    )

    driver_profiles.set_platform(taximeter_platform)

    rh.set_driver_status(redis_store, 'park_id', 'driver_profile_id', '2')

    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/create',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'order_id': 'order_id',
                'driver': {
                    'park_id': 'park_id',
                    'driver_profile_id': 'driver_profile_id',
                    'alias_id': 'alias_id',
                },
                'is_multioffer': False,
                'is_chain_order': False,
                'is_logistic_order': False,
                'is_reposition': False,
            },
        ),
    )

    rh.check_order_setcar_items(redis_store, 'park_id', 'alias_id')

    rh.check_setcar_driver_reserv(
        redis_store, 'park_id', 'driver_profile_id', 'alias_id',
    )

    assert (
        stq.driver_orders_send_communications_notifications.times_called == 1
    )

    http_error_metrics = await taxi_driver_orders_app_api_monitor.get_metric(
        'create_error_response_codes',
    )

    assert http_error_metrics == {'ok': 1, 'start': 1}

    assert response.status_code == 200


@pytest.mark.experiments3(filename='exp3_config_create_settings.json')
@pytest.mark.parametrize(
    'driver_status_value,reserv_orders_len,matched,message,metrics',
    [
        (
            '0',
            0,
            False,
            'driver_status_not_free check failed',
            {'start': 1, 'driver_status_not_free': 1},
        ),
        (
            '1',
            0,
            False,
            'driver_status_not_free check failed',
            {'start': 1, 'driver_status_not_free': 1},
        ),
        ('2', 0, True, None, {'start': 1, 'ok': 1}),
        (
            '3',
            0,
            False,
            'driver_status_not_free check failed',
            {'start': 1, 'driver_status_not_free': 1},
        ),
        (
            '4',
            0,
            False,
            'driver_status_not_free check failed',
            {'start': 1, 'driver_status_not_free': 1},
        ),
        (
            '2',
            1,
            False,
            'driver_has_order_in_work check failed',
            {'start': 1, 'driver_has_order_in_work': 1},
        ),
        (
            '2',
            2,
            False,
            'driver_has_order_in_work check failed',
            {'start': 1, 'driver_has_order_in_work': 1},
        ),
    ],
    ids=[
        'offline',
        'busy',
        'free',
        'in_order_busy',
        'in_order_free',
        'one_reserv',
        'two_reserv',
    ],
)
async def test_create_order_check_status(
        taxi_driver_orders_app_api,
        taxi_driver_orders_app_api_monitor,
        fleet_parks,
        driver_orders_builder,
        redis_store,
        load_json,
        load,
        driver_status_value,
        reserv_orders_len,
        matched,
        message,
        metrics,
):
    await taxi_driver_orders_app_api.tests_control(reset_metrics=True)

    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}

    builder_setcar = json.loads(load('setcar.json'))
    driver_orders_builder.set_v2_setcar_resp(
        {'setcar': builder_setcar, 'setcar_push': {}},
    )

    rh.set_driver_status(
        redis_store, 'park_id', 'driver_profile_id', driver_status_value,
    )

    for i in range(reserv_orders_len):
        setcar = copy.deepcopy(builder_setcar)
        alias_id = '{}_{}'.format('alias_id', i)
        setcar['alias_id'] = alias_id
        rh.set_redis_for_order_cancelling(
            redis_store, 'park_id', alias_id, 'driver_profile_id', setcar,
        )

    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/create',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'order_id': 'order_id',
                'driver': {
                    'park_id': 'park_id',
                    'driver_profile_id': 'driver_profile_id',
                    'alias_id': 'alias_id',
                },
                'is_multioffer': False,
                'is_chain_order': False,
                'is_logistic_order': False,
                'is_reposition': False,
            },
        ),
    )

    assert driver_orders_builder.v2_setcar.times_called == int(matched)

    http_error_metrics = await taxi_driver_orders_app_api_monitor.get_metric(
        'create_error_response_codes',
    )

    assert http_error_metrics == metrics

    assert response.status_code == (200 if matched else 410)

    if message is not None:
        assert response.json().get('message') == message


@pytest.mark.experiments3(filename='exp3_config_create_settings.json')
@pytest.mark.parametrize(
    'driver_status_value,reserv_orders_len,matched,message,metrics',
    [
        (
            '0',
            0,
            False,
            'driver_status_not_free check failed',
            {'start': 1, 'driver_status_not_free': 1},
        ),
        ('1', 0, True, None, {'start': 1, 'ok': 1}),
        ('2', 0, True, None, {'start': 1, 'ok': 1}),
        ('3', 0, True, None, {'start': 1, 'ok': 1}),
        ('4', 0, True, None, {'start': 1, 'ok': 1}),
        ('2', 1, True, None, {'start': 1, 'ok': 1}),
        ('2', 2, True, None, {'start': 1, 'ok': 1}),
    ],
    ids=[
        'offline',
        'busy',
        'free',
        'in_order_busy',
        'in_order_free',
        'one_reserv',
        'two_reserv',
    ],
)
async def test_create_multioffer(
        taxi_driver_orders_app_api,
        taxi_driver_orders_app_api_monitor,
        contractor_orders_multioffer,
        fleet_parks,
        driver_orders_builder,
        redis_store,
        taxi_config,
        load_json,
        load,
        driver_status_value,
        reserv_orders_len,
        matched,
        message,
        metrics,
):
    await taxi_driver_orders_app_api.tests_control(reset_metrics=True)

    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}

    builder_setcar = json.loads(load('setcar.json'))
    driver_orders_builder.set_v2_setcar_resp(
        {'setcar': builder_setcar, 'setcar_push': {}},
    )

    rh.set_driver_status(
        redis_store, 'park_id', 'driver_profile_id', driver_status_value,
    )

    for i in range(reserv_orders_len):
        setcar = copy.deepcopy(builder_setcar)
        alias_id = '{}_{}'.format('alias_id', i)
        setcar['alias_id'] = alias_id
        rh.set_redis_for_order_cancelling(
            redis_store, 'park_id', alias_id, 'driver_profile_id', setcar,
        )

    rh.set_setcared(
        redis_store,
        'park_id',
        'driver_profile_id',
        'alias_id',
        builder_setcar,
    )

    taxi_config.set_values(
        {
            'DRIVER_ORDERS_APP_API_SEND_COMMUNICATIONS_SETTINGS': {
                'send_cancel_order_over_stq': True,
                'send_force_polling_order_over_stq': True,
            },
            'DRIVER_ORDERS_APP_API_SENDING_PUSH_SETTINGS': {
                'price_changing_push_notification': True,
                'force_polling_order_push_notification': True,
                'order_canceled_push_notification': True,
            },
        },
    )

    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/create',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'order_id': 'order_id',
                'driver': {
                    'park_id': 'park_id',
                    'driver_profile_id': 'driver_profile_id',
                    'alias_id': 'alias_id',
                },
                'is_multioffer': True,
                'is_chain_order': False,
                'is_logistic_order': False,
                'is_reposition': False,
            },
        ),
    )

    assert driver_orders_builder.v2_setcar.times_called == int(matched)

    http_error_metrics = await taxi_driver_orders_app_api_monitor.get_metric(
        'create_error_response_codes',
    )

    assert http_error_metrics == metrics

    assert response.status_code == (200 if matched else 410)

    if message is not None:
        assert response.json().get('message') == message

    assert contractor_orders_multioffer.state.times_called == 0

    rh.check_setcar_driver_reserv(
        redis_store, 'park_id', 'driver_profile_id', 'alias_id', matched,
    )
    rh.check_driver_cancel_request(
        redis_store, 'park_id', 'alias_id', 'driver_profile_id', not matched,
    )


@pytest.mark.experiments3(filename='exp3_config_create_settings.json')
@pytest.mark.parametrize(
    'is_multioffer,has_setcar,has_cancelrequest,has_completerequest,code,'
    'message,metrics',
    [
        (
            False,
            True,
            False,
            False,
            200,
            None,
            {'already_created': 1, 'start': 1},
        ),
        (True, True, False, False, 200, None, {'ok': 1, 'start': 1}),
        (
            False,
            False,
            True,
            False,
            410,
            'Order has already been cancelled',
            {'order_cancelled': 1, 'start': 1},
        ),
        (
            True,
            False,
            True,
            False,
            410,
            'Order has already been cancelled',
            {'order_cancelled': 1, 'start': 1},
        ),
        (
            False,
            False,
            False,
            True,
            410,
            'Order has already been completed',
            {'order_completed': 1, 'start': 1},
        ),
        (
            True,
            False,
            False,
            True,
            410,
            'Order has already been completed',
            {'order_completed': 1, 'start': 1},
        ),
    ],
    ids=[
        'already_created',
        'already_created_multioffer',
        'cancelled',
        'cancelled_multioffer',
        'completed',
        'completed_multioffer',
    ],
)
async def test_create_completed_cancelled_or_setcared(
        taxi_driver_orders_app_api,
        taxi_driver_orders_app_api_monitor,
        fleet_parks,
        driver_orders_builder,
        redis_store,
        load_json,
        load,
        is_multioffer,
        has_setcar,
        has_cancelrequest,
        has_completerequest,
        code,
        message,
        metrics,
):
    await taxi_driver_orders_app_api.tests_control(reset_metrics=True)

    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}

    builder_setcar = json.loads(load('setcar.json'))
    driver_orders_builder.set_v2_setcar_resp(
        {'setcar': builder_setcar, 'setcar_push': {}},
    )

    rh.set_driver_status(redis_store, 'park_id', 'driver_profile_id', '2')

    if has_cancelrequest:
        rh.set_cancelrequested(
            redis_store, 'park_id', 'alias_id', 'driver_profile_id',
        )
    if has_completerequest:
        rh.set_completerequested(
            redis_store, 'park_id', 'alias_id', 'driver_profile_id',
        )
    if has_setcar:
        rh.set_setcared(
            redis_store, 'park_id', 'driver_profile_id', 'alias_id',
        )

    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/create',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'order_id': 'experiment_order_id',
                'driver': {
                    'park_id': 'park_id',
                    'driver_profile_id': 'driver_profile_id',
                    'alias_id': 'alias_id',
                },
                'is_multioffer': is_multioffer,
                'is_chain_order': False,
                'is_logistic_order': False,
                'is_reposition': False,
            },
        ),
    )

    http_error_metrics = await taxi_driver_orders_app_api_monitor.get_metric(
        'create_error_response_codes',
    )

    assert http_error_metrics == metrics

    assert response.status_code == code

    if message:
        assert response.json().get('message') == message


@pytest.mark.experiments3(filename='exp3_config_create_settings.json')
@pytest.mark.parametrize(
    'is_logistic_order,has_active_shift,matched,message,metrics',
    [
        (
            False,
            False,
            False,
            'driver_status_not_free check failed',
            {'driver_status_not_free': 1, 'start': 1},
        ),
        (
            True,
            False,
            False,
            'courier_no_active_shift check failed',
            {'courier_no_active_shift': 1, 'start': 1},
        ),
        (True, True, True, None, {'ok': 1, 'start': 1}),
    ],
    ids=[
        'non_logistic_order',
        'logistic_order_no_shift',
        'logistic_order_with_shift',
    ],
)
async def test_check_courier_no_active_shift(
        taxi_driver_orders_app_api,
        taxi_driver_orders_app_api_monitor,
        fleet_parks,
        driver_orders_builder,
        partner_api_proxy,
        redis_store,
        load_json,
        load,
        is_logistic_order,
        has_active_shift,
        matched,
        message,
        metrics,
):
    await taxi_driver_orders_app_api.tests_control(reset_metrics=True)

    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}

    builder_setcar = json.loads(load('setcar.json'))
    driver_orders_builder.set_v2_setcar_resp(
        {'setcar': builder_setcar, 'setcar_push': {}},
    )

    partner_api_proxy.set_response({'isActive': has_active_shift})

    rh.set_driver_status(redis_store, 'park_id', 'driver_profile_id', '1')

    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/create',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'order_id': 'order_id',
                'driver': {
                    'park_id': 'park_id',
                    'driver_profile_id': 'driver_profile_id',
                    'alias_id': 'alias_id',
                },
                'is_multioffer': False,
                'is_chain_order': False,
                'is_logistic_order': is_logistic_order,
                'is_reposition': False,
            },
        ),
    )

    assert driver_orders_builder.v2_setcar.times_called == int(matched)

    http_error_metrics = await taxi_driver_orders_app_api_monitor.get_metric(
        'create_error_response_codes',
    )

    assert http_error_metrics == metrics

    assert response.status_code == (200 if matched else 410)

    if message is not None:
        assert response.json().get('message') == message


@pytest.mark.experiments3(filename='exp3_config_create_settings.json')
@pytest.mark.parametrize(
    'is_multioffer,code,' 'message,metrics',
    [
        (False, 200, None, {'already_created': 1, 'start': 1}),
        (True, 200, None, {'ok': 1, 'start': 1}),
    ],
    ids=['already_created', 'already_created_multioffer'],
)
@pytest.mark.parametrize('taximeter_platform', ['ios', 'android'])
async def test_create_already_created(
        mockserver,
        taxi_driver_orders_app_api,
        taxi_driver_orders_app_api_monitor,
        fleet_parks,
        driver_orders_builder,
        redis_store,
        load_json,
        load,
        is_multioffer,
        code,
        message,
        metrics,
        stq,
        taxi_config,
        driver_profiles,
        taximeter_platform,
):
    await taxi_driver_orders_app_api.tests_control(reset_metrics=True)

    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}

    builder_setcar = json.loads(load('setcar.json'))
    driver_orders_builder.set_v2_setcar_resp(
        {'setcar': builder_setcar, 'setcar_push': {}},
    )

    rh.set_driver_status(redis_store, 'park_id', 'driver_profile_id', '2')

    rh.set_setcared(redis_store, 'park_id', 'driver_profile_id', 'alias_id')
    taxi_config.set_values(
        {
            'DRIVER_ORDERS_APP_API_SEND_COMMUNICATIONS_SETTINGS': {
                'send_force_polling_order_over_stq': True,
            },
        },
    )

    if taximeter_platform == 'ios':

        @mockserver.json_handler('/driver-orders-builder/v2/setcar_push')
        def _mock_setcar_data(request):
            return {'setcar_push': {'some_push': 'some_data'}}

    driver_profiles.set_platform(taximeter_platform)

    await taxi_driver_orders_app_api.invalidate_caches()

    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/create',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'order_id': 'experiment_order_id',
                'driver': {
                    'park_id': 'park_id',
                    'driver_profile_id': 'driver_profile_id',
                    'alias_id': 'alias_id',
                },
                'is_multioffer': is_multioffer,
                'is_chain_order': False,
                'is_logistic_order': False,
                'is_reposition': False,
            },
        ),
    )

    http_error_metrics = await taxi_driver_orders_app_api_monitor.get_metric(
        'create_error_response_codes',
    )

    assert http_error_metrics == metrics

    assert response.status_code == code

    if message:
        assert response.json().get('message') == message
    assert (
        stq.driver_orders_send_communications_notifications.times_called == 1
    )


@pytest.mark.experiments3(filename='exp3_config_create_settings.json')
@pytest.mark.parametrize(
    'driver_freightage, expected_flags',
    [
        pytest.param(True, r'{driver_freightage}', id='freightage_is_true'),
        pytest.param(False, None, id='freightage_is_false'),
        pytest.param(None, None, id='freightage_is_empty'),
    ],
)
async def test_create_order_with_freightage_flag(
        taxi_driver_orders_app_api,
        contractor_order_history,
        driver_profiles,
        fleet_parks,
        driver_orders_builder,
        redis_store,
        load_json,
        load,
        driver_freightage,
        expected_flags,
):
    await taxi_driver_orders_app_api.tests_control(reset_metrics=True)

    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}

    builder_setcar = json.loads(load('setcar.json'))
    if driver_freightage is not None:
        builder_setcar['internal'] = {'driver_freightage': driver_freightage}
    driver_orders_builder.set_v2_setcar_resp(
        {'setcar': builder_setcar, 'setcar_push': {}},
    )

    driver_profiles.set_platform('android')

    rh.set_driver_status(redis_store, 'park_id', 'driver_profile_id', '2')

    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/create',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'order_id': 'order_id',
                'driver': {
                    'park_id': 'park_id',
                    'driver_profile_id': 'driver_profile_id',
                    'alias_id': 'alias_id',
                },
                'is_multioffer': False,
                'is_chain_order': False,
                'is_logistic_order': False,
                'is_reposition': False,
            },
        ),
    )

    rh.check_order_setcar_items(redis_store, 'park_id', 'alias_id')

    rh.check_setcar_driver_reserv(
        redis_store, 'park_id', 'driver_profile_id', 'alias_id',
    )

    assert response.status_code == 200
    coh_request_args = await contractor_order_history.insert.wait_call()
    coh_request = coh_request_args['self'].json

    coh_fields = coh_request['order_fields']

    coh_flags = None
    for item in coh_fields:
        name = item['name']
        if name == 'flags':
            coh_flags = item['value']
            assert coh_flags == expected_flags
    assert coh_flags == expected_flags


@pytest.mark.experiments3(filename='exp3_config_create_settings.json')
@pytest.mark.parametrize('should_add_track', {True, False})
@pytest.mark.parametrize('cos_response_code', {429, 200})
async def test_create_order_geo_sharing(
        taxi_driver_orders_app_api,
        fleet_parks,
        driver_orders_builder,
        redis_store,
        load_json,
        load,
        mockserver,
        taxi_config,
        should_add_track,
        cos_response_code,
):
    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}

    builder_setcar = json.loads(load('setcar.json'))
    builder_setcar['client_geo_sharing'] = {'track_id': 'user_id'}
    if should_add_track:
        builder_setcar['client_geo_sharing']['is_enabled'] = True
    driver_orders_builder.set_v2_setcar_resp(
        {'setcar': builder_setcar, 'setcar_push': {}},
    )

    rh.set_driver_status(redis_store, 'park_id', 'driver_profile_id', '2')

    taxi_config.set_values({'TAXIMETER_USE_COS_FOR_GEO_SHARING': True})

    @mockserver.json_handler(
        '/contractor-order-setcar/v1/order/client-geo-sharing',
    )
    def _mock_cos_geo_sharing(request):
        expected_method = 'PUT'
        assert request.method == expected_method
        return mockserver.make_response(status=cos_response_code)

    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/create',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'order_id': 'experiment_order_id',
                'driver': {
                    'park_id': 'park_id',
                    'driver_profile_id': 'driver_profile_id',
                    'alias_id': 'alias_id',
                },
                'is_multioffer': False,
                'is_chain_order': False,
                'is_logistic_order': False,
                'is_reposition': False,
            },
        ),
    )

    assert response.status_code == 200
    assert _mock_cos_geo_sharing.times_called == should_add_track


@pytest.mark.experiments3(filename='exp3_config_create_settings.json')
async def test_create_order_contains_order_id(
        taxi_driver_orders_app_api,
        contractor_order_history,
        driver_profiles,
        fleet_parks,
        driver_orders_builder,
        redis_store,
        load_json,
        load,
):
    await taxi_driver_orders_app_api.tests_control(reset_metrics=True)

    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}

    builder_setcar = json.loads(load('setcar.json'))
    driver_orders_builder.set_v2_setcar_resp(
        {'setcar': builder_setcar, 'setcar_push': {}},
    )

    driver_profiles.set_platform('android')

    rh.set_driver_status(redis_store, 'park_id', 'driver_profile_id', '2')

    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/create',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'order_id': 'order_id',
                'driver': {
                    'park_id': 'park_id',
                    'driver_profile_id': 'driver_profile_id',
                    'alias_id': 'alias_id',
                },
                'is_multioffer': False,
                'is_chain_order': False,
                'is_logistic_order': False,
                'is_reposition': False,
            },
        ),
    )

    rh.check_order_setcar_items(redis_store, 'park_id', 'alias_id')

    rh.check_setcar_driver_reserv(
        redis_store, 'park_id', 'driver_profile_id', 'alias_id',
    )

    assert response.status_code == 200
    coh_request_args = await contractor_order_history.insert.wait_call()
    coh_request = coh_request_args['self'].json

    coh_fields = coh_request['order_fields']

    order_id = None
    for item in coh_fields:
        name = item['name']
        if name == 'order_id':
            order_id = item['value']
    assert order_id == 'e6db964483d0cf1288c21badca4c9ad7'
