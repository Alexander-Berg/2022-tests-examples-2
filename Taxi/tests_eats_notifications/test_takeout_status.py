import pytest


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
    INSERT INTO eats_notifications.projects (name, key, tanker_project,
    tanker_keyset, intent)
    VALUES ('project_name_test', 'project_key_test', 'tanker_project_test',
    'tanker_keyset_test', 'intent_test')
    """,
        """
    INSERT INTO eats_notifications.templates (name, key, project_id,
    transport_type, waiting_condition, ttl)
    VALUES ('template_name_test', 'template_key_test', 1, 0, 'sent', 0)
    """,
        # This notification should be considered as
        # user data
        """
    INSERT INTO eats_notifications.notifications (token, status,
    project_id, template_id, user_id, application, user_device_id,
    notification_params, message_title, message_body, deeplink,
    api_response, request, message_id, client_type, sent_at, updated_at,
    sent_transport_type, personal_phone_id)
    VALUES ('test_token-1', 'skipped', 1, 1, 'eater_id-1',
    'test_application', 'test_user_device_id-1', '{}',
    'test_message_title', 'test_message_body', 'test_deeplink',
    'test_api_response', 'test_request', 'test_message_id',
    'client-notify', '2021-07-28T18:00:00+00:00',
    '2021-07-28T18:00:00+00:00', 'push',
    'personal_phone_id_test-1')
    """,
        # This notification should not be considered as
        # user data as having updated_at later than requested
        """
    INSERT INTO eats_notifications.notifications (token, status,
    project_id, template_id, user_id, application, user_device_id,
    notification_params, message_title, message_body, deeplink,
    api_response, request, message_id, client_type, sent_at, updated_at,
    sent_transport_type, personal_phone_id)
    VALUES ('test_token-2', 'skipped', 1, 1, 'eater_id-2',
    'test_application', 'test_user_device_id-1', '{}',
    'test_message_title', 'test_message_body', 'test_deeplink',
    'test_api_response', 'test_request', 'test_message_id',
    'client-notify', '2022-07-28T18:00:00+00:00',
    '2022-07-28T18:00:00+00:00', 'push',
    'personal_phone_id_test-2')
    """,
    ],
)
@pytest.mark.now('2021-08-28T18:00:00+00:00')
async def test_takeout_status(taxi_eats_notifications, mockserver):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eaters(request):
        assert request.json['with_soft_deleted']
        eater = {}
        if request.json['passport_uids'][0] == 'yandex_uid-1':
            eater = {
                'id': 'eater_id-1',
                'uuid': 'eater_uuid-2',
                'updated_at': '2021-07-28T18:00:00+00:00',
                'created_at': '2021-07-28T18:00:00+00:00',
            }
        elif request.json['passport_uids'][0] == 'yandex_uid-2':
            eater = {
                'id': 'eater_id-2',
                'uuid': 'eater_uuid-1',
                'updated_at': '2021-07-28T18:00:00+00:00',
                'created_at': '2021-07-28T18:00:00+00:00',
            }
        else:
            assert False
        return {
            'eaters': [eater],
            'pagination': {'limit': 0, 'has_more': False},
        }

    body = {'yandex_uids': [{'uid': 'yandex_uid-1', 'is_portal': True}]}

    response = await taxi_eats_notifications.post(
        '/takeout/v1/status', json=body,
    )

    assert response.status_code == 200
    assert response.json()['data_state'] == 'ready_to_delete'

    body = {
        'yandex_uids': [{'uid': 'yandex_uid-2', 'is_portal': True}],
        # day before mocked notification
        'date_request_at': '2022-07-27T18:00:00+00:00',
    }

    response = await taxi_eats_notifications.post(
        '/takeout/v1/status', json=body,
    )

    assert response.status_code == 200
    assert response.json()['data_state'] == 'empty'
