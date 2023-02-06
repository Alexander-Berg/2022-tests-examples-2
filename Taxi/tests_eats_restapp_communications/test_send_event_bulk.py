import pytest

CONFIG_TELEGRAM_SETTINGS = {
    'telegram_events': [{'event_type': 'daily-digest', 'template': []}],
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


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_TELEGRAM_SETTINGS=CONFIG_TELEGRAM_SETTINGS,
    EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS=CONFIG_SEND_EVENT_SETTINGS,
    EATS_RESTAPP_COMMUNICATIONS_SEND_EVENT_SUBSCRIPTION_CHECK=CFG_SUBS_CHECK,
)
async def test_send_event_bulk(
        taxi_eats_restapp_communications, stq, mockserver, pgsql,
):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/feature/enabled-for-places',
    )
    def _mock_subscriptions(request):
        req = request.json
        assert req['feature'] == 'boss_bot'
        assert sorted(req['place_ids']) == [1, 2, 3]
        resp = {
            'feature': 'boss_bot',
            'places': {
                'with_enabled_feature': [1, 3],
                'with_disabled_feature': [2],
            },
        }
        return mockserver.make_response(status=200, json=resp)

    event = 'daily-digest'
    params = {'event_type': event}
    data = {
        'recipients_with_data': [
            {'recipients': {'place_ids': [1]}, 'data': {'some': 'value-1'}},
            {'recipients': {'place_ids': [2]}, 'data': {'some': 'value-2'}},
            {'recipients': {'place_ids': [3]}, 'data': {'some': 'value-3'}},
            {'recipients': {'partner_ids': [42]}, 'data': {'other': 'value'}},
        ],
    }
    response = await taxi_eats_restapp_communications.post(
        '/internal/communications/v1/send-event-bulk',
        params=params,
        json=data,
    )
    assert response.status_code == 204

    assert _mock_subscriptions.times_called == 1
    assert stq.eats_restapp_communications_event_sender.times_called == 3
    cursor = pgsql['eats_restapp_communications'].cursor()

    arg = stq.eats_restapp_communications_event_sender.next_call()
    assert arg['queue'] == 'eats_restapp_communications_event_sender'
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients, data
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (arg['id'],),
    )
    res = cursor.fetchall()
    assert len(res) == 1
    assert res[0][0] == event
    assert res[0][1] == 'asap'
    assert res[0][2]['recipients'] == {'place_ids': [1]}
    assert res[0][3] == {'some': 'value-1'}

    arg = stq.eats_restapp_communications_event_sender.next_call()
    assert arg['queue'] == 'eats_restapp_communications_event_sender'
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients, data
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (arg['id'],),
    )
    res = cursor.fetchall()
    assert len(res) == 1
    assert res[0][0] == event
    assert res[0][1] == 'asap'
    assert res[0][2]['recipients'] == {'place_ids': [3]}
    assert res[0][3] == {'some': 'value-3'}

    arg = stq.eats_restapp_communications_event_sender.next_call()
    assert arg['queue'] == 'eats_restapp_communications_event_sender'
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients, data
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (arg['id'],),
    )
    res = cursor.fetchall()
    assert len(res) == 1
    assert res[0][0] == event
    assert res[0][1] == 'asap'
    assert res[0][2]['recipients'] == {'partner_ids': [42]}
    assert res[0][3] == {'other': 'value'}


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
    params = {'event_type': event}
    data = {
        'recipients_with_data': [
            {'recipients': {'place_ids': [1]}, 'data': {'some': 'value-1'}},
            {'recipients': {'place_ids': [2]}, 'data': {'some': 'value-2'}},
            {'recipients': {'place_ids': [3]}, 'data': {'some': 'value-3'}},
            {'recipients': {'partner_ids': [42]}, 'data': {'other': 'value'}},
        ],
    }
    response = await taxi_eats_restapp_communications.post(
        '/internal/communications/v1/send-event-bulk',
        params=params,
        json=data,
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'Incorrect event type'
    assert stq.eats_restapp_communications_event_sender.times_called == 0

    metrics = (
        await taxi_eats_restapp_communications_monitor.get_metrics(
            metrics_name,
        )
    )[metrics_name]
    errors = metrics.get('slug_error', 0)
    assert errors == errors_on_start + 1


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_TELEGRAM_SETTINGS=CONFIG_TELEGRAM_SETTINGS,
    EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS=CONFIG_SEND_EVENT_SETTINGS,
)
async def test_empty_recipients(taxi_eats_restapp_communications, stq):
    event = 'daily-digest'
    params = {'event_type': event}
    data = {
        'recipients_with_data': [
            {'recipients': {'place_ids': [1]}, 'data': {'some': 'value-1'}},
            {'recipients': {}, 'data': {'some': 'value-2'}},
            {'recipients': {'place_ids': [3]}, 'data': {'some': 'value-3'}},
            {'recipients': {'partner_ids': [42]}, 'data': {'other': 'value'}},
        ],
    }
    response = await taxi_eats_restapp_communications.post(
        '/internal/communications/v1/send-event-bulk',
        params=params,
        json=data,
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'There is no recipients'
    assert stq.eats_restapp_communications_event_sender.times_called == 0
