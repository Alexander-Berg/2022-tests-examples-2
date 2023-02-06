import pytest

CONFIG_TELEGRAM_SETTINGS = {
    'telegram_events': [
        {
            'event_type': 'daily-digest',
            'template': [
                '<b>{place_name} ({place_address})</b>',
                '',
                'first value: {first}',
                'second_value : {second}',
            ],
        },
    ],
}
CONFIG_SEND_EVENT_SETTINGS = {
    'partner_search_limit': 1,
    'event_communication_types': [
        {'event_type': 'daily-digest', 'communication_types': ['telegram']},
    ],
}
CFG_SUBS_CHECK = {
    'features': [{'feature': 'boss_bot', 'event_types': ['daily-digest']}],
}
CFG_RETRY_SETTINGS = {'limit': 30, 'delay': 60000}


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_TELEGRAM_SETTINGS=CONFIG_TELEGRAM_SETTINGS,
    EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS=CONFIG_SEND_EVENT_SETTINGS,
    EATS_RESTAPP_COMMUNICATIONS_SEND_EVENT_SUBSCRIPTION_CHECK=CFG_SUBS_CHECK,
)
async def test_send_event(
        taxi_eats_restapp_communications, stq, mockserver, pgsql,
):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/feature/enabled-for-places',
    )
    def _mock_subscriptions(request):
        req = request.json
        assert req['feature'] == 'boss_bot'
        assert req['place_ids'] == [1, 2, 3]
        resp = {
            'feature': 'boss_bot',
            'places': {
                'with_enabled_feature': [1, 3],
                'with_disabled_feature': [2],
            },
        }
        return mockserver.make_response(status=200, json=resp)

    event = 'daily-digest'
    place_ids = [1, 2, 3]
    json_data = {'first': 'some value', 'second': 'other value'}
    params = {'event_type': event}
    data = {'recipients': {'place_ids': place_ids}, 'data': json_data}
    response = await taxi_eats_restapp_communications.post(
        '/internal/communications/v1/send-event', params=params, json=data,
    )
    assert response.status_code == 204

    assert _mock_subscriptions.times_called == 1
    assert stq.eats_restapp_communications_event_sender.times_called == 1
    arg = stq.eats_restapp_communications_event_sender.next_call()
    assert arg['queue'] == 'eats_restapp_communications_event_sender'

    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients, data, deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (arg['id'],),
    )
    res = cursor.fetchall()
    assert res == [
        (
            event,
            'asap',
            {'emails_types': [], 'recipients': {'place_ids': [1, 3]}},
            json_data,
            None,
        ),
    ]


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_TELEGRAM_SETTINGS=CONFIG_TELEGRAM_SETTINGS,
    EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS=CONFIG_SEND_EVENT_SETTINGS,
)
async def test_not_contained_event_with_metrics(
        taxi_eats_restapp_communications,
        taxi_eats_restapp_communications_monitor,
        stq,
):
    metrics_name = 'global-statistics'
    metrics = (
        await taxi_eats_restapp_communications_monitor.get_metrics(
            metrics_name,
        )
    )[metrics_name]
    errors_on_start = metrics.get('slug_error', 0)

    event = 'unknown-event'
    place_ids = [1, 2, 3]
    json_data = {'first': 'some value', 'second': 'other value'}
    params = {'event_type': event}
    data = {'recipients': {'place_ids': place_ids}, 'data': json_data}
    response = await taxi_eats_restapp_communications.post(
        '/internal/communications/v1/send-event', params=params, json=data,
    )
    assert response.status_code == 400
    assert stq.eats_restapp_communications_event_sender.times_called == 0

    metrics = (
        await taxi_eats_restapp_communications_monitor.get_metrics(
            metrics_name,
        )
    )[metrics_name]
    errors = metrics.get('slug_error', 0)
    assert errors == errors_on_start + 1


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_TELEGRAM_SETTINGS=CONFIG_TELEGRAM_SETTINGS,
    EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS=CONFIG_SEND_EVENT_SETTINGS,
)
async def test_stq_send_by_place_ids_no_logins(mockserver, stq_runner, stq):
    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='fake_task',
    )
    assert stq.eats_restapp_tg_bot_send_message.times_called == 0


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_bind_places_logins.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_TELEGRAM_SETTINGS=CONFIG_TELEGRAM_SETTINGS,
    EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS=CONFIG_SEND_EVENT_SETTINGS,
)
@pytest.mark.parametrize(
    'resolved_logins',
    [
        pytest.param(
            True,
            marks=(
                pytest.mark.config(EATS_RESTAPP_TG_BOT_ENABLE_PERSONAL=False)
            ),
            id='send to logins resolved in personal',
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.config(EATS_RESTAPP_TG_BOT_ENABLE_PERSONAL=True)
            ),
            id='send to login ids',
        ),
    ],
)
async def test_stq_send_by_place_ids(
        stq,
        mock_personal_telegram_retrieve,
        mock_catalog_storage,
        stq_runner,
        resolved_logins,
):
    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='fake_task',
    )

    assert mock_personal_telegram_retrieve.times_called == 1
    assert mock_catalog_storage.times_called == 1

    assert stq.eats_restapp_tg_bot_send_message.times_called == 3
    arg = stq.eats_restapp_tg_bot_send_message.next_call()
    assert arg['queue'] == 'eats_restapp_tg_bot_send_message'
    assert (
        arg['kwargs']['message'] == '<b>place1 (address1)</b>\n\n'
        'first value: some value\nsecond_value : other value'
    )
    if resolved_logins:
        assert arg['kwargs']['logins'] == [
            'resolved_loginid1',
            'resolved_loginid2',
        ]
    else:
        assert arg['kwargs']['logins'] == ['loginid1', 'loginid2']
    arg = stq.eats_restapp_tg_bot_send_message.next_call()
    assert arg['queue'] == 'eats_restapp_tg_bot_send_message'
    assert (
        arg['kwargs']['message'] == '<b>place2 (address2)</b>\n\n'
        'first value: some value\nsecond_value : other value'
    )
    if resolved_logins:
        assert arg['kwargs']['logins'] == [
            'resolved_loginid2',
            'resolved_loginid3',
        ]
    else:
        assert arg['kwargs']['logins'] == ['loginid2', 'loginid3']
    arg = stq.eats_restapp_tg_bot_send_message.next_call()
    assert arg['queue'] == 'eats_restapp_tg_bot_send_message'
    assert (
        arg['kwargs']['message'] == '<b>place3 (address3)</b>\n\n'
        'first value: some value\nsecond_value : other value'
    )
    if resolved_logins:
        assert arg['kwargs']['logins'] == ['resolved_loginid1']
    else:
        assert arg['kwargs']['logins'] == ['loginid1']


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_bind_places_logins.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_TELEGRAM_SETTINGS=CONFIG_TELEGRAM_SETTINGS,
    EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS=CONFIG_SEND_EVENT_SETTINGS,
    EATS_RESTAPP_COMMUNICATIONS_EVENT_SENDER_RETRY_SETTINGS=CFG_RETRY_SETTINGS,
)
@pytest.mark.parametrize(
    'reschedule_counter, has_stq_restarted',
    [(28, True), (29, True), (30, False)],
)
async def test_stq_restart_w_different_restart_limit(
        mockserver,
        testpoint,
        stq_runner,
        reschedule_counter,
        has_stq_restarted,
):
    @mockserver.json_handler('/personal/v1/telegram_logins/bulk_retrieve')
    def _mock_response500(request):
        return mockserver.make_response(
            status=500, json={'error': 'Internal Server Error'},
        )

    @testpoint('telegram_stq_restart')
    def _telegram_stq_event_sender_restart(data):
        return data

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='fake_task', reschedule_counter=reschedule_counter,
    )

    assert _telegram_stq_event_sender_restart.has_calls == has_stq_restarted
