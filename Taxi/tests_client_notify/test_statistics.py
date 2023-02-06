async def test_limiter_statistics(
        taxi_client_notify, taxi_client_notify_monitor,
):
    response = await taxi_client_notify.post(
        'v1/push',
        json={
            'service': 'eda_courier',
            'client_id': 'courier1',
            'intent': 'order_new',
            'data': {
                'payload': {'content': {'title': 'My Push', 'value': 10}},
                'repack': {
                    'fcm': {'repack_payload': ['content']},
                    'apns': {'repack_payload': ['content']},
                },
            },
        },
    )
    assert response.status_code == 200

    statistics = await taxi_client_notify_monitor.get_metric('client-notify')
    assert statistics == {
        'services': {
            'eda_courier': {
                'notifications': {'sent': 1, 'error': 0, 'queued': 0},
                'intents': {
                    'order_new': {
                        'notifications': {'sent': 1, 'error': 0, 'queued': 0},
                    },
                    '$meta': {
                        'solomon_children_labels': 'client_notify_intent',
                    },
                },
                'bulk_notifications': {'success': 0, 'error': 0},
                'subscription_events': {
                    '$meta': {
                        'solomon_children_labels': (
                            'client_notify_subscription_evnt'
                        ),
                    },
                },
            },
            '$meta': {'solomon_children_labels': 'client_notify_service'},
        },
        'ack_statuses': {
            '$meta': {'solomon_children_labels': 'client_notify_ack_status'},
        },
    }
