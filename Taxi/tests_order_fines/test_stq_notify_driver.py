import datetime

import pytest


ORDER_FINES_CODES_WITH_NOTIFICATIONS = [
    {
        'description': 'first fine description',
        'disabled': False,
        'fine_code': 'first_fine',
        'title': 'first fine title',
        'driver_notification_params': {
            'tanker_keyset': 'notify',
            'fine_assigned_tanker_key': (
                'order_fines.driver_pushes.fine_assigned_first_fine'
            ),
        },
    },
]

SIMPLE_PUSH_CLIENT_NOTIFY_REQUEST = {
    'service': 'taximeter',
    'intent': 'PersonalOffer',
    'notification': {
        'text': {
            'key': 'order_fines.driver_pushes.fine_assigned_first_fine',
            'keyset': 'notify',
            'params': {'order_created_at': '13.02.2021 10:00'},
        },
    },
    'data': {},
    'client_id': (
        'cc111111111111111111111111111111-dd111111111111111111111111111111'
    ),
}

CUSTOM_PUSH_CLIENT_NOTIFY_REQUEST = {
    'intent': 'FineUpdate',
    'service': 'taximeter',
    'collapse_key': 'FineUpdate',
    'data': {
        'fine_identity': {'order_id': 'aa111111111111111111111111111111'},
        'button_label': {
            'key': 'order_fines.driver_pushes.custom_push.button_label',
            'keyset': 'notify',
        },
    },
    'notification': {
        'text': {
            'key': 'order_fines.driver_pushes.fine_assigned_first_fine',
            'keyset': 'notify',
            'params': {'order_created_at': '13.02.2021 10:00'},
        },
    },
    'client_id': (
        'cc111111111111111111111111111111-dd111111111111111111111111111111'
    ),
}


async def _check_saved_driver_notifications(pgsql, expected_exists):
    cursor = pgsql['order_fines'].cursor()
    cursor.execute(
        """
        SELECT operation_id, order_id
        FROM order_fines.driver_notifications
        """,
    )
    if expected_exists:
        assert cursor.fetchall() == [
            (
                '1-0-1111-11111111111111111111111111111111',
                '11111111111111111111111111111111',
            ),
        ]
    else:
        assert cursor.fetchall() == []


@pytest.fixture(name='mock_taxi_tariffs_response')
def _mock_taxi_tariffs_response(mockserver):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _mock_handle(request):
        zone = request.args['zone_names'][0]
        response = {
            'zones': [
                {
                    'zone': zone,
                    'tariff_settings': {'timezone': 'Europe/Madrid'},
                },
            ],
        }
        return mockserver.make_response(json=response, status=200)


@pytest.mark.config(ORDER_FINES_CODES=ORDER_FINES_CODES_WITH_NOTIFICATIONS)
async def test_happy_path(
        stq_runner,
        mockserver,
        order_proc,
        save_decision,
        handlers,
        mock_taxi_tariffs_response,
):
    decision = {'has_fine': True, 'fine_code': 'first_fine'}
    await save_decision(decision, order_proc['_id'])

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert request.json == SIMPLE_PUSH_CLIENT_NOTIFY_REQUEST
        assert (
            request.headers['X-Idempotency-Token']
            == '1-0-1111-11111111111111111111111111111111'
        )
        return {'notification_id': 'some-magic-notification-id'}

    await stq_runner.order_fines_notify_driver_on_fine.call(
        task_id='123',
        kwargs={'taxi_order_id': order_proc['_id']},
        expect_fail=False,
    )

    assert mock_client_notify.times_called == 1


@pytest.mark.parametrize(
    'ignore_any_push, communications_push', [(True, False), (False, True)],
)
@pytest.mark.config(ORDER_FINES_CODES=ORDER_FINES_CODES_WITH_NOTIFICATIONS)
@pytest.mark.experiments3()
async def test_ignore_any_push(
        stq_runner,
        mockserver,
        experiments3,
        order_proc,
        taxi_order_fines,
        save_decision,
        handlers,
        pgsql,
        mock_taxi_tariffs_response,
        ignore_any_push,
        communications_push,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='order_fines_driver_push_settings',
        consumers=['order-fines/custom-pushes'],
        clauses=[],
        default_value={'ignore_any_push': ignore_any_push},
    )
    await taxi_order_fines.invalidate_caches()

    decision = {'has_fine': True, 'fine_code': 'first_fine'}
    await save_decision(decision, order_proc['_id'])

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert request.json == SIMPLE_PUSH_CLIENT_NOTIFY_REQUEST
        assert (
            request.headers['X-Idempotency-Token']
            == '1-0-1111-11111111111111111111111111111111'
        )
        return {'notification_id': 'some-magic-notification-id'}

    await stq_runner.order_fines_notify_driver_on_fine.call(
        task_id='123',
        kwargs={'taxi_order_id': order_proc['_id']},
        expect_fail=False,
    )

    if communications_push:
        assert mock_client_notify.times_called == 1
    else:
        assert mock_client_notify.times_called == 0
    await _check_saved_driver_notifications(pgsql, True)


@pytest.mark.parametrize(
    'delay_after_decision_resolved, communications_push, reschedule',
    [(60, True, False), (3600, False, True)],
)
@pytest.mark.config(ORDER_FINES_CODES=ORDER_FINES_CODES_WITH_NOTIFICATIONS)
@pytest.mark.translations(
    notify={
        'order_fines.driver_pushes.fine_assigned_first_fine': {
            'ru': 'Fine Assigned First Fine %(order_created_at)s',
        },
    },
    taximeter_backend_driver_messages={
        'order_fines.driver_pushes.custom_push.button_label': {
            'ru': 'Подробнее',
        },
    },
)
@pytest.mark.experiments3()
@pytest.mark.now('2021-02-13T11:03:03+0000')
async def test_custom_push(
        stq_runner,
        mockserver,
        experiments3,
        order_proc,
        taxi_order_fines,
        save_decision,
        handlers,
        mock_taxi_tariffs_response,
        pgsql,
        stq,
        delay_after_decision_resolved,
        communications_push,
        reschedule,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='order_fines_driver_push_settings',
        consumers=['order-fines/custom-pushes'],
        clauses=[],
        default_value={
            'enable_custom_push': True,
            'delay_after_decision_resolved': delay_after_decision_resolved,
        },
    )
    await taxi_order_fines.invalidate_caches()

    decision = {'has_fine': True, 'fine_code': 'first_fine'}
    await save_decision(decision, order_proc['_id'])

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert request.json == CUSTOM_PUSH_CLIENT_NOTIFY_REQUEST
        assert (
            request.headers['X-Idempotency-Token']
            == '1-0-1111-11111111111111111111111111111111'
        )
        return {'notification_id': 'some-magic-notification-id'}

    await stq_runner.order_fines_notify_driver_on_fine.call(
        task_id='123',
        kwargs={'taxi_order_id': order_proc['_id']},
        expect_fail=False,
    )

    if communications_push:
        assert mock_client_notify.times_called == 1
    else:
        assert mock_client_notify.times_called == 0
    await _check_saved_driver_notifications(pgsql, communications_push)

    if reschedule:
        assert stq.order_fines_notify_driver_on_fine.times_called == 1
        stq_call = stq.order_fines_notify_driver_on_fine.next_call()
        assert stq_call == {
            'args': None,
            'eta': datetime.datetime(2021, 2, 13, 12, 0, 2),
            'id': '123',
            'kwargs': None,
            'queue': 'order_fines_notify_driver_on_fine',
        }
    else:
        assert stq.order_fines_notify_driver_on_fine.times_called == 0


@pytest.mark.config(ORDER_FINES_CODES=ORDER_FINES_CODES_WITH_NOTIFICATIONS)
async def test_fine_cancel(
        stq_runner,
        mockserver,
        order_proc,
        save_decision,
        handlers,
        fines_queue,
        mock_taxi_tariffs_response,
):
    decision = {'has_fine': False, 'fine_code': 'first_fine'}
    await save_decision(decision, order_proc['_id'])

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert request.json == {
            'intent': 'PersonalOffer',
            'service': 'taximeter',
            'notification': {
                'text': {
                    'key': 'order_fines.driver_pushes.fine_canceled',
                    'keyset': 'notify',
                    'params': {'order_created_at': '13.02.2021 10:00'},
                },
            },
            'data': {},
            'client_id': (
                'cc111111111111111111111111111111-'
                'dd111111111111111111111111111111'
            ),
        }
        assert (
            request.headers['X-Idempotency-Token']
            == '1-11-1111-11111111111111111111111111111111'
        )
        return {'notification_id': 'some-magic-notification-id'}

    fines_queue.restore_events_rejected_fine()
    await stq_runner.order_fines_notify_driver_on_fine.call(
        task_id='123',
        kwargs={'taxi_order_id': order_proc['_id']},
        expect_fail=False,
    )

    assert mock_client_notify.times_called == 1


@pytest.mark.config(ORDER_FINES_CODES=ORDER_FINES_CODES_WITH_NOTIFICATIONS)
async def test_unique_push(
        stq_runner,
        mockserver,
        order_proc,
        save_decision,
        handlers,
        mock_taxi_tariffs_response,
):
    decision = {'has_fine': True, 'fine_code': 'first_fine'}
    await save_decision(decision, order_proc['_id'])

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': 'some-magic-notification-id'}

    await stq_runner.order_fines_notify_driver_on_fine.call(
        task_id='123',
        kwargs={'taxi_order_id': order_proc['_id']},
        expect_fail=False,
    )
    # Double requests
    await stq_runner.order_fines_notify_driver_on_fine.call(
        task_id='123',
        kwargs={'taxi_order_id': order_proc['_id']},
        expect_fail=False,
    )

    assert mock_client_notify.times_called == 1


async def test_order_not_found(stq_runner, order_proc, mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': 'some-magic-notification-id'}

    await stq_runner.order_fines_notify_driver_on_fine.call(
        task_id='123', kwargs={'taxi_order_id': 'UNKNOWN'}, expect_fail=True,
    )

    assert mock_client_notify.times_called == 0


@pytest.mark.config(ORDER_FINES_CODES=[])
async def test_deleted_fine(
        stq_runner,
        mockserver,
        order_proc,
        save_decision,
        handlers,
        mock_taxi_tariffs_response,
):
    # Fine was deleted from config ORDER_FINES_CODES

    decision = {'has_fine': True, 'fine_code': 'first_fine'}
    await save_decision(decision, order_proc['_id'])

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        assert (
            request.json['notification']['text']['key']
            == 'order_fines.driver_pushes.fine_assigned_fallback'
        )
        assert request.json['notification']['text']['keyset'] == 'notify'
        return {'notification_id': 'some-magic-notification-id'}

    await stq_runner.order_fines_notify_driver_on_fine.call(
        task_id='123',
        kwargs={'taxi_order_id': order_proc['_id']},
        expect_fail=False,
    )

    assert mock_client_notify.times_called == 1


@pytest.mark.config(
    ORDER_FINES_CODES=ORDER_FINES_CODES_WITH_NOTIFICATIONS,
    ORDER_FINES_DRIVER_PUSH_ON_FINE_TTL={'ttl_hours': 48, 'enabled': True},
)
async def test_expired_notification(
        stq_runner,
        mockserver,
        order_proc,
        save_decision,
        handlers,
        mock_taxi_tariffs_response,
):
    # Do not notify driver because it's too late

    decision = {'has_fine': True, 'fine_code': 'first_fine'}
    await save_decision(decision, order_proc['_id'])

    @mockserver.json_handler('/client-notify/v2/push')
    def mock_client_notify(request):
        return {'notification_id': 'some-magic-notification-id'}

    await stq_runner.order_fines_notify_driver_on_fine.call(
        task_id='123',
        kwargs={'taxi_order_id': order_proc['_id']},
        expect_fail=False,
    )

    assert mock_client_notify.times_called == 0
