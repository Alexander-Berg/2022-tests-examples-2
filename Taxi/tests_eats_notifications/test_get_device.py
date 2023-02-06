import pytest


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.user_devices
        (id, user_id, auth_token, active, os, os_version, app_version, model,
        device_id, brand, code_version, push_enabled, appmetrica_uuid)
        VALUES (1, 'test_user_id', 'x_taxi_session_value', TRUE, 'os_test',
        'os_version_test', 'app_version_test', 'model_test',
        'test_active_user_device_id', 'brand_test', 'code_version_test', TRUE,
        'appmetrica_uuid_test')
        """,
        """
        INSERT INTO eats_notifications.user_device_tokens
        (user_device_id, type, token, is_registered)
        VALUES(1, 'apns', 'token_ios', true)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (id, user_id, auth_token, active, os, os_version, app_version, model,
        device_id, brand, code_version, push_enabled, appmetrica_uuid)
        VALUES (2, 'test_user_id', 'x_taxi_session_value', FALSE, 'os_test',
        'os_version_test', 'app_version_test', 'model_test',
        'test_inactive_user_device_id', 'brand_test', 'code_version_test',
        FALSE, 'appmetrica_uuid_test')
        """,
        """
        INSERT INTO eats_notifications.user_device_tokens
        (user_device_id, type, token, is_registered)
        VALUES(2, 'fcm', 'token_firebase', true)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (id, user_id, auth_token, active, os, os_version, app_version, model,
        device_id, brand, code_version, push_enabled, appmetrica_uuid)
        VALUES (3, 'test_user_id', 'x_taxi_session_value', FALSE, 'os_test',
        'os_version_test', 'app_version_test','model_test',
        'test_inactive_user_device_id_2', 'brand_test', 'code_version_test',
        FALSE, 'appmetrica_uuid_test')
        """,
        """
        INSERT INTO eats_notifications.user_device_tokens
        (user_device_id, type, token, is_registered)
        VALUES(3, 'hms', 'token_hms', true)
        """,
    ],
)
@pytest.mark.parametrize(
    'request_json, expected_code, expected_response',
    [
        pytest.param(
            {'eater_id': 'test_user_id'},
            200,
            {
                'device_id': 'test_active_user_device_id',
                'token_type': 'apns',
                'token': 'token_ios',
                'os': 'os_test',
                'os_version': 'os_version_test',
                'app_version': 'app_version_test',
                'code_version': 'code_version_test',
                'device_brand': 'brand_test',
                'device_model': 'model_test',
                'appmetrica_uuid': 'appmetrica_uuid_test',
                'push_enabled': True,
                'active': True,
            },
            id='only_eater_id',
        ),
        pytest.param(
            {
                'eater_id': 'test_user_id',
                'device_id': 'test_inactive_user_device_id',
            },
            200,
            {
                'device_id': 'test_inactive_user_device_id',
                'token_type': 'fcm',
                'token': 'token_firebase',
                'os': 'os_test',
                'os_version': 'os_version_test',
                'app_version': 'app_version_test',
                'code_version': 'code_version_test',
                'device_brand': 'brand_test',
                'device_model': 'model_test',
                'appmetrica_uuid': 'appmetrica_uuid_test',
                'push_enabled': False,
                'active': False,
            },
            id='fcm_with_device_id',
        ),
        pytest.param(
            {
                'eater_id': 'test_user_id',
                'device_id': 'test_inactive_user_device_id_2',
            },
            200,
            {
                'device_id': 'test_inactive_user_device_id_2',
                'token_type': 'hms',
                'token': 'token_hms',
                'os': 'os_test',
                'os_version': 'os_version_test',
                'app_version': 'app_version_test',
                'code_version': 'code_version_test',
                'device_brand': 'brand_test',
                'device_model': 'model_test',
                'appmetrica_uuid': 'appmetrica_uuid_test',
                'push_enabled': False,
                'active': False,
            },
            id='hms_with_device_id',
        ),
        pytest.param(
            {'eater_id': 'wrong_eater_id'},
            400,
            {
                'code': 'INVALID_OPERATION',
                'message': (
                    'There is no active device for eater with id: '
                    'wrong_eater_id'
                ),
            },
            id='unknown_eater_id',
        ),
        pytest.param(
            {'eater_id': 'test_user_id', 'device_id': 'wrong_device_id'},
            400,
            {
                'code': 'INVALID_OPERATION',
                'message': (
                    'Unknown device_id: wrong_device_id for eater with '
                    'eater_id: test_user_id'
                ),
            },
            id='unknown_device_id',
        ),
    ],
)
async def test_get_device(
        taxi_eats_notifications,
        request_json,
        expected_code,
        expected_response,
):
    # get device
    response = await taxi_eats_notifications.post(
        '/v1/get-device', json=request_json,
    )
    assert response.status_code == expected_code
    assert response.json() == expected_response
