DROP TABLE IF EXISTS crm_hub.user_tags_test_table;
CREATE TABLE crm_hub.user_tags_test_table (
    id SERIAL PRIMARY KEY,
    unique_driver_id TEXT,
    user_id TEXT,
    phone_pd_id TEXT,
    user_phone_id TEXT,
    group_id TEXT,
    group_name TEXT,
    db_id TEXT,
    driver_uuid TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    locale TEXT,
    global_control_flg TEXT,
    experiment_id TEXT,
    application TEXT,
    was_logged BOOLEAN,
    timestamp TIMESTAMPTZ,
    actions_states JSONB,
    user_sms JSONB
);
INSERT INTO crm_hub.user_tags_test_table
(
    unique_driver_id,
    user_id,
    phone_pd_id,
    user_phone_id,
    group_id,
    group_name,
    db_id,
    driver_uuid,
    phone,
    city,
    country,
    locale,
    global_control_flg,
    experiment_id,
    application,
    actions_states,
    user_sms
)
(
    SELECT
       'driver_' || i::TEXT,
       'user_phone_' || i::TEXT,
       'phone_pd_id_' || i::TEXT,
       'user_phone_id_' || i::TEXT,
       'driver_' || i::TEXT,
       '',
       'db_id_' || i::TEXT,
       'driver_uuid_' || i::TEXT,
       '',
       '',
       '',
       '',
       '',
       '',
       'android',
       CASE WHEN i % 2 = 1 THEN ('{"policy": {"status": "SUCCESS", "source_task_id": 123}}')::jsonb
           ELSE ('{"policy": {"status": "SKIP", "reason": "Filtered", "source_task_id": 123}}')::jsonb
       END,
       ('{
           "channel_name": "user_sms",
           "intent": "",
           "sender": "",
           "text": "",
           "action": "",
           "content": "",
           "deeplink": "",
           "code": 100,
           "ttl": 30,
           "collapse_key": "",
           "feed_id": "",
           "send_at": "2020-09-11T10:00:00+03:00",
           "type": "",
           "url": "",
           "title": "",
           "teaser": ""
       }')::jsonb
    FROM generate_series(1, 200) as i
);

INSERT INTO crm_hub.batch_sending (
    id,
    campaign_id,
    group_id,
    filter,
    yt_table,
    yt_test_table,
    pg_table,
    state,
    entity_type,
    group_type,
    processing_chunk_size,
    use_policy,
    extra_data,
    extra_data_path,
    created_at,
    subfilters,
    sending_stats,
    start_id,
    replication_state,
    verify,
    control,
    group_name,
    actions
) VALUES
(
    '00000000000000000000000000000001',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'user_tags_test_table',
    '',
    'user',
    'testing',
    30,
    TRUE,
    '{}'::jsonb,
    '//home/taxi-crm/cmp_extra_data',
    NOW() AT TIME ZONE 'UTC',
    '{}'::jsonb,
    '{}'::jsonb,
    0,
    'NEW',
    FALSE,
    FALSE,
    'group_name',
    ('[
       {
           "action_name": "channel",
           "channel_info": {"channel_name": "user_sms",
                         "intent": "none",
                         "sender": "sender",
                         "content": "my_content"}
       },
       {
           "action_name": "policy",
           "channel": "sms"
       },
       {
           "action_name": "user_tags",
           "tags":
           [
                  {
                     "service": "taxi",
                     "tag": "tag1",
                     "validity_time": {
                         "active_days": 5,
                         "end_time": "12:00"
                     }
                  }
           ]
       }
    ]')::jsonb
),
(
    '00000000000000000000000000000002',
    123,
    123,
    '',
    '//home/taxi-crm/drivers/test/experiments/friday_the_13th_cm',
    '',
    'user_tags_test_table',
    '',
    'user',
    'testing',
    30,
    TRUE,
    '{}'::jsonb,
    '//home/taxi-crm/cmp_extra_data',
    NOW() AT TIME ZONE 'UTC',
    '{}'::jsonb,
    '{}'::jsonb,
    0,
    'NEW',
    FALSE,
    FALSE,
    'group_name',
    ('[
       {
           "action_name": "channel",
           "channel_info": {"channel_name": "user_sms",
                         "intent": "none",
                         "sender": "sender",
                         "content": "my_content"}
       },
       {
           "action_name": "policy",
           "channel": "sms"
       },
       {
           "action_name": "user_tags",
           "tags":
           [
                  {
                     "service": "taxi",
                     "tag": "tag1",
                     "validity_time": {
                         "active_days": 5,
                         "end_time": "12:00"
                     }
                  },
                  {
                     "service": "eats",
                     "tag": "tag2",
                     "finish_at": "2023-01-31T04:00:00+03:00"
                  },
                  {
                     "service": "grocery",
                     "tag": "tag3",
                     "finish_at": "2023-01-31T12:34:56+03:00"
                  }
           ]
       }
    ]')::jsonb
);
