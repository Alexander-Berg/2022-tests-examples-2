NOTIFICATIONS = [
    {
        'id': 'notification_id_01',
        'firebase_token': 'firebase_token_01',
        'title': 'some_title',
        'body': 'some_body',
    },
    {
        'id': 'notification_id_02',
        'firebase_token': 'firebase_token_02',
        'title': 'some_title',
        'body': 'some_body',
    },
]


async def test_send_notifications(
        web_app, web_app_client, validate_web_sent_notifications,
):
    response = await web_app_client.post(
        '/internal/v1/send-notifications',
        json={'notifications': NOTIFICATIONS},
    )
    validate_web_sent_notifications(expected_notifications=NOTIFICATIONS)
    assert response.status == 200
    response_json = await response.json()
    expected_response_json = {
        'message_ids': [
            'message_id/notification_id_01',
            'message_id/notification_id_02',
        ],
    }
    assert response_json == expected_response_json
