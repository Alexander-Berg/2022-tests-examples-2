import pytest

DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


TEST_SIMPLE_JSON_PERFORMER_RESULT = {
    'car_id': 'car_id1',
    'car_model': 'some_car_model',
    'car_number': 'some_car_number',
    'driver_id': 'driver_id1',
    'is_deaf': False,
    'lookup_version': 1,
    'name': 'Kostya',
    'order_alias_id': '1234',
    'order_id': '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
    'park_clid': 'park_clid1',
    'park_id': 'park_id1',
    'park_name': 'some_park_name',
    'park_org_name': 'some_park_org_name',
    'phone_pd_id': 'phone_pd_id',
    'revision': 1,
    'tariff_class': 'cargo',
    'transport_type': 'electric_bicycle',
}


@pytest.fixture(name='exp3_order_cancel_performer_reason_workmode')
async def _exp3_order_cancel_performer_reason_workmode(
        experiments3, taxi_cargo_orders,
):
    async def call(default_use_new_flow=True, clauses=None):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_order_cancel_performer_reason_workmode',
            consumers=['cargo-orders/order-cancel-performer-reason-workmode'],
            clauses=clauses if clauses else [],
            default_value={'use_new_flow': default_use_new_flow},
        )
        await taxi_cargo_orders.invalidate_caches()

    return call


@pytest.fixture(name='exp3_performer_order_cancel_reasons')
async def _exp3_performer_order_cancel_reasons(
        experiments3, taxi_cargo_orders,
):
    async def call():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_performer_order_cancel_reasons',
            consumers=['cargo-claims/driver'],
            clauses=[],
            default_value={
                'reason_list': [
                    {
                        'reason_title_tanker_key': 'title',
                        'reason_subtitle_tanker_key': 'subtitle',
                        'id': 'reason',
                        'taxi_id': 'taxi_reason',
                        'use_blocked_restrictions': True,
                        'need_reorder': True,
                    },
                ],
            },
        )
        await taxi_cargo_orders.invalidate_caches()

    return call


@pytest.fixture(name='exp3_performer_order_cancel_determine_guilty')
async def _exp3_performer_order_cancel_determine_guilty(
        experiments3, taxi_cargo_orders,
):
    async def call(guilty=True):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_orders_performer_order_cancel_determine_guilty',
            consumers=['cargo-orders/performer-order-cancel'],
            clauses=[],
            default_value={
                'alert_title_tanker_key': 'performer_cancel_title',
                'alert_message_tanker_key': 'performer_cancel_message',
                'alert_message_tanker_args': {
                    'key1': 'value1',
                    'key2': 'value2',
                },
                'guilty': guilty,
            },
        )
        await taxi_cargo_orders.invalidate_caches()

    return call


@pytest.fixture(name='exp3_order_cancel_performer_reason_limits')
async def _exp3_order_cancel_performer_reason_limits(
        experiments3, taxi_cargo_orders,
):
    async def call(guilty=True):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_performer_fines_performer_cancellations_limits',
            consumers=['cargo-orders/performer-cancellations-limits'],
            clauses=[],
            default_value={
                'free_cancellation_limit': 1,
                'required_completed_orders_to_reset_cancellation_limit': 30,
                'title_tanker_key': 'performer_cancel_limit_title',
                'subtitle_tanker_key': 'performer_cancel_limit_subtitle',
                'detail_tanker_key': 'performer_cancel_limit_detail',
                'right_icon_payload': {
                    'text_tanker_key': 'performer_cancel_limit_right_icon',
                },
            },
        )
        await taxi_cargo_orders.invalidate_caches()

    return call


async def test_order_cancel_performer_reason(
        taxi_cargo_orders,
        default_order_id,
        exp3_performer_order_cancel_reasons,
        exp3_order_cancel_performer_reason_workmode,
):
    await exp3_performer_order_cancel_reasons()
    await exp3_order_cancel_performer_reason_workmode(False)
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'cancel_reason_id': 'reason',
            'dispatch_version': 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'cancel_reason_id': 'reason',
        'taxi_cancel_reason_id': 'taxi_reason',
        'use_blocked_restrictions': True,
    }


@pytest.mark.parametrize('use_new_flow', [True, False])
@pytest.mark.parametrize(
    'bad_header', ['X-YaTaxi-Driver-Profile-Id', 'X-YaTaxi-Park-Id'],
)
async def test_no_auth(
        taxi_cargo_orders,
        exp3_performer_order_cancel_reasons,
        exp3_order_cancel_performer_reason_workmode,
        default_order_id,
        use_new_flow,
        bad_header: str,
):
    await exp3_order_cancel_performer_reason_workmode(use_new_flow)
    await exp3_performer_order_cancel_reasons()
    headers_bad_driver = DEFAULT_HEADERS.copy()
    headers_bad_driver[bad_header] = 'bad'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
        headers=headers_bad_driver,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'cancel_reason_id': 'reason',
            'point_id': 123123,
        },
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': 'not_authorized',
        'message': 'Попробуйте снова',
    }


@pytest.mark.parametrize(
    'clauses',
    [
        [
            {
                'title': 'по корпам',
                'value': {'use_new_flow': True},
                'enabled': True,
                'is_signal': False,
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'set': [
                                        '5e36732e2bc54e088b1466e08e31c486',
                                    ],
                                    'arg_name': 'corp_client_id',
                                    'set_elem_type': 'string',
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'value': (
                                        'cargo_order_cancel_performer_reason'
                                    ),
                                    'arg_name': 'driver_features_custom_set',
                                    'set_elem_type': 'string',
                                },
                                'type': 'contains',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'is_tech_group': False,
                'extension_method': 'replace',
                'is_paired_signal': False,
            },
        ],
        [],
    ],
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'cargo_order_cancel_performer_reason': '9.00'},
        },
    },
)
@pytest.mark.now('2020-08-18T13:57:49.939497+00:00')
async def test_new_flow_perf_cancel_workmode(
        taxi_cargo_orders,
        mockserver,
        exp3_performer_order_cancel_reasons,
        exp3_performer_order_cancel_determine_guilty,
        exp3_order_cancel_performer_reason_workmode,
        exp3_order_cancel_performer_reason_limits,
        testpoint,
        default_order_id,
        query_performer_order_cancel,
        clauses,
):
    await exp3_performer_order_cancel_reasons()
    await exp3_performer_order_cancel_determine_guilty()
    await exp3_order_cancel_performer_reason_workmode(
        default_use_new_flow=False, clauses=clauses,
    )
    await exp3_order_cancel_performer_reason_limits()

    @testpoint('time_info')
    def time_info(data):
        assert data == {'weekday': 'tuesday', 'hh': 16, 'mm': 57}

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _driver_tags(request):
        assert request.json == {'dbid': 'park_id1', 'uuid': 'driver_id1'}
        return {'tags': ['test_tag_1']}

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'cancel_reason_id': 'reason',
        },
    )

    assert response.status_code == 200

    if clauses:
        assert response.json() == {
            'cancel_reason_id': 'reason',
            'taxi_cancel_reason_id': 'taxi_reason',
            'use_blocked_restrictions': True,
            'first_call_info': {
                'alert_title': 'Заголовок',
                'alert_message': 'текст отмены value1, value2',
                'request_id': 1,
            },
        }

        result = query_performer_order_cancel(id_=1)[0]
        assert not result.completed
        assert result.guilty
        assert result.need_reorder
        assert not result.free_cancellations_limit_exceeded

        response = await taxi_cargo_orders.post(
            '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
            headers=DEFAULT_HEADERS,
            json={
                'cargo_ref_id': 'order/' + default_order_id,
                'request_id': 1,
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            'cancel_reason_id': 'reason',
            'taxi_cancel_reason_id': 'taxi_reason',
            'use_blocked_restrictions': False,
        }

        result = query_performer_order_cancel(id_=1)[0]
        assert result.completed
        assert result.guilty
        assert result.need_reorder
        assert not result.free_cancellations_limit_exceeded
        assert result.payload == {
            'tags': ['test_tag_1'],
            'waybill_ref': 'waybill-ref',
            'time_in_status_sec': 60,
            'special_requirements': ['cargo_eds'],
            'claim_status': 'pickuped',
            'items_weight': 15.0,
        }

        assert time_info.times_called == 1
    else:
        assert response.json() == {
            'cancel_reason_id': 'reason',
            'taxi_cancel_reason_id': 'taxi_reason',
            'use_blocked_restrictions': True,
        }


@pytest.mark.parametrize(
    'clauses',
    [
        [
            {
                'title': 'c2c',
                'value': {'use_new_flow': True},
                'enabled': True,
                'is_signal': False,
                'predicate': {
                    'init': {
                        'predicates': [
                            {'init': {'arg_name': 'is_c2c'}, 'type': 'bool'},
                            {
                                'init': {
                                    'value': (
                                        'cargo_order_cancel_performer_reason'
                                    ),
                                    'arg_name': 'driver_features_custom_set',
                                    'set_elem_type': 'string',
                                },
                                'type': 'contains',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'is_tech_group': False,
                'extension_method': 'replace',
                'is_paired_signal': False,
            },
        ],
        [],
    ],
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'cargo_order_cancel_performer_reason': '9.00'},
        },
    },
)
@pytest.mark.now('2020-08-18T13:57:49.939497+00:00')
async def test_new_flow_order_cancel_performer_reason_c2c_enabled(
        taxi_cargo_orders,
        taxi_config,
        mockserver,
        exp3_performer_order_cancel_reasons,
        exp3_performer_order_cancel_determine_guilty,
        exp3_order_cancel_performer_reason_workmode,
        exp3_order_cancel_performer_reason_limits,
        my_waybill_info,
        default_order_id,
        query_performer_order_cancel,
        clauses,
):
    await exp3_performer_order_cancel_reasons()
    await exp3_performer_order_cancel_determine_guilty()
    await exp3_order_cancel_performer_reason_workmode(
        default_use_new_flow=False, clauses=clauses,
    )
    await exp3_order_cancel_performer_reason_limits()

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        for segment in my_waybill_info['execution']['segments']:
            segment['cargo_c2c_order_id'] = 'c2c_id'
        return mockserver.make_response(status=200, json=my_waybill_info)

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _driver_tags(request):
        assert request.json == {'dbid': 'park_id1', 'uuid': 'driver_id1'}
        return {'tags': ['test_tag_1']}

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'cancel_reason_id': 'reason',
        },
    )
    assert response.status_code == 200

    if clauses:
        assert response.json() == {
            'cancel_reason_id': 'reason',
            'taxi_cancel_reason_id': 'taxi_reason',
            'use_blocked_restrictions': True,
            'first_call_info': {
                'alert_title': 'Заголовок',
                'alert_message': 'текст отмены value1, value2',
                'request_id': 1,
            },
        }

        result = query_performer_order_cancel(id_=1)[0]
        assert not result.completed
        assert result.guilty
        assert result.need_reorder
        assert not result.free_cancellations_limit_exceeded

        response = await taxi_cargo_orders.post(
            '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
            headers=DEFAULT_HEADERS,
            json={
                'cargo_ref_id': 'order/' + default_order_id,
                'request_id': 1,
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            'cancel_reason_id': 'reason',
            'taxi_cancel_reason_id': 'taxi_reason',
            'use_blocked_restrictions': False,
        }

        result = query_performer_order_cancel(id_=1)[0]
        assert result.completed
        assert result.guilty
        assert result.need_reorder
        assert not result.free_cancellations_limit_exceeded
        assert result.payload == {
            'tags': ['test_tag_1'],
            'waybill_ref': 'waybill-ref',
            'time_in_status_sec': 60,
            'special_requirements': ['cargo_eds'],
            'claim_status': 'pickuped',
            'items_weight': 15.0,
        }
    else:
        assert response.json() == {
            'cancel_reason_id': 'reason',
            'taxi_cancel_reason_id': 'taxi_reason',
            'use_blocked_restrictions': True,
        }


@pytest.mark.parametrize('second_cancel_guilty', [True])
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'cargo_order_cancel_performer_reason': '9.00'},
        },
    },
)
@pytest.mark.now('2020-08-18T13:57:49.939497+00:00')
async def test_new_flow_check_statistics(
        taxi_cargo_orders,
        mockserver,
        exp3_performer_order_cancel_reasons,
        exp3_performer_order_cancel_determine_guilty,
        exp3_order_cancel_performer_reason_workmode,
        exp3_order_cancel_performer_reason_limits,
        query_performer_order_cancel,
        default_order_id,
        query_performer_order_cancel_statistics,
        second_cancel_guilty,
):
    await exp3_performer_order_cancel_reasons()
    await exp3_performer_order_cancel_determine_guilty()
    await exp3_order_cancel_performer_reason_workmode(
        default_use_new_flow=True,
    )
    await exp3_order_cancel_performer_reason_limits()

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _driver_tags(request):
        assert request.json == {'dbid': 'park_id1', 'uuid': 'driver_id1'}
        return {'tags': ['test_tag_1']}

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'cancel_reason_id': 'reason',
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id, 'request_id': 1},
    )
    assert response.status_code == 200

    result = query_performer_order_cancel_statistics(
        dbid_uuid_='park_id1_driver_id1',
    )[0]
    assert result.dbid_uuid == 'park_id1_driver_id1'
    assert result.completed_orders == 0
    assert result.cancellation_count == 1

    result = query_performer_order_cancel(id_=1)[0]
    assert not result.free_cancellations_limit_exceeded

    await exp3_performer_order_cancel_determine_guilty(
        guilty=second_cancel_guilty,
    )

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'cancel_reason_id': 'reason',
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id, 'request_id': 2},
    )
    assert response.status_code == 200

    result = query_performer_order_cancel_statistics(
        dbid_uuid_='park_id1_driver_id1',
    )[0]
    assert result.dbid_uuid == 'park_id1_driver_id1'
    assert result.completed_orders == 0
    assert result.cancellation_count == 2 if second_cancel_guilty else 1

    result = query_performer_order_cancel(id_=2)[0]
    assert (
        result.free_cancellations_limit_exceeded
        if second_cancel_guilty
        else not result.free_cancellations_limit_exceeded
    )


async def test_cargo_performer_fines_flow(
        taxi_cargo_orders,
        mockserver,
        exp3_performer_order_cancel_reasons,
        exp_cargo_orders_use_performer_fines_service,
        exp3_order_cancel_performer_reason_workmode,
        query_performer_order_cancel,
        default_order_id,
        query_performer_order_cancel_statistics,
        waybill_state,
):
    await exp3_performer_order_cancel_reasons()
    await exp3_order_cancel_performer_reason_workmode(
        default_use_new_flow=True,
    )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _driver_tags(request):
        assert request.json == {'dbid': 'park_id1', 'uuid': 'driver_id1'}
        return {'tags': ['test_tag_1']}

    @mockserver.json_handler(
        '/cargo-performer-fines/performer/cancel/determine-guilty',
    )
    def _performer_fines(request):
        assert request.json == {
            'cancel_reason_id': 'reason',
            'taxi_order_id': 'taxi-order',
            'cancel_request_id': 1,
            'waybill_info': waybill_state.waybills['waybill-ref'],
            'performer': TEST_SIMPLE_JSON_PERFORMER_RESULT,
        }
        return {
            'alert_for_performer': {
                'alert_title': 'title',
                'alert_message': 'message',
            },
        }

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'cancel_reason_id': 'reason',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'cancel_reason_id': 'reason',
        'first_call_info': {
            'alert_message': 'message',
            'alert_title': 'title',
            'request_id': 1,
        },
        'taxi_cancel_reason_id': 'taxi_reason',
        'use_blocked_restrictions': True,
    }

    result = query_performer_order_cancel(id_=1)[0]
    assert not result.guilty

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/order-cancel-performer-reason',
        headers=DEFAULT_HEADERS,
        json={'cargo_ref_id': 'order/' + default_order_id, 'request_id': 1},
    )
    assert response.status_code == 200
    result = query_performer_order_cancel(id_=1)[0]
    assert result.completed
