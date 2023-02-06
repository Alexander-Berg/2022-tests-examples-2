import pytest

from order_notify.stq.sbp import transporting_notification


TRANSLATIONS_CLIENT_MESSAGES = {
    'taxi_payments.sbp.push.driving.pay_within_x_minutes': {
        'ru': 'Оплатите в течение %(minutes)s минут',
    },
    'taxi_payments.sbp.push.driving.pay_during_the_trip': {
        'ru': 'Оплатите в течение поездки',
    },
}


@pytest.mark.parametrize(
    'plan_transporting_time_sec,expected_message',
    [
        pytest.param(500, 'Оплатите в течение поездки', id='short_ride'),
        pytest.param(700, 'Оплатите в течение 10 минут', id='long_ride'),
    ],
)
@pytest.mark.config(
    TAXI_PAYMENTS_SBP_TRASACTION_EXPIRE_TIMEOUT=600,
    TAXI_PAYMENTS_SBP_NOTIFICATIONS={
        'transporting': {
            'long_ride_tanker_key': (
                'taxi_payments.sbp.push.driving.pay_within_x_minutes'
            ),
            'short_ride_tanker_key': (
                'taxi_payments.sbp.push.driving.pay_during_the_trip'
            ),
            'enabled': True,
            'short_ride_time_sec': 600,
        },
    },
)
@pytest.mark.translations(client_messages=TRANSLATIONS_CLIENT_MESSAGES)
async def test_sbp_transporting_notification(
        stq3_context, mockserver, plan_transporting_time_sec, expected_message,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _ucommunications_handler(request):
        expected_request = {
            'confirm': True,
            'intent': 'unknown',
            'ttl': 60,
            'user': 'user_1',
            'locale': 'ru',
            'data': {
                'payload': {
                    'id': '00000000000040008000000000000000',
                    'msg': expected_message,
                    'show_in_foreground': True,
                },
                'repack': {
                    'apns': {
                        'aps': {
                            'content-available': 1,
                            'mutable-content': 1,
                            'sound': {'name': 'default'},
                            'alert': expected_message,
                            'repack_payload': [
                                'id',
                                'msg',
                                'show_in_foreground',
                            ],
                        },
                    },
                    'fcm': {
                        'notification': {'title': expected_message},
                        'repack_payload': ['id', 'msg', 'show_in_foreground'],
                    },
                    'hms': {
                        'notification_title': expected_message,
                        'repack_payload': ['id', 'msg', 'show_in_foreground'],
                    },
                },
            },
        }

        assert request.json == expected_request
        return {}

    await transporting_notification.task(
        context=stq3_context,
        user_id='user_1',
        locale='ru',
        plan_transporting_time_sec=plan_transporting_time_sec,
    )
    assert _ucommunications_handler.times_called == 1
