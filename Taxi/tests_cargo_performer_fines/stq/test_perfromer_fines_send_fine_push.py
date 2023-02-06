import datetime

import pytest


async def test_happy_path(
        mock_fines_state,
        default_dbid_uuid,
        default_taxi_order_id,
        default_operation_id,
        default_fine_code,
        exp3_driver_simple_push_settings,
        setup_order_fines_codes,
        stq_runner,
        mockserver,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    mock_fines_state(
        park_id=park_id, driver_id=driver_id, fine_code=default_fine_code,
    )

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert request.json == {
            'service': 'taximeter',
            'intent': 'PersonalOffer',
            'notification': {
                'text': {
                    'key': (
                        'cargo_performer_fines.'
                        'driver_pushes.assigned_default_fine'
                    ),
                    'keyset': 'notify',
                },
            },
            'data': {},
            'client_id': f'{park_id}-{driver_id}',
        }
        assert request.headers['X-Idempotency-Token'] == default_operation_id
        return {'notification_id': 'notification-id'}

    await stq_runner.cargo_performer_fines_send_fine_push.call(
        task_id='test_push',
        kwargs={
            'taxi_order_id': default_taxi_order_id,
            'driver_uuid': driver_id,
            'park_id': park_id,
            'operation_id': default_operation_id,
        },
    )

    assert mock_client_notify.times_called == 1


@pytest.mark.parametrize(
    'ignore_any_push, communications_push', [(True, False), (False, True)],
)
async def test_ignore_any_push(
        taxi_cargo_performer_fines,
        mock_fines_state,
        default_dbid_uuid,
        default_taxi_order_id,
        default_operation_id,
        default_fine_code,
        exp3_driver_simple_push_settings,
        setup_order_fines_codes,
        stq_runner,
        mockserver,
        experiments3,
        ignore_any_push,
        communications_push,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_performer_fines_driver_push_settings',
        consumers=['cargo-performer-fines/decision'],
        clauses=[],
        default_value={
            'ignore_any_push': ignore_any_push,
            'enable_custom_push': False,
            'delay_after_decision_resolved': 0,
        },
    )
    await taxi_cargo_performer_fines.invalidate_caches()

    mock_fines_state(
        park_id=park_id, driver_id=driver_id, fine_code=default_fine_code,
    )

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert request.json == {
            'service': 'taximeter',
            'intent': 'PersonalOffer',
            'notification': {
                'text': {
                    'key': (
                        'cargo_performer_fines.'
                        'driver_pushes.assigned_default_fine'
                    ),
                    'keyset': 'notify',
                },
            },
            'data': {},
            'client_id': f'{park_id}-{driver_id}',
        }
        assert request.headers['X-Idempotency-Token'] == default_operation_id
        return {'notification_id': 'notification-id'}

    await stq_runner.cargo_performer_fines_send_fine_push.call(
        task_id='test_push',
        kwargs={
            'taxi_order_id': default_taxi_order_id,
            'driver_uuid': driver_id,
            'park_id': park_id,
            'operation_id': default_operation_id,
        },
    )

    if communications_push:
        assert mock_client_notify.times_called == 1
    else:
        assert mock_client_notify.times_called == 0


@pytest.mark.parametrize(
    'delay_after_decision_resolved, communications_push, reschedule',
    [(60, True, False), (3600, False, True)],
)
@pytest.mark.now('2020-02-25T06:12:00+03:00')
async def test_custom_push(
        taxi_cargo_performer_fines,
        mock_fines_state,
        stq,
        default_dbid_uuid,
        default_taxi_order_id,
        default_operation_id,
        default_taxi_alias_id,
        default_fine_code,
        exp3_driver_simple_push_settings,
        setup_order_fines_codes,
        stq_runner,
        mockserver,
        experiments3,
        delay_after_decision_resolved,
        communications_push,
        reschedule,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='cargo_performer_fines_driver_push_settings',
        consumers=['cargo-performer-fines/decision'],
        clauses=[],
        default_value={
            'ignore_any_push': False,
            'enable_custom_push': True,
            'delay_after_decision_resolved': delay_after_decision_resolved,
        },
    )
    await taxi_cargo_performer_fines.invalidate_caches()

    mock_fines_state(
        park_id=park_id, driver_id=driver_id, fine_code=default_fine_code,
    )

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert request.json == {
            'service': 'taximeter',
            'intent': 'FineUpdate',
            'collapse_key': 'FineUpdate',
            'notification': {
                'text': {
                    'key': (
                        'cargo_performer_fines.'
                        'driver_pushes.assigned_default_fine'
                    ),
                    'keyset': 'notify',
                },
            },
            'data': {
                'fine_identity': {'taxi_alias_id': default_taxi_alias_id},
                'button_label': {
                    'key': (
                        'order_fines.driver_pushes.custom_push.button_label'
                    ),
                    'keyset': 'notify',
                },
            },
            'client_id': f'{park_id}-{driver_id}',
        }
        assert request.headers['X-Idempotency-Token'] == default_operation_id
        return {'notification_id': 'notification-id'}

    await stq_runner.cargo_performer_fines_send_fine_push.call(
        task_id='test_push',
        kwargs={
            'taxi_order_id': default_taxi_order_id,
            'driver_uuid': driver_id,
            'park_id': park_id,
            'operation_id': default_operation_id,
        },
    )

    if communications_push:
        assert mock_client_notify.times_called == 1
    else:
        assert mock_client_notify.times_called == 0

    if reschedule:
        assert stq.cargo_performer_fines_send_fine_push.times_called == 1
        stq_call = stq.cargo_performer_fines_send_fine_push.next_call()
        assert stq_call == {
            'args': None,
            'eta': datetime.datetime(2020, 2, 25, 4, 10, 0),
            'id': 'test_push',
            'kwargs': None,
            'queue': 'cargo_performer_fines_send_fine_push',
        }
    else:
        assert stq.cargo_performer_fines_send_fine_push.times_called == 0


async def test_fine_cancel(
        mock_fines_state,
        default_dbid_uuid,
        default_taxi_order_id,
        default_operation_id,
        default_fine_code,
        exp3_driver_simple_push_settings,
        setup_order_fines_codes,
        stq_runner,
        mockserver,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    mock_fines_state(park_id=park_id, driver_id=driver_id)

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert request.json == {
            'service': 'taximeter',
            'intent': 'PersonalOffer',
            'notification': {
                'text': {
                    'key': 'order_fines.driver_pushes.fine_canceled',
                    'keyset': 'notify',
                },
            },
            'data': {},
            'client_id': f'{park_id}-{driver_id}',
        }
        assert request.headers['X-Idempotency-Token'] == default_operation_id
        return {'notification_id': 'notification-id'}

    await stq_runner.cargo_performer_fines_send_fine_push.call(
        task_id='test_push',
        kwargs={
            'taxi_order_id': default_taxi_order_id,
            'driver_uuid': driver_id,
            'park_id': park_id,
            'operation_id': default_operation_id,
        },
    )

    assert mock_client_notify.times_called == 1


async def test_state_not_found(
        mock_fines_state,
        default_dbid_uuid,
        default_taxi_order_id,
        default_operation_id,
        default_fine_code,
        exp3_driver_simple_push_settings,
        setup_order_fines_codes,
        stq_runner,
        mockserver,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    mock_fines_state(
        park_id=park_id, driver_id=driver_id, fine_code=default_fine_code,
    )

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': 'notification-id'}

    await stq_runner.cargo_performer_fines_send_fine_push.call(
        task_id='test_push',
        kwargs={
            'taxi_order_id': default_taxi_order_id,
            'driver_uuid': driver_id,
            'park_id': park_id,
            'operation_id': 'UNKNOWN',
        },
        expect_fail=True,
    )

    assert mock_client_notify.times_called == 0


async def test_deleted_fine(
        mock_fines_state,
        default_dbid_uuid,
        default_taxi_order_id,
        default_operation_id,
        default_fine_code,
        exp3_driver_simple_push_settings,
        stq_runner,
        mockserver,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    mock_fines_state(
        park_id=park_id, driver_id=driver_id, fine_code=default_fine_code,
    )

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert request.json == {
            'service': 'taximeter',
            'intent': 'PersonalOffer',
            'notification': {
                'text': {
                    'key': 'order_fines.driver_pushes.fine_assigned_fallback',
                    'keyset': 'notify',
                },
            },
            'data': {},
            'client_id': f'{park_id}-{driver_id}',
        }
        assert request.headers['X-Idempotency-Token'] == default_operation_id
        return {'notification_id': 'notification-id'}

    await stq_runner.cargo_performer_fines_send_fine_push.call(
        task_id='test_push',
        kwargs={
            'taxi_order_id': default_taxi_order_id,
            'driver_uuid': driver_id,
            'park_id': park_id,
            'operation_id': default_operation_id,
        },
    )

    assert mock_client_notify.times_called == 1
