import datetime

import pytest


JOB_NAME = 'cargo-claims-points-ready-monitor'

TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

TRYOUT_PAID_CANCEL = {
    'reason': 'point_is_ready',
    'paid_cancel_max_waiting_time': 999999,
}

OTHER_PAID_CANCEL = {'reason': 'disabled_experiment'}


@pytest.fixture(name='mock_client_notify')
async def _mock_client_notify(mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def v2_push(request):
        return {'notification_id': 'some-magic-id'}

    return v2_push


@pytest.fixture(name='notify_driver')
async def _notify_driver(mockserver, stq_runner):
    async def _wrapper(
            *,
            limited_paid_waiting: bool = None,
            locale: str = None,
            ready_ts=None,
            order_id: str = None,
            expect_communications=True,
            flags: str = None,
    ):
        @mockserver.json_handler('/client-notify/v2/push')
        def mock_client_notify(request):
            if flags:
                assert request.json['data']['flags'] == [flags]
            return {'notification_id': 'some-magic-id'}

        args = [
            1000,
            'park02e56c2740d9a536650f5390de0b',
            'drivere56c2740d9a536650f5390de0b',
            'corp02e56c2740d9a536650f5390de0b',
            limited_paid_waiting,
            locale,
            ready_ts,
            order_id,
        ]

        await stq_runner.cargo_claims_point_ready_notify.call(
            task_id='testsuite-point-ready-notify-stq',
            args=args,
            expect_fail=False,
        )

        if expect_communications:
            assert mock_client_notify.times_called == 1
        else:
            assert mock_client_notify.times_called == 0

    return _wrapper


@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_claims_set_points_ready',
    consumers=['cargo-claims/set-points-ready'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='limit_paid_waiting_point_ready',
    consumers=['cargo-claims/accept'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_point_ready_notification_settings',
    consumers=['cargo-claims/point_ready_notify'],
    is_config=True,
    clauses=[],
    default_value={
        'enabled': True,
        'base_requirements': {
            'keyset': 'keyset',
            'message_tanker_key': 'no_key',
            'action_tanker_key': 'no_key',
        },
        'full_requirements': {
            'limited_waiting_keyset': 'cargo',
            'limited_waiting_tanker_key': 'no_key',
        },
    },
)
@pytest.mark.parametrize('points_ready_count', [0, 1])
@pytest.mark.parametrize(
    'workmode, expected_paid_cancel_result',
    [
        ('oldway', OTHER_PAID_CANCEL),
        ('dryrun', OTHER_PAID_CANCEL),
        ('tryout', TRYOUT_PAID_CANCEL),
    ],
)
@pytest.mark.config(CARGO_CLAIMS_POINTS_READY_MONITOR_ENABLED=True)
@pytest.mark.config(
    CARGO_CLAIMS_POINT_READY_AMNESTY_TIME={'amnesty-time-ms': 1},
)
async def test_points_ready_for_interact_basic(
        pgsql,
        taxi_cargo_claims,
        get_default_headers,
        state_controller,
        run_task_once,
        taxi_config,
        stq,
        notify_driver,
        points_ready_count,
        workmode,
        expected_paid_cancel_result,
):
    taxi_config.set_values(
        dict(CARGO_CLAIMS_LIMITED_PAID_WAITING_WORKMODE=workmode),
    )

    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')
    if points_ready_count:
        response = await taxi_cargo_claims.post(
            '/api/integration/v1/claims/set-points-ready',
            params={'claim_id': claim_info.claim_id},
            headers=get_default_headers('01234567890123456789012345678912'),
            json={},
        )
        assert response.status_code == 200

    await run_task_once(JOB_NAME)

    queue = stq.cargo_claims_point_ready_notify
    assert queue.times_called == points_ready_count

    if points_ready_count:
        await notify_driver()

    if points_ready_count:
        response = await taxi_cargo_claims.post(
            f'/v1/claims/paid-cancel',
            params={'claim_id': claim_info.claim_id},
            headers={'X-B2B-Client-Id': '01234567890123456789012345678912'},
        )
        assert response.status_code == 200
        assert response.json() == expected_paid_cancel_result


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_point_ready_notification_settings',
    consumers=['cargo-claims/point_ready_notify'],
    is_config=True,
    clauses=[],
    default_value={
        'enabled': True,
        'base_requirements': {
            'keyset': 'keyset',
            'message_tanker_key': 'no_key',
            'action_tanker_key': 'no_key',
        },
    },
)
async def test_uncomplete_args_stq(mockserver, stq_runner, mock_client_notify):
    args = [
        1000,
        'park02e56c2740d9a536650f5390de0b',
        'drivere56c2740d9a536650f5390de0b',
        'corp02e56c2740d9a536650f5390de0b',
    ]

    await stq_runner.cargo_claims_point_ready_notify.call(
        task_id='testsuite-point-ready-notify-stq',
        args=args,
        expect_fail=False,
    )
    assert mock_client_notify.times_called == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_point_ready_notification_settings',
    consumers=['cargo-claims/point_ready_notify'],
    is_config=True,
    clauses=[],
    default_value={
        'enabled': True,
        'base_requirements': {
            'keyset': 'keyset',
            'message_tanker_key': 'no_key',
            'action_tanker_key': 'no_key',
        },
        'full_requirements': {
            'limited_waiting_keyset': 'cargo',
            'limited_waiting_tanker_key': 'no_key',
        },
    },
)
@pytest.mark.parametrize(
    (
        'limited_paid_waiting, communicaiton_calls,'
        'updaterequest_calls, driver_chat_calls,'
        'update_setcar_calls'
    ),
    [(True, 0, 1, 1, 0), (False, 1, 0, 0, 1)],
)
@pytest.mark.translations(cargo={'no_key': {'ru': 'some_text'}})
async def test_point_ready_notify_stq(
        stq,
        prepare_state,
        stq_runner,
        mockserver,
        limited_paid_waiting,
        communicaiton_calls,
        updaterequest_calls,
        driver_chat_calls,
        update_setcar_calls,
        mock_client_notify,
):
    @mockserver.json_handler('/driver-protocol/service/chat/add')
    def mock_driver_protocol(request):
        return {}

    @mockserver.json_handler('/driver-orders-builder/v1/setcar/update-lite')
    def mock_dob(request):
        return {
            'paid_waiting': {
                'end': {
                    'date': '2020-06-26T08:28:00.000000Z',
                    'reason': 'cargo_ready',
                },
            },
        }

    if update_setcar_calls:
        await prepare_state(visit_order=1)

    now = datetime.datetime.now()
    await stq_runner.cargo_claims_point_ready_notify.call(
        task_id='testsuite-point-ready-notify-stq',
        args=[
            1000,
            'park02e56c2740d9a536650f5390de0b',
            'drivere56c2740d9a536650f5390de0b',
            'corp02e56c2740d9a536650f5390de0b',
            limited_paid_waiting,
            'ru',
            now,
            'order2e56c2740d9a536650f5390de0b',
        ],
        expect_fail=False,
    )

    assert mock_client_notify.times_called == communicaiton_calls
    assert mock_driver_protocol.times_called == driver_chat_calls
    assert mock_dob.times_called == updaterequest_calls
    assert (
        stq.cargo_update_setcar_state_version.times_called
        == update_setcar_calls
    )


@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_claims_set_points_ready',
    consumers=['cargo-claims/set-points-ready'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='limit_paid_waiting_point_ready',
    consumers=['cargo-claims/accept'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_point_ready_notification_settings',
    consumers=['cargo-claims/point_ready_notify'],
    is_config=True,
    clauses=[],
    default_value={
        'enabled': True,
        'base_requirements': {
            'keyset': 'keyset',
            'message_tanker_key': 'no_key',
            'action_tanker_key': 'no_key',
        },
        'full_requirements': {
            'limited_waiting_keyset': 'cargo',
            'limited_waiting_tanker_key': 'no_key',
        },
    },
)
@pytest.mark.config(
    CARGO_CLAIMS_POINTS_READY_MONITOR_ENABLED=True,
    CARGO_CLAIMS_POINT_READY_AMNESTY_TIME={'amnesty-time-ms': 1},
    CARGO_CLAIMS_LIMITED_PAID_WAITING_WORKMODE='tryout',
)
async def test_dragon_order(
        pgsql,
        taxi_cargo_claims,
        get_default_headers,
        state_controller,
        run_task_once,
        get_db_segment_ids,
        taxi_config,
        stq,
        notify_driver,
        create_segment_with_performer,
):
    segment = await create_segment_with_performer()

    response = await taxi_cargo_claims.post(
        '/api/integration/v1/claims/set-points-ready',
        params={'claim_id': segment.claim_id},
        headers=get_default_headers('01234567890123456789012345678912'),
        json={},
    )
    assert response.status_code == 200

    await run_task_once(JOB_NAME)

    assert stq.cargo_claims_point_ready_notify.times_called == 1

    await notify_driver()

    response = await taxi_cargo_claims.post(
        f'/v1/claims/paid-cancel',
        params={'claim_id': f'order/{segment.cargo_order_id}'},
        headers={'X-B2B-Client-Id': '01234567890123456789012345678912'},
    )
    assert response.status_code == 200
    assert response.json() == TRYOUT_PAID_CANCEL

    segment_ids = await get_db_segment_ids()
    response = await taxi_cargo_claims.post(
        '/v1/segments/bulk-info',
        json={'segment_ids': [{'segment_id': segment_ids[0]}]},
    )
    assert response.status_code == 200
    assert len(response.json()['segments']) == 1
    first_point = response.json()['segments'][0]['points'][0]
    assert first_point['was_ready_at']


@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_claims_set_points_ready',
    consumers=['cargo-claims/set-points-ready'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='limit_paid_waiting_point_ready',
    consumers=['cargo-claims/accept'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_point_ready_notification_settings',
    consumers=['cargo-claims/point_ready_notify'],
    is_config=True,
    clauses=[
        {
            'title': 'clause',
            'predicate': {
                'init': {
                    'arg_name': 'tariff_class',
                    'set': ['eda', 'lavka'],
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {
                'enabled': True,
                'base_requirements': {
                    'keyset': 'keyset',
                    'message_tanker_key': 'no_key',
                    'action_tanker_key': 'no_key',
                },
                'full_requirements': {
                    'limited_waiting_keyset': 'cargo',
                    'limited_waiting_tanker_key': 'no_key1',
                },
            },
        },
    ],
    default_value={
        'enabled': True,
        'base_requirements': {
            'keyset': 'keyset',
            'message_tanker_key': 'no_key',
            'action_tanker_key': 'no_key',
        },
        'full_requirements': {
            'limited_waiting_keyset': 'cargo',
            'limited_waiting_tanker_key': 'no_key',
        },
    },
)
@pytest.mark.config(
    CARGO_CLAIMS_POINTS_READY_MONITOR_ENABLED=True,
    CARGO_CLAIMS_POINT_READY_AMNESTY_TIME={'amnesty-time-ms': 1},
    CARGO_CLAIMS_LIMITED_PAID_WAITING_WORKMODE='tryout',
)
@pytest.mark.translations(
    cargo={'no_key': {'ru': 'some_text'}, 'no_key1': {'ru': 'some_text1'}},
)
@pytest.mark.parametrize(
    'tariff_class, message',
    [('eda', 'some_text1'), ('lavka', 'some_text1'), ('courier', 'some_text')],
)
async def test_custom_message_for_tariff(
        mockserver,
        taxi_cargo_claims,
        get_default_headers,
        run_task_once,
        stq,
        notify_driver,
        create_segment_with_performer,
        tariff_class: str,
        message: str,
):
    """
        Check no message send for courier of 'eda', 'lavka' classes.
    """

    @mockserver.json_handler('/driver-orders-builder/v1/setcar/update-lite')
    def _mock_dob(request):
        return {
            'paid_waiting': {
                'end': {
                    'date': '2020-06-26T08:28:00.000000Z',
                    'reason': 'cargo_ready',
                },
            },
        }

    @mockserver.json_handler('/driver-protocol/service/chat/add')
    def mock_driver_protocol(request):
        assert request.json['msg'] == message
        return {}

    segment = await create_segment_with_performer(taxi_class=tariff_class)

    response = await taxi_cargo_claims.post(
        '/api/integration/v1/claims/set-points-ready',
        params={'claim_id': segment.claim_id},
        headers=get_default_headers('01234567890123456789012345678912'),
        json={},
    )
    assert response.status_code == 200

    await run_task_once(JOB_NAME)

    assert stq.cargo_claims_point_ready_notify.times_called == 1

    await notify_driver(
        limited_paid_waiting=True,
        locale='ru',
        ready_ts=datetime.datetime.now(),
        order_id='order2e56c2740d9a536650f5390de0b',
        expect_communications=False,
    )

    assert mock_driver_protocol.times_called == 1


@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_claims_set_points_ready',
    consumers=['cargo-claims/set-points-ready'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='limit_paid_waiting_point_ready',
    consumers=['cargo-claims/accept'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_point_ready_notification_settings',
    consumers=['cargo-claims/point_ready_notify'],
    is_config=True,
    clauses=[],
    default_value={
        'enabled': True,
        'base_requirements': {
            'keyset': 'keyset',
            'message_tanker_key': 'no_key',
            'action_tanker_key': 'no_key',
            'use_priority_push': True,
        },
        'full_requirements': {
            'limited_waiting_keyset': 'cargo',
            'limited_waiting_tanker_key': 'no_key',
            'use_priority_push': True,
        },
    },
)
@pytest.mark.config(CARGO_CLAIMS_POINTS_READY_MONITOR_ENABLED=True)
@pytest.mark.config(
    CARGO_CLAIMS_POINT_READY_AMNESTY_TIME={'amnesty-time-ms': 1},
    CARGO_CLAIMS_LIMITED_PAID_WAITING_WORKMODE='tryout',
)
async def test_points_ready_for_interact_high_priority(
        pgsql,
        taxi_cargo_claims,
        get_default_headers,
        state_controller,
        run_task_once,
        taxi_config,
        stq,
        notify_driver,
):

    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')

    response = await taxi_cargo_claims.post(
        '/api/integration/v1/claims/set-points-ready',
        params={'claim_id': claim_info.claim_id},
        headers=get_default_headers('01234567890123456789012345678912'),
        json={},
    )
    assert response.status_code == 200

    await run_task_once(JOB_NAME)

    queue = stq.cargo_claims_point_ready_notify
    assert queue.times_called == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_point_ready_notification_settings',
    consumers=['cargo-claims/point_ready_notify'],
    is_config=True,
    clauses=[],
    default_value={
        'enabled': True,
        'base_requirements': {
            'keyset': 'keyset',
            'message_tanker_key': 'no_key',
            'action_tanker_key': 'no_key',
        },
        'full_requirements': {
            'limited_waiting_keyset': 'cargo',
            'limited_waiting_tanker_key': 'no_key',
        },
    },
)
async def test_stq_point_ready_notify_timeout_error(
        stq, stq_runner, mockserver, prepare_state,
):
    @mockserver.json_handler('/driver-orders-builder/v1/setcar/update-lite')
    def mock_dob_timeout(request):
        raise mockserver.TimeoutError()

    await prepare_state(visit_order=1)
    now = datetime.datetime.now()
    await stq_runner.cargo_claims_point_ready_notify.call(
        task_id='testsuite-point-ready-notify-stq',
        args=[
            1000,
            'park02e56c2740d9a536650f5390de0b',
            'drivere56c2740d9a536650f5390de0b',
            'corp02e56c2740d9a536650f5390de0b',
            True,
            'ru',
            now,
            'order2e56c2740d9a536650f5390de0b',
        ],
        expect_fail=True,
    )

    assert mock_dob_timeout.times_called
    assert stq.cargo_update_setcar_state_version.times_called == 0


@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_claims_set_points_ready',
    consumers=['cargo-claims/set-points-ready'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_point_ready_notification_settings',
    consumers=['cargo-claims/point_ready_notify'],
    is_config=True,
    clauses=[],
    default_value={
        'enabled': True,
        'base_requirements': {
            'keyset': 'keyset',
            'message_tanker_key': 'no_key',
            'action_tanker_key': 'no_key',
        },
        'full_requirements': {
            'limited_waiting_keyset': 'cargo',
            'limited_waiting_tanker_key': 'no_key',
        },
    },
)
@pytest.mark.config(
    CARGO_CLAIMS_POINTS_READY_MONITOR_ENABLED=True,
    CARGO_CLAIMS_POINT_READY_AMNESTY_TIME={'amnesty-time-ms': 1},
    CARGO_CLAIMS_LIMITED_PAID_WAITING_WORKMODE='tryout',
)
@pytest.mark.parametrize(
    'tariff_class, order_flow_type',
    [('eda', 'native'), ('lavka', 'retail'), ('courier', 'native')],
)
@pytest.mark.parametrize(
    'status_filter_default, status_filter_clauses',
    [
        (
            False,
            [
                {
                    'title': 'title',
                    'predicate': {
                        'type': 'eq',
                        'init': {
                            'value': 'order_ready',
                            'arg_name': 'claim_status',
                            'arg_type': 'string',
                        },
                    },
                    'value': {'enabled': True},
                },
            ],
        ),
    ],
)
async def test_order_ready_notify(
        pgsql,
        taxi_cargo_claims,
        get_default_headers,
        state_controller,
        run_task_once,
        get_db_segment_ids,
        taxi_config,
        stq,
        notify_driver,
        create_segment_with_performer,
        query_processing_events,
        procaas_event_kind_filter,
        tariff_class,
        order_flow_type,
        procaas_claim_status_filter,
        status_filter_default,
        status_filter_clauses,
):
    await procaas_event_kind_filter()
    await procaas_claim_status_filter(
        enabled=status_filter_default, clauses=status_filter_clauses,
    )

    segment = await create_segment_with_performer(
        taxi_class=tariff_class,
        custom_context={'order_flow_type': order_flow_type},
    )
    response = await taxi_cargo_claims.post(
        '/api/integration/v1/claims/set-points-ready',
        params={'claim_id': segment.claim_id},
        headers=get_default_headers('01234567890123456789012345678912'),
        json={},
    )
    assert response.status_code == 200

    await run_task_once(JOB_NAME)
    assert stq.cargo_claims_point_ready_notify.times_called == 1
    await notify_driver()

    events = query_processing_events(segment.claim_id)
    assert len(events) == 1

    payload = events[0].payload
    assert payload['data']['was_ready_at']
    del payload['data']['was_ready_at']

    assert payload == {
        'kind': 'status-change-succeeded',
        'status': 'order_ready',
        'data': {
            'park_id': 'park_id1',
            'zone_id': 'moscow',
            'phoenix_claim': False,
            'current_point_id': 1000,
            'is_terminal': False,
            'cargo_order_id': '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
            'corp_client_id': '01234567890123456789012345678912',
            'driver_profile_id': 'driver_id1',
            'tariff_class': tariff_class,
            'custom_context': {'order_flow_type': order_flow_type},
        },
    }
