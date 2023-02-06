import datetime
import json

import pytest

NOTIFICATION_PARAMS_SAMPLE = json.dumps(
    {
        'key': 'order.taken',
        'route': 'eda',
        'token': '23d8537095434a7f842bba4603c903d6',
        'intent': 'eats_on_order',
        'locale': 'ru',
        'sender': 'eda',
    },
)


@pytest.mark.config(
    EATS_NOTIFICATIONS_HISTORY_TAGS={
        'regular': ['city'],
        'sensitive': ['order_id'],
    },
)
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
        # This notification should be deleted
        # by eater_id from eats-eaters
        f"""
        INSERT INTO eats_notifications.notifications (token, status,
        project_id, template_id, user_id, application, user_device_id,
        notification_params, message_title, message_body, deeplink,
        api_response, request, message_id, client_type, sent_at, updated_at,
        sent_transport_type, personal_phone_id)
        VALUES ('test_token-1', 'skipped', 1, 1, 'eater_id-1',
        'test_application', 'test_user_device_id-1',
        '{NOTIFICATION_PARAMS_SAMPLE}'::jsonb,
        'test_message_title', 'test_message_body', 'test_deeplink',
        'test_api_response', 'test_request', 'test_message_id',
        'client-notify', '2021-07-28T18:00:00+00:00',
        '2021-07-28T18:00:00+00:00', 'push',
        'personal_phone_id_test-1')
        """,
        # This notification should be deleted by
        # eater_uuid from eats-eaters
        f"""
        INSERT INTO eats_notifications.notifications (token, status,
        project_id, template_id, user_id, application, user_device_id,
        notification_params, message_title, message_body, deeplink,
        api_response, request, message_id, client_type, sent_at, updated_at,
        sent_transport_type, personal_phone_id)
        VALUES ('test_token-2', 'skipped', 1, 1, 'eater_uuid-1',
        'test_application', 'test_user_device_id-2',
        '{NOTIFICATION_PARAMS_SAMPLE}'::jsonb,
        'test_message_title', 'test_message_body', 'test_deeplink',
        'test_api_response', 'test_request', 'test_message_id',
        'client-notify', '2021-07-28T18:00:00+00:00',
        '2021-07-28T18:00:00+00:00', 'push',
        'personal_phone_id_test-2')
        """,
        # This notification should be deleted by
        # taxi_user_id from user_ids stq kwarg
        f"""
        INSERT INTO eats_notifications.notifications (token, status,
        project_id, template_id, user_id, application, user_device_id,
        notification_params, message_title, message_body, deeplink,
        api_response, request, message_id, client_type, sent_at, updated_at,
        sent_transport_type, personal_phone_id)
        VALUES ('test_token-3', 'skipped', 1, 1, 'taxi_user_id-1',
        'test_application', 'test_user_device_id-3',
        '{NOTIFICATION_PARAMS_SAMPLE}'::jsonb,
        'test_message_title', 'test_message_body', 'test_deeplink',
        'test_api_response', 'test_request', 'test_message_id',
        'client-notify', '2021-07-28T18:00:00+00:00',
        '2021-07-28T18:00:00+00:00', 'push',
        'personal_phone_id_test-3')
        """,
        # This notification should not be deleted as
        # being updated_at after delete_before stq kwarg
        f"""
        INSERT INTO eats_notifications.notifications (token, status,
        project_id, template_id, user_id, application, user_device_id,
        notification_params, message_title, message_body, deeplink,
        api_response, request, message_id, client_type, sent_at, updated_at,
        sent_transport_type, personal_phone_id)
        VALUES ('test_token-4', 'skipped', 1, 1, 'taxi_user_id-1',
        'test_application', 'test_user_device_id-3',
        '{NOTIFICATION_PARAMS_SAMPLE}'::jsonb,
        'test_message_title', 'test_message_body', 'test_deeplink',
        'test_api_response', 'test_request', 'test_message_id',
        'client-notify', '2022-08-01T18:00:00+00:00',
        '2022-08-01T18:00:00+00:00', 'push',
        'personal_phone_id_test-3')
        """,
        # This tag should be deleted as containing sensitive data
        """
        INSERT INTO eats_notifications.notifications_tags
        (key, value, notification_token, updated_at)
        VALUES ('order_id', 'order_id-1', 'test_token-1',
         '2021-07-28T18:00:00+00:00')
        """,
        # This tag should not be deleted
        """
        INSERT INTO eats_notifications.notifications_tags
        (key, value, notification_token, updated_at)
        VALUES ('city', 'city-1', 'test_token-2',
         '2021-07-28T18:00:00+00:00')
        """,
    ],
)
@pytest.mark.now('2022-05-28T18:00:00+00:00')
async def test_delete(stq_runner, pgsql, mockserver, taxi_config):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uids')
    def _mock_eaters(request):
        assert request.json['with_soft_deleted']
        assert request.json['passport_uids'] == ['yandex_uid-1']
        return {
            'eaters': [
                {
                    'id': 'eater_id-1',
                    'uuid': 'eater_uuid-2',
                    'updated_at': '2021-07-28T18:00:00+00:00',
                    'created_at': '2021-07-28T18:00:00+00:00',
                },
                {
                    'id': 'eater_id-2',
                    'uuid': 'eater_uuid-1',
                    'updated_at': '2021-07-28T18:00:00+00:00',
                    'created_at': '2021-07-28T18:00:00+00:00',
                },
            ],
            'pagination': {'limit': 0, 'has_more': False},
        }

    date_delete_before = '2022-07-28T18:00:00+00:00'
    stq_args = {
        'date_delete_before': date_delete_before,
        'request_id': 'request_id-1',
        'yandex_uids': [{'uid': 'yandex_uid-1', 'is_portal': False}],
        'user_ids': ['taxi_user_id-1'],
    }
    date_delete_before = datetime.datetime.fromisoformat(date_delete_before)

    await stq_runner.eats_notifications_takeout.call(
        task_id='task_id', expect_fail=False, kwargs=stq_args,
    )

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        """
        SELECT user_id, user_device_id,
               notification_params, message_title,
               message_body, deeplink,
               request, personal_phone_id,
               sent_at
        FROM eats_notifications.notifications
        """,
    )

    notifications = list(cursor)
    for notification in notifications:
        # use sent_at because we change updated_at while takeout.
        sent_at = notification[8]
        for item in notification[:-2]:
            if sent_at < date_delete_before:
                assert not item
            else:
                assert item

    cursor.execute(
        """
        SELECT key
        FROM eats_notifications.notifications_tags
        """,
    )

    config_values = taxi_config.get_values()
    sensitive_keys = config_values['EATS_NOTIFICATIONS_HISTORY_TAGS'][
        'sensitive'
    ]

    tags = list(cursor)
    for tag_row in tags:
        key = tag_row[0]
        assert key not in sensitive_keys
