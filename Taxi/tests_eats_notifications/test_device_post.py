import pytest


@pytest.mark.parametrize(
    'headers, body, eaters_response, applications_config, stq_times_called',
    [
        pytest.param(
            {
                'x-os-version': 'test',
                'x-app-version': 'test',
                'x-appmetrica-uuid': 'test',
                'x-code-version': 'test',
                'x-device-brand': 'HTC',
                'x-device-model': 'test',
                'x-device-id': 'device_id_value1',
                'x-platform': 'test',
                'X-Eats-User': 'user_id=eater_id',
                'X-YaTaxi-Session': 'x_taxi_session_value',
                'X-AppMetrica-DeviceId': 'app_metrica_device_id_value1',
                'X-Request-Language': 'ru',
            },
            {
                'push_token_firebase': 'test',
                'push_notifications_enabled': True,
            },
            {
                'eater': {
                    'id': 'eater_id',
                    'uuid': 'eater_uuid',
                    'created_at': '2018-01-01T10:59:59+03:00',
                    'updated_at': '2018-01-01T10:59:59+03:00',
                },
            },
            {
                'eda_native': {
                    'type': 'xiva',
                    'xiva_settings': {
                        'ios': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                        'android': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                    },
                    'settings': {'service': 'eda-client', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            1,
            id='fcm',
        ),
        pytest.param(
            {
                'x-os-version': 'test',
                'x-app-version': 'test',
                'x-appmetrica-uuid': 'test',
                'x-code-version': 'test',
                'x-device-brand': 'Apple',
                'x-device-model': 'test',
                'x-device-id': 'device_id_value2',
                'x-platform': 'test',
                'X-YaTaxi-Session': 'x_taxi_session_value',
            },
            {'push_token_origin': 'test', 'push_notifications_enabled': True},
            {
                'eater': {
                    'id': 'eater_id',
                    'uuid': 'eater_uuid',
                    'created_at': '2018-01-01T10:59:59+03:00',
                    'updated_at': '2018-01-01T10:59:59+03:00',
                },
            },
            {
                'eda_native': {
                    'type': 'xiva',
                    'xiva_settings': {
                        'ios': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                        'android': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                    },
                    'settings': {'service': 'eda-client', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            0,
            id='ios',
        ),
    ],
)
async def test_v1_device_post_204(
        taxi_eats_notifications,
        taxi_config,
        mockserver,
        pgsql,
        headers,
        body,
        eaters_response,
        applications_config,
        stq_times_called,
        stq,
):
    response = await taxi_eats_notifications.post(
        '/v1/device', headers=headers, json=body,
    )
    assert response.status_code == 204

    assert stq.eats_notifications_save_device.times_called == stq_times_called
