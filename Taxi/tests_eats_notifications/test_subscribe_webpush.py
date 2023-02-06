async def test_simple(taxi_eats_notifications, stq):
    headers = {
        'x-device-id': 'device_id_value1',
        'x-platform': 'test',
        'X-Eats-User': 'user_id=eater_id',
        'X-YaTaxi-Session': 'x_taxi_session_value',
        'X-AppMetrica-DeviceId': 'app_metrica_device_id_value1',
    }
    body = {
        'subscription': {
            'endpoint': (
                'https://android.googleapis.com/gcm/send/a-subscription-id'
            ),
            'keys': {'auth': 'AEl357fG', 'p256dh': 'Fg5t82rC'},
        },
    }
    response = await taxi_eats_notifications.post(
        '/v1/subscribe/webpush', json=body, headers=headers,
    )

    assert response.status_code == 204

    assert stq.eats_notifications_save_device_web.times_called == 1
