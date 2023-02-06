import pytest


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.user_devices
        (id, user_id, auth_token, active, os, os_version, app_version, model,
        device_id, brand, code_version, push_enabled, appmetrica_uuid)
        VALUES (1, 'test_user_id-1', 'x_taxi_session_value', TRUE, 'os_test',
        'os_version_test', 'app_version_test', 'model_test',
        'user-device-1', 'brand_test', 'code_version_test', TRUE,
        'appmetrica_uuid_test')
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (id, user_id, auth_token, active, os, os_version, app_version, model,
        device_id, brand, code_version, push_enabled, appmetrica_uuid)
        VALUES (2, 'test_user_id-1', 'x_taxi_session_value', FALSE, 'os_test',
        'os_version_test', 'app_version_test', 'model_test',
        'user-device-2', 'brand_test', 'code_version_test',
        FALSE, 'appmetrica_uuid_test')
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (id, user_id, auth_token, active, os, os_version, app_version, model,
        device_id, brand, code_version, push_enabled, appmetrica_uuid)
        VALUES (3, 'test_user_id-2', 'x_taxi_session_value', FALSE, 'os_test',
        'os_version_test', 'app_version_test','model_test',
        'user-device-3', 'brand_test', 'code_version_test',
        FALSE, 'appmetrica_uuid_test')
        """,
    ],
)
@pytest.mark.parametrize(
    'request_json, expected_response',
    [
        pytest.param(
            {
                'ids': ['test_user_id-1', 'test_user_id-2'],
                'ids_type': 'eater_id',
            },
            {
                'test_user_id-1': ['user-device-1', 'user-device-2'],
                'test_user_id-2': ['user-device-3'],
            },
            id='Simple case',
        ),
        pytest.param(
            {'ids': ['test_user_id-4'], 'ids_type': 'eater_id'},
            {},
            id='No such eater_ids found',
        ),
        pytest.param(
            {'ids': ['test_user_id-1'], 'ids_type': 'eater_id'},
            {'test_user_id-1': ['user-device-1', 'user-device-2']},
            id='Part of table',
        ),
        pytest.param(
            {
                'ids': ['pers_phone-1', 'pers_phone-2'],
                'ids_type': 'personal_phone_id',
            },
            {
                'pers_phone-1': ['user-device-1', 'user-device-2'],
                'pers_phone-2': ['user-device-3'],
            },
            id='Simple case personal_phone_id',
        ),
    ],
)
async def test_get_device(
        mockserver, taxi_eats_notifications, request_json, expected_response,
):
    @mockserver.json_handler(
        '/eats-eaters/v1/eaters/find-by-personal-phone-id',
    )
    def _mock_eaters(request):
        phone_to_eater_id = {
            'pers_phone-1': 'test_user_id-1',
            'pers_phone-2': 'test_user_id-2',
        }
        return {
            'eaters': [
                {
                    'id': phone_to_eater_id[request.json['personal_phone_id']],
                    'uuid': 'test_uuid',
                    'created_at': '2050-02-07T19:45:00.922+0000',
                    'updated_at': '2050-02-07T19:45:00.922+0000',
                    'personal_phone_id': request.json['personal_phone_id'],
                },
            ],
            'pagination': {'limit': 1, 'has_more': False},
        }

    response = await taxi_eats_notifications.post(
        '/v1/device-list', json=request_json,
    )
    assert response.status_code == 200
    assert response.json() == expected_response
