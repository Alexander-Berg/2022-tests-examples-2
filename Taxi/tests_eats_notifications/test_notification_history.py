import pytest

import json


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
        """
        INSERT INTO eats_notifications.notifications (token, status,
        project_id, template_id, user_id, application, user_device_id,
        notification_params, message_title, message_body, deeplink,
        api_response, request, message_id, client_type, sent_at,
        sent_transport_type, personal_phone_id)
        VALUES ('test_token', 'skipped', 1, 1, 'test_user_id',
        'test_application', 'test_user_device_id', '{}',
        'test_message_title', 'test_message_body', 'test_deeplink',
        'test_api_response', 'test_request', 'test_message_id',
        'client-notify', '2021-07-28T18:00:00+00:00', 'push',
        'personal_phone_id_test')
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id, model, brand)
        VALUES ('test_user_id', 'x_taxi_session_value', TRUE,
        'test_user_device_id', 'model_test', 'brand_test'),
        ('test_user_id_2', 'x_taxi_session_value_1', FALSE,
        'test_user_device_id', 'model_test', 'brand_test')
        """,
    ],
)
@pytest.mark.parametrize(
    'request_json', [pytest.param({'tokens': ['test_token']})],
)
async def test_200(taxi_eats_notifications, taxi_config, request_json):
    # get history
    response = await taxi_eats_notifications.post(
        '/v1/notification/get-history', json=request_json,
    )
    assert response.status_code == 200
    assert len(response.json()['notifications']) == 1
    assert (
        response.json()['notifications'][0]['application']
        == 'test_application'
    )
    assert (
        response.json()['notifications'][0]['client_type'] == 'client-notify'
    )
    assert response.json()['notifications'][0]['deeplink'] == 'test_deeplink'
    assert (
        response.json()['notifications'][0]['message_body']
        == 'test_message_body'
    )
    assert (
        response.json()['notifications'][0]['message_id'] == 'test_message_id'
    )
    assert (
        response.json()['notifications'][0]['message_title']
        == 'test_message_title'
    )
    assert (
        response.json()['notifications'][0]['sent_at']
        == '2021-07-28T18:00:00+00:00'
    )
    assert response.json()['notifications'][0]['status'] == 'skipped'
    assert response.json()['notifications'][0]['token'] == 'test_token'
    assert response.json()['notifications'][0]['user_id'] == 'test_user_id'
    assert (
        response.json()['notifications'][0]['device']
        == 'brand_test model_test'
    )
    assert (
        response.json()['notifications'][0]['personal_phone_id']
        == 'personal_phone_id_test'
    )
    assert response.json()['notifications'][0]['transport_type'] == 'push'


@pytest.mark.parametrize(
    'body_tags, expected_result',
    [
        pytest.param(
            [
                {'key': 'city', 'value': 'moscow'},
                {'key': 'order_id', 'value': 'order_id-123'},
            ],
            {
                'notification_token-1': {
                    'expected_tags': [
                        {'key': 'group', 'value': 'group-2'},
                        {'key': 'order_id', 'value': 'order_id-123'},
                        {'key': 'city', 'value': 'moscow'},
                    ],
                },
                'notification_token-3': {
                    'expected_tags': [
                        {'key': 'group', 'value': 'group-1'},
                        {'key': 'order_id', 'value': 'order_id-123'},
                        {'key': 'city', 'value': 'moscow'},
                    ],
                },
            },
            marks=[
                pytest.mark.pgsql(
                    'eats_notifications',
                    queries=[
                        """
                        INSERT INTO eats_notifications.notifications_tags
                        (key, value, notification_token, updated_at)
                        VALUES ('order_id', 'order_id-123', 'notification_token-1', '2021-07-28T18:00:00+00:00'),
                               ('group', 'group-2', 'notification_token-1', '2021-07-28T18:00:00+00:00'),
                               ('order_id', 'order_id-321', 'notification_token-2', '2021-07-28T18:00:00+00:00'),
                               ('order_id', 'order_id-123', 'notification_token-3', '2021-07-28T18:00:00+00:00'),
                               ('city', 'moscow', 'notification_token-3', '2021-07-28T18:00:00+00:00'),
                               ('city', 'moscow', 'notification_token-1', '2021-07-28T18:00:00+00:00'),
                               ('city', 'moscow', 'notification_token-4', '2021-07-28T18:00:00+00:00'),
                               ('group', 'group-1', 'notification_token-3', '2021-07-28T18:00:00+00:00');
                        """,
                        """
                            INSERT INTO eats_notifications.notifications 
                            (token, status, notification_params, message_title, message_body, sent_at)
                            VALUES   ('notification_token-1', 'sent', '{}', '', '', '2021-07-28T18:00:00+00:00'),
                                     ('notification_token-2', 'sent', '{}', '', '', '2021-07-28T18:00:00+00:00'),
                                     ('notification_token-3', 'sent', '{}', '', '', '2021-07-28T18:00:00+00:00'),
                                     ('notification_token-4', 'sent', '{}', '', '', '2021-07-28T18:00:00+00:00')
                        """,
                    ],
                ),
            ],
            id='Filtering',
        ),
        pytest.param(
            [
                {'key': 'city', 'value': 'moscow'},
                {'key': 'order_id', 'value': 'order_id-123'},
            ],
            {},
            id='No tokens found',
        ),
    ],
)
async def test_find_history_by_tags(
        taxi_eats_notifications, pgsql, expected_result, body_tags,
):
    body = {'tags': body_tags}

    expected_tokens = expected_result.keys()

    response = await taxi_eats_notifications.post(
        '/v1/notification/get-history-by-tags', json=body,
    )
    assert response.status_code == 200

    notifications = response.json()['notifications']

    tokens = [item['notification']['token'] for item in notifications]
    assert sorted(tokens) == sorted(expected_tokens)

    for item in notifications:
        token = item['notification']['token']
        expected_tags = expected_result[token]['expected_tags']
        assert sorted(item['tags'], key=lambda x: x['value']) == sorted(
            expected_tags, key=lambda x: x['value'],
        )
