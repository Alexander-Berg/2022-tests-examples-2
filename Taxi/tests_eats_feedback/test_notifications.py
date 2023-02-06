# flake8: noqa
# pylint: disable=import-error,wildcard-import
import json
import psycopg2
import pytest

MOCK_NOW = '2020-07-24T12:59:59+00:00'
MOCK_EXPIRATE = '2020-07-23T12:59:59+00:00'
LOGBROKER_CONSUMER_SETTINGS = {
    'order_client_events_consumer': {
        'enabled': True,
        'chunk_size': 2,
        'queue_timeout_ms': 50,
        'config_poll_period_ms': 1000,
    },
}
NOTIFICATIONS_SETTINGS_ENABLED = {
    'enabled': True,
    'expiration_time': 600,
    'max_exec_tries': 2,
}
NOTIFICATIONS_SETTINGS_DISABLED = {
    'enabled': False,
    'expiration_time': 600,
    'max_exec_tries': 0,
}


def _get_payload(order_nr, personal_phone_id='123123'):
    payload = {
        'order_nr': order_nr,
        'eater_personal_phone_id': personal_phone_id,
    }
    payload['order_event'] = 'finished'
    payload['created_at'] = '2020-09-04T15:26:43+00:00'
    payload['order_type'] = 'order_type'
    payload['delivery_type'] = 'delivery_type'
    payload['shipping_type'] = 'shipping_type'
    payload['eater_id'] = '123123'
    payload['eater_passport_uid'] = '123123'
    payload['promised_at'] = '2020-09-04T16:26:43+00:00'
    payload['application'] = 'web'
    payload['place_id'] = '123123'
    payload['payed_at'] = '2020-09-04T15:26:48+00:00'
    payload['payed_at'] = '2020-09-04T15:26:51+00:00'
    payload['taken_at'] = '2020-09-04T15:56:51+00:00'
    payload['finished_at'] = '2020-09-04T15:59:51+00:00'
    payload['cancelled_at'] = '2020-09-04T16:59:51+00:00'
    payload['cancellation_reason'] = 'not_ready'
    payload['cancelled_by'] = 'operator'
    payload['promised_at'] = '2020-09-04T17:59:51+00:00'
    payload['payment_method'] = 'payment-method'

    return payload


async def _push_lb_order(taxi_eats_feedback, lb_order):
    message = str(json.dumps(lb_order))
    response = await taxi_eats_feedback.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-client-events-consumer',
                'data': message,
                'topic': '/eda/processing/testing/order-client-events',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200


@pytest.mark.config(
    EATS_FEEDBACK_LOGBROKER_CONSUMER_SETTINGS=LOGBROKER_CONSUMER_SETTINGS,
    EATS_FEEDBACK_NOTIFICATION_SETTINGS=NOTIFICATIONS_SETTINGS_DISABLED,
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.experiments3(filename='notifications_exp.json')
async def test_send_stq(taxi_eats_feedback, stq):
    lb_orders = [
        _get_payload('111111-100000', '100000'),
        _get_payload('111111-100001', '100001'),
        _get_payload('111111-100002', '100002'),
        _get_payload('111111-100003', '100003'),
    ]

    for lb_order in lb_orders:
        await _push_lb_order(taxi_eats_feedback, lb_order)

    # wait for lb messages to be read
    await taxi_eats_feedback.run_task(
        'order-client-events-consumer-lb_consumer',
    )

    assert stq.eats_feedback_notifications.times_called == 1

    stq_kwargs = stq.eats_feedback_notifications.next_call()['kwargs']
    del stq_kwargs['log_extra']
    assert stq_kwargs == {
        'notification': {
            'order_nr': '111111-100003',
            'payload': {
                'idempotency_key': 'order_nr:111111-100003',
                'notification_event': 'some_event',
                'allowed_channels': ['sms', 'push'],
            },
        },
        'start_timestamp': MOCK_NOW,
    }


@pytest.fixture(name='mock_eats_core_communication')
def _mock_eats_core_communication(mockserver):
    @mockserver.json_handler(
        '/eats-core-communication/internal-api/v1/communication/notification',
    )
    def mock(request):
        order_nr = request.json['order_nr']
        if order_nr == '111111-100003':
            return mockserver.make_response(
                status=200, json={'notification_id': '52394834'},
            )

        return mockserver.make_response(
            status=500,
            json={
                'code': 'dummy_error_code_500',
                'message': 'dummy_message_500',
            },
        )

    return mock


@pytest.mark.config(
    EATS_FEEDBACK_NOTIFICATION_SETTINGS=NOTIFICATIONS_SETTINGS_ENABLED,
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    """order_nr,payload,start_timestamp,expect_stq_fail,exec_tries,communication_expected_times_called""",
    [
        (
            '111111-100003',
            {
                'idempotency_key': 'order_nr:111111-100003',
                'notification_event': 'some_event',
                'allowed_channels': ['sms', 'push'],
            },
            MOCK_NOW,
            False,
            0,
            1,
        ),
        (
            '111111-100004',
            {
                'idempotency_key': 'order_nr:111111-100004',
                'notification_event': 'some_event',
                'allowed_channels': ['sms', 'push'],
            },
            MOCK_EXPIRATE,
            False,
            0,
            2,
        ),
        (
            '111111-100005',
            {
                'idempotency_key': 'order_nr:111111-100005',
                'notification_event': 'some_event',
                'allowed_channels': ['sms', 'push'],
            },
            MOCK_NOW,
            False,
            4,
            2,
        ),
        (
            '111111-100006',
            {
                'idempotency_key': 'order_nr:111111-100006',
                'notification_event': 'some_event',
                'allowed_channels': ['sms', 'push'],
            },
            MOCK_NOW,
            True,
            0,
            2,
        ),
        (
            '111111-100007',
            {
                'idempotency_key': 'order_nr:111111-100007',
                'notification_event': 'some_event',
                'allowed_channels': ['sms', 'push'],
            },
            MOCK_NOW,
            False,
            0,
            0,
        ),
        (
            '111111-100008',
            {
                'idempotency_key': 'order_nr:111111-100008',
                'notification_event': 'some_event',
                'allowed_channels': ['sms', 'push'],
            },
            MOCK_NOW,
            False,
            0,
            0,
        ),
    ],
)
@pytest.mark.pgsql('eats_feedback', files=['feedbacks.sql'])
async def test_stq_consumer_enabled(
        stq_runner,
        mock_eats_core_communication,
        order_nr,
        payload,
        expect_stq_fail,
        start_timestamp,
        exec_tries,
        communication_expected_times_called,
):
    await stq_runner.eats_feedback_notifications.call(
        task_id='sample_task',
        kwargs={
            'link': 'some_link',
            'notification': {'order_nr': order_nr, 'payload': payload},
            'start_timestamp': start_timestamp,
        },
        expect_fail=expect_stq_fail,
        exec_tries=exec_tries,
    )

    assert (
        mock_eats_core_communication.times_called
        == communication_expected_times_called
    )


@pytest.mark.config(
    EATS_FEEDBACK_NOTIFICATION_SETTINGS=NOTIFICATIONS_SETTINGS_DISABLED,
)
@pytest.mark.now(MOCK_NOW)
async def test_stq_consumer_disabled(stq_runner, mock_eats_core_communication):
    await stq_runner.eats_feedback_notifications.call(
        task_id='sample_task',
        kwargs={
            'link': 'some_link',
            'notification': {
                'order_nr': '111111-100002',
                'payload': {
                    'idempotency_key': 'order_nr:111111-100002',
                    'notification_event': 'some_event',
                    'allowed_channels': ['sms', 'push'],
                },
            },
            'start_timestamp': MOCK_NOW,
        },
    )
