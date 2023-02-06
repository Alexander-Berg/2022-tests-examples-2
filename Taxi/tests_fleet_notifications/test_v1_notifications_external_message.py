import pytest

from tests_fleet_notifications import utils

ENDPOINT = '/v1/notifications/external-message'
FLEET_NOTIFICATIONS_TELEGRAM_BOT_ENDPOINT = (
    '/fleet-notifications-telegram-bot/internal'
    '/fleet-notifications-telegram-bot/v1/message'
)
DISPATCHER_ACCESS_CONTROL_ENDPOINT = (
    '/dispatcher-access-control/v1/parks/users/list'
)
HEADERS = {
    'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
    'X-Idempotency-Token': 'idempotency_token',
}

PAYLOAD = {'title': 'Test', 'text': 'testing test'}

DAC_USERS = [
    {
        'park_id': 'p1',
        'id': 'u1',
        'is_enabled': True,
        'is_confirmed': True,
        'is_superuser': False,
        'group_id': 'g1',
        'is_usage_consent_accepted': True,
        'email': 'user1@yandex.ru',
        'passport_uid': '1',
    },
    {
        'park_id': 'p1',
        'id': 'u2',
        'is_enabled': True,
        'is_confirmed': True,
        'is_superuser': False,
        'group_id': 'g1',
        'is_usage_consent_accepted': True,
        'email': 'user2@yandex.ru',
        'passport_uid': '2',
    },
    {
        'park_id': 'p1',
        'id': 'u3',
        'is_enabled': True,
        'is_confirmed': True,
        'is_superuser': True,
        'is_usage_consent_accepted': True,
        'email': 'user3@yandex.ru',
        'passport_uid': '3',
    },
]

EMAIL_TO_PDID = {
    'user1@yandex.ru': 'pd1',
    'user2@yandex.ru': 'pd2',
    'user3@yandex.ru': 'pd3',
}


OK_PARAMS = [
    pytest.param({}, {'email': True, 'telegram': True}, 1, 1, id='only_park'),
    pytest.param(
        {'group_id': 'g1'},
        {'email': True, 'telegram': True},
        1,
        1,
        id='group_id',
    ),
    pytest.param(
        {'user_id': 'u2'},
        {'email': True, 'telegram': True},
        1,
        1,
        id='user_id',
    ),
    pytest.param(
        {'position': 'director'},
        {'email': True, 'telegram': True},
        1,
        1,
        id='director',
    ),
    pytest.param(
        {}, {'email': True, 'telegram': False}, 1, 0, id='only_email',
    ),
    pytest.param(
        {}, {'email': False, 'telegram': True}, 0, 1, id='only_telegram',
    ),
    pytest.param(
        {}, {'email': False, 'telegram': False}, 0, 0, id='no_notifications',
    ),
]


@pytest.mark.parametrize(
    'destinations_extra, notification_types, '
    'stq_calls_amount_email, stq_calls_amount_telegram',
    OK_PARAMS,
)
async def test_send_external(
        taxi_fleet_notifications,
        mockserver,
        destinations_extra,
        notification_types,
        stq_calls_amount_email,
        stq_calls_amount_telegram,
        stq,
        stq_runner,
):
    @mockserver.json_handler(FLEET_NOTIFICATIONS_TELEGRAM_BOT_ENDPOINT)
    def _mock_v1_bot_message(request):
        assert notification_types['telegram']
        receivers = request.json['receivers']
        if 'group_id' in destinations_extra:
            assert len(receivers) == 2
        elif 'user_id' in destinations_extra:
            assert len(receivers) == 1
        elif 'position' in destinations_extra:
            assert len(receivers) == 1
        else:
            assert len(receivers) == 3
        return mockserver.make_response(status=200)

    @mockserver.json_handler(DISPATCHER_ACCESS_CONTROL_ENDPOINT)
    def _mock_usrs_list(request):
        if 'user_id' in destinations_extra:
            return {'offset': 2, 'users': DAC_USERS[1:2]}
        return {'offset': 2, 'users': DAC_USERS}

    @mockserver.json_handler('/personal/v1/emails/bulk_store')
    def _mock_personal(request):
        return {
            'items': [
                {'id': EMAIL_TO_PDID[item['value']], 'value': item['value']}
                for item in request.json['items']
            ],
            'offset': 0,
        }

    @mockserver.json_handler('/sticker/send/')
    def _sticker(request):
        assert notification_types['email']
        emails = request.json['send_to']
        assert len(emails) == 1
        if 'group_id' in destinations_extra:
            assert emails in [['pd2'], ['pd1']]
        elif 'user_id' in destinations_extra:
            assert emails in [['pd2']]
        elif 'position' in destinations_extra:
            assert emails in [['pd3']]
        else:
            assert emails in [['pd2'], ['pd1'], ['pd3']]
        return mockserver.make_response(status=200)

    response = await taxi_fleet_notifications.post(
        ENDPOINT,
        json={
            'notification_types': notification_types,
            'destinations': [{'park_id': 'p1', **destinations_extra}],
            'payload': PAYLOAD,
        },
        headers=HEADERS,
    )

    assert response.status_code == 200, response.text

    assert (
        stq.fleet_notifications_external_message_telegram.times_called
        == stq_calls_amount_telegram
    )
    assert (
        stq.fleet_notifications_external_message_email.times_called
        == stq_calls_amount_email
    )

    if stq_calls_amount_telegram != 0:
        stq_call = (
            stq.fleet_notifications_external_message_telegram.next_call()
        )
        await stq_runner.fleet_notifications_external_message_telegram.call(
            task_id=stq_call['id'],
            args=stq_call['args'],
            kwargs=stq_call['kwargs'],
        )
    if stq_calls_amount_email != 0:
        stq_call = stq.fleet_notifications_external_message_email.next_call()
        await stq_runner.fleet_notifications_external_message_email.call(
            task_id=stq_call['id'],
            args=stq_call['args'],
            kwargs=stq_call['kwargs'],
        )


INVALID_DESTINATION_PARAMS = [
    {'park_id': 'park1', 'group_id': 'group1', 'user_id': 'user1'},
    {'park_id': 'park1', 'group_id': 'group1', 'position': 'director'},
    {'park_id': 'park1', 'user_id': 'user1', 'position': 'director'},
]


@pytest.mark.parametrize('destination', INVALID_DESTINATION_PARAMS)
async def test_invalid_destination_external(
        taxi_fleet_notifications, destination,
):
    response = await taxi_fleet_notifications.post(
        ENDPOINT,
        json={
            'destinations': [destination],
            'payload': PAYLOAD,
            'notification_types': {'email': True, 'telegram': False},
        },
        headers=HEADERS,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_destination',
        'message': 'Too many destination properties',
    }
