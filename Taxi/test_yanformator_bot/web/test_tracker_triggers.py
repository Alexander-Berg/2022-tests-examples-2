import pytest

TELEGRAM_LOGIN = 'TestLoginTG'
TELEGRAM_ID = '123123'
CHAT_ID = '-456'


@pytest.mark.config(
    YANFORMATOR_BOT_NOTIFICATION_SETTINGS=[
        {
            'info': {
                'name': 'efficiency',
                'owners': ['alex-tsarkov'],
                'telegram_channels': [CHAT_ID],
                'subscribers': ['dlefimov'],
                'abc_duty_group': 'very_responsible_group',
            },
            'tracker_trigger': {'components': ['taxi_efficiency_dispatch']},
        },
        {
            'info': {
                'name': 'infra',
                'owners': ['algol83'],
                'telegram_channels': [CHAT_ID],
                'subscribers': ['dlefimov'],
            },
            'tracker_trigger': {
                'components': ['taxi_infra'],
                'tg_channels_override': ['-123'],
            },
        },
    ],
)
async def test_tracker_duty(taxi_yanformator_bot_web, mockserver, load_json):
    messages_count = 0

    @mockserver.json_handler(
        '/telegram/bot666666666:AAAAAAAAAA_WWWWWWWWWWWWWWWWWWWWWWWW'
        '/sendMessage',
    )
    def _telegram(request):
        nonlocal messages_count
        assert request.json == load_json('messages.json')[messages_count]
        messages_count += 1
        return {'ok': True}

    response = await taxi_yanformator_bot_web.post(
        '/v1/tracker_trigger',
        json={
            'components': 'taxi_efficiency_dispatch, taxi_infra',
            'ticket_id': 'TAXIDUTY-12345',
            'title': 'Drivers are absent',
        },
    )
    assert response.status == 200

    await _telegram.wait_call()
    await _telegram.wait_call()

    response = await taxi_yanformator_bot_web.post(
        '/v1/tracker_trigger',
        json={
            'components': 'taxi_infra',
            'ticket_id': 'TAXIDUTY-67890',
            'title': 'Drivers disappeared',
            'level': 'Критичный',
        },
    )
    assert response.status == 200

    await _telegram.wait_call()


@pytest.mark.config(
    YANFORMATOR_BOT_NOTIFICATION_SETTINGS=[
        {
            'info': {
                'name': 'efficiency',
                'owners': ['alex-tsarkov'],
                'telegram_channels': [CHAT_ID],
                'subscribers': ['dlefimov'],
                'abc_duty_group': 'very_responsible_group',
            },
            'tracker_trigger': {'tags': ['beta']},
        },
        {
            'info': {
                'name': 'infra',
                'owners': ['algol83'],
                'telegram_channels': [CHAT_ID],
                'subscribers': ['dlefimov'],
            },
            'tracker_trigger': {
                'tags': ['alpha', 'beta'],
                'tg_channels_override': ['-123'],
            },
        },
        {
            'info': {
                'name': 'some_other_group_with_same_duty_person',
                'owners': ['abd-damir'],
                'telegram_channels': [CHAT_ID],
                'subscribers': ['abd-damir'],
                'abc_duty_group': 'another_very_responsible_group',
            },
        },
    ],
)
async def test_tracker_tags(taxi_yanformator_bot_web, mockserver, load_json):
    messages_count = 0

    @mockserver.json_handler(
        '/telegram/bot666666666:AAAAAAAAAA_WWWWWWWWWWWWWWWWWWWWWWWW'
        '/sendMessage',
    )
    def _telegram(request):
        nonlocal messages_count
        assert request.json == load_json('messages.json')[messages_count]
        messages_count += 1
        return {'ok': True}

    response = await taxi_yanformator_bot_web.post(
        '/v1/tracker_trigger',
        json={
            'tags': 'alpha, beta',
            'ticket_id': 'TAXIDUTY-12345',
            'title': 'Drivers are absent',
        },
    )
    assert response.status == 200

    await _telegram.wait_call()
    await _telegram.wait_call()

    response = await taxi_yanformator_bot_web.post(
        '/v1/tracker_trigger',
        json={
            'components': 'taxi_infra',
            'tags': 'alpha',
            'ticket_id': 'TAXIDUTY-67890',
            'title': 'Drivers disappeared',
            'level': 'Критичный',
        },
    )
    assert response.status == 200

    await _telegram.wait_call()

    response = await taxi_yanformator_bot_web.post(
        '/v1/tracker_trigger',
        json={
            'tags': 'gamma',
            'ticket_id': 'TAXIDUTY-67890',
            'title': 'Drivers disappeared',
            'level': 'Критичный',
        },
    )
    assert response.status == 200
    assert _telegram.times_called == 0


@pytest.mark.parametrize(
    'has_login, need_to_send_direct_message',
    [
        pytest.param(
            True,
            True,
            marks=pytest.mark.config(
                YANFORMATOR_BOT_TELEGRAM_ID_BY_LOGIN={
                    TELEGRAM_LOGIN: TELEGRAM_ID,
                },
            ),
            id='has_login_with_direct',
        ),
        pytest.param(
            True,
            False,
            marks=pytest.mark.config(
                YANFORMATOR_BOT_TELEGRAM_ID_BY_LOGIN={
                    TELEGRAM_LOGIN: TELEGRAM_ID,
                },
            ),
            id='has_login_without_direct',
        ),
        pytest.param(False, False, id='does_not_have_login'),
    ],
)
@pytest.mark.parametrize('has_comment', [True, False])
@pytest.mark.config(
    YANFORMATOR_BOT_NOTIFICATION_SETTINGS=[
        {
            'info': {
                'name': 'efficiency',
                'owners': ['alex-tsarkov'],
                'telegram_channels': [CHAT_ID],
                'subscribers': ['dlefimov'],
            },
            'tracker_trigger': {
                'tags': ['beta'],
                'need_to_send_direct_message': True,
            },
        },
    ],
)
async def test_tracker_discounts(
        taxi_yanformator_bot_web,
        mockserver,
        load_json,
        has_login,
        need_to_send_direct_message,
        has_comment,
        taxi_config,
):
    taxi_config.set(
        YANFORMATOR_BOT_NOTIFICATION_SETTINGS=[
            {
                'info': {
                    'name': 'efficiency',
                    'owners': ['alex-tsarkov'],
                    'telegram_channels': [CHAT_ID],
                    'subscribers': ['dlefimov'],
                },
                'tracker_trigger': {
                    'tags': ['beta'],
                    'need_to_send_direct_message': need_to_send_direct_message,
                },
            },
        ],
    )
    telegram_messages = []

    @mockserver.json_handler(
        '/telegram/bot666666666:AAAAAAAAAA_WWWWWWWWWWWWWWWWWWWWWWWW'
        '/sendMessage',
    )
    def _telegram(request):
        telegram_messages.append(request.json)
        return {'ok': True}

    @mockserver.json_handler('/startrek/issues/TAXIBUDGETALERT-8449')
    def _st_main_ticket(request):
        return {
            'id': '123',
            'key': 'TAXIBUDGETALERT-8449',
            'created_by': {'id': 'robot-budgetalert'},
            'description': '1. ticket for create discount: INTPRICING-2301',
        }

    @mockserver.json_handler('/startrek/issues/TAXIBUDGETALERT-8449/comments')
    def _st_comments(request):
        if has_comment:
            return [{'id': 123, 'text': 'comment text'}]
        return []

    @mockserver.json_handler('/startrek/issues/INTPRICING-2301')
    def _st_ticket_in_description(request):
        return {
            'id': '8449',
            'key': 'INTPRICING-2301',
            'created_by': {'id': 'staff-login'},
            'description': 'description',
        }

    @mockserver.json_handler('/staff/v3/persons')
    def _staff(requeest):
        result = []
        if has_login:
            result.append(
                {
                    'accounts': [
                        {
                            'value': 'TestLoginTG',
                            'type': 'telegram',
                            'private': False,
                            'id': 0,
                        },
                    ],
                    'login': 'staff-login',
                },
            )
        return {
            'links': {},
            'page': 1,
            'limit': 50,
            'result': result,
            'total': 1,
            'pages': 1,
        }

    response = await taxi_yanformator_bot_web.post(
        '/v1/tracker_trigger',
        json={
            'tags': 'beta',
            'ticket_id': 'TAXIBUDGETALERT-8449',
            'title': 'KZ_tier2_new_09_21 discount limit',
            'message_type': 'discounts',
        },
    )
    assert response.status == 200, await response.json()
    postfix = ''
    description = '1. ticket for create discount: INTPRICING-2301'
    if has_comment:
        description = 'comment text'

    text = (
        f'<b>Hey guys! New ticket TAXIBUDGETALERT-8449</b>\n'
        f'<a href="https://st.yandex-team.ru/TAXIBUDGETALERT-8449">'
        f'KZ_tier2_new_09_21 discount limit</a>\n'
        f'{description}\n'
        f'{postfix}'
    )
    if has_login:
        text += f'@{TELEGRAM_LOGIN}'

    if need_to_send_direct_message:
        assert telegram_messages == [
            {'chat_id': CHAT_ID, 'parse_mode': 'HTML', 'text': text},
            {'chat_id': TELEGRAM_ID, 'parse_mode': 'HTML', 'text': text},
        ]
    else:
        assert telegram_messages == [
            {'chat_id': CHAT_ID, 'parse_mode': 'HTML', 'text': text},
        ]
